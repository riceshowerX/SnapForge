// =============================================
// 图像处理核心库 (基于 Sharp)
// =============================================
// 安全基线：
// - 所有 sharp 入口显式 limitInputPixels + failOn:'error'（S-04 / P-05）
// - 明确拒绝 SVG 等矢量输入（S-04）
// - 远程水印图片 URL 完整 SSRF 防护：协议白名单 + DNS 解析后私有网段拦截
//   + 5s 超时 + redirect:'manual' 手动跟随（每跳重新校验）（S-01）
// 功能修复：
// - F-02 flip/flop 真实生效
// - F-05 preserveMetadata → withMetadata()
// - F-06 tile 平铺水印（SVG pattern / 循环 composite，支持间距与旋转）
// - F-11 crop 边界 clamp 兜底
// - F-12 targetSize 压缩（二分法调整 quality，JPEG/WebP 有效）

import sharp from 'sharp';
import { lookup } from 'node:dns/promises';
import {
  ProcessConfig,
  ResizeMode,
  FilterType,
  WatermarkPosition,
  WatermarkConfig,
  CompressionConfig,
  ConvertConfig,
} from '@/types';
import { detectImageMime } from './file-validation';

// =============================================
// 常量
// =============================================

/** 解码像素上限（约 64MP，阻止解压炸弹） */
const MAX_INPUT_PIXELS = 64_000_000;

/** 远程水印 fetch 超时（毫秒） */
const WATERMARK_FETCH_TIMEOUT = 5000;

/** 手动跟随重定向的最大跳数 */
const MAX_REDIRECT_HOPS = 2;

// 私有/保留网段判定用的首字节规则
function isPrivateIpv4(ip: string): boolean {
  const parts = ip.split('.').map(Number);
  if (
    parts.length !== 4 ||
    parts.some((p) => !Number.isInteger(p) || p < 0 || p > 255)
  ) {
    return true; // 非法 IP 一律视为不安全
  }
  const [a, b] = parts;
  // 10.0.0.0/8
  if (a === 10) return true;
  // 172.16.0.0/12
  if (a === 172 && b >= 16 && b <= 31) return true;
  // 192.168.0.0/16
  if (a === 192 && b === 168) return true;
  // 127.0.0.0/8（环回）
  if (a === 127) return true;
  // 169.254.0.0/16（链路本地）
  if (a === 169 && b === 254) return true;
  // 0.0.0.0/8
  if (a === 0) return true;
  // 100.64.0.0/10（CGNAT）
  if (a === 100 && b >= 64 && b <= 127) return true;
  return false;
}

function isPrivateIp(ip: string): boolean {
  const lower = ip.toLowerCase();

  // IPv4-mapped IPv6：::ffff:x.x.x.x 按内嵌 IPv4 校验
  const v4Mapped = lower.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/);
  if (v4Mapped) return isPrivateIpv4(v4Mapped[1]);

  // IPv6
  if (lower.includes(':')) {
    // ::1 环回
    if (lower === '::1') return true;
    // fc00::/7 唯一本地地址
    if (lower.startsWith('fc') || lower.startsWith('fd')) return true;
    // fe80::/10 链路本地
    if (
      lower.startsWith('fe8') ||
      lower.startsWith('fe9') ||
      lower.startsWith('fea') ||
      lower.startsWith('feb')
    ) {
      return true;
    }
    // ::/128（未指定）与 ::ffff/96 已在上方处理
    if (lower === '::' || lower.startsWith('::')) return true;
    return false;
  }

  return isPrivateIpv4(lower);
}

/** DNS 解析 hostname，任一解析结果为私有 IP 即拦截（防 DNS rebinding） */
async function assertPublicHost(hostname: string): Promise<void> {
  const addresses = await lookup(hostname, { all: true, verbatim: true });
  if (addresses.length === 0) {
    throw new WatermarkFetchError('DNS_LOOKUP_EMPTY');
  }
  for (const addr of addresses) {
    if (isPrivateIp(addr.address)) {
      throw new WatermarkFetchError('PRIVATE_IP_BLOCKED');
    }
  }
}

/** 水印远程图片获取错误（携带机器可读 code） */
export class WatermarkFetchError extends Error {
  code: string;
  constructor(code: string, message?: string) {
    super(message || code);
    this.name = 'WatermarkFetchError';
    this.code = code;
  }
}

/**
 * 安全获取远程水印图片（S-01 方案 B）。
 * - 仅允许 http/https
 * - hostname DNS 解析为 IP 后拦截所有私有/保留网段
 * - fetch 加 5s 超时与 redirect:'manual'，手动跟随最多 2 跳且每跳重新校验
 * - 校验失败抛 WatermarkFetchError，绝不发起请求（对不可信目标）
 */
async function fetchWatermarkImage(imageUrl: string): Promise<Buffer> {
  let currentUrl: URL;
  try {
    currentUrl = new URL(imageUrl);
  } catch {
    throw new WatermarkFetchError('INVALID_URL');
  }

  if (currentUrl.protocol !== 'http:' && currentUrl.protocol !== 'https:') {
    throw new WatermarkFetchError('INVALID_URL_PROTOCOL');
  }

  await assertPublicHost(currentUrl.hostname);

  for (let hop = 0; hop <= MAX_REDIRECT_HOPS; hop++) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), WATERMARK_FETCH_TIMEOUT);

    try {
      const response = await fetch(currentUrl, {
        signal: controller.signal,
        redirect: 'manual',
        headers: {
          'user-agent': 'SnapForge/1.0',
          accept: 'image/*',
        },
      });

      // 重定向：手动跟随，每跳重新做协议 + DNS 校验
      if (response.status >= 300 && response.status < 400) {
        const location = response.headers.get('location');
        if (!location) {
          throw new WatermarkFetchError('INVALID_REDIRECT');
        }
        currentUrl = new URL(location, currentUrl);
        if (
          currentUrl.protocol !== 'http:' &&
          currentUrl.protocol !== 'https:'
        ) {
          throw new WatermarkFetchError('INVALID_URL_PROTOCOL');
        }
        await assertPublicHost(currentUrl.hostname);
        continue;
      }

      if (!response.ok) {
        throw new WatermarkFetchError('FETCH_FAILED');
      }

      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);

      // 校验返回内容确实是受支持的位图
      const mime = detectImageMime(buffer);
      if (!mime) {
        throw new WatermarkFetchError('INVALID_IMAGE_TYPE');
      }

      return buffer;
    } catch (error) {
      if (error instanceof WatermarkFetchError) throw error;
      if (error instanceof Error && error.name === 'AbortError') {
        throw new WatermarkFetchError('FETCH_TIMEOUT');
      }
      throw new WatermarkFetchError('FETCH_FAILED');
    } finally {
      clearTimeout(timeout);
    }
  }

  throw new WatermarkFetchError('TOO_MANY_REDIRECTS');
}

/** 构造带安全选项的 sharp 实例 */
function safeSharp(input: Buffer | string): sharp.Sharp {
  return sharp(input, {
    limitInputPixels: MAX_INPUT_PIXELS,
    failOn: 'error',
  });
}

// =============================================
// 格式映射
// =============================================

export const FORMAT_MAP: Record<string, string> = {
  jpg: 'jpeg',
  jpeg: 'jpeg',
  png: 'png',
  webp: 'webp',
  gif: 'gif',
  bmp: 'bmp',
  tiff: 'tiff',
  avif: 'avif',
};

// =============================================
// 主处理函数
// =============================================

export async function processImage(
  inputBuffer: Buffer,
  config: ProcessConfig,
  originalName: string,
  counter: number = 1
): Promise<{ buffer: Buffer; filename: string; metadata: ImageMetadata }> {
  // S-04：显式像素上限 + failOn:'error'
  const image = safeSharp(inputBuffer);
  const metadata = await image.metadata();

  // S-04：明确拒绝 SVG/PDF 等矢量输入
  if (metadata.format === 'svg' || metadata.format === 'pdf') {
    throw new Error(
      `Input format "${metadata.format}" is not allowed. Only raster images are supported.`
    );
  }

  const imgWidth = metadata.width || 0;
  const imgHeight = metadata.height || 0;

  // 1. 裁剪（F-11：边界 clamp 兜底，避免负宽高抛 500）
  if (config.crop.enabled && config.crop.width > 0 && config.crop.height > 0) {
    const left = Math.max(0, Math.min(config.crop.x, Math.max(0, imgWidth - 1)));
    const top = Math.max(0, Math.min(config.crop.y, Math.max(0, imgHeight - 1)));
    const width = Math.max(1, Math.min(config.crop.width, imgWidth - left));
    const height = Math.max(1, Math.min(config.crop.height, imgHeight - top));
    image.extract({ left, top, width, height });
  }

  // 2. 旋转
  if (config.rotate.enabled && config.rotate.angle !== 0) {
    const rotation = ((config.rotate.angle % 360) + 360) % 360;
    if (rotation === 90) {
      image.rotate(90);
    } else if (rotation === 180) {
      image.rotate(180);
    } else if (rotation === 270) {
      image.rotate(270);
    } else {
      // 任意角度旋转
      const fillColor = config.rotate.fillColor || '#ffffff';
      image.rotate(config.rotate.angle, {
        background: fillColor,
      });
    }
  }

  // F-02：翻转真实生效（注意 sharp 的 flip=垂直翻转、flop=水平翻转）
  if (config.rotate.enabled && config.rotate.flip) {
    image.flip();
  }
  if (config.rotate.enabled && config.rotate.flop) {
    image.flop();
  }

  // 3. 缩放
  if (config.resize.enabled) {
    const resizeOptions: sharp.ResizeOptions = {
      width: config.resize.width || undefined,
      height: config.resize.height || undefined,
      fit: mapResizeMode(config.resize.mode),
      withoutEnlargement: config.resize.onlyShrink,
      kernel: sharp.kernel.lanczos3,
    };
    image.resize(resizeOptions);
  }

  // 4. 特效 (亮度、对比度、饱和度)
  if (config.effects.enabled) {
    const { brightness, contrast, saturation, sharpness } = config.effects;

    if (brightness !== 1) {
      image.modulate({ brightness });
    }

    if (contrast !== 1) {
      image.linear(contrast, -(128 * contrast) + 128);
    }

    if (saturation !== 1) {
      image.modulate({ saturation });
    }

    if (sharpness !== 1) {
      image.sharpen(sharpness * 2);
    }
  }

  // 5. 滤镜
  if (config.filter.enabled) {
    applyFilter(image, config.filter.type, config.filter.intensity);
  }

  // 6. 边框
  if (config.border.enabled && config.border.width > 0) {
    applyBorder(image, config.border);
  }

  // 7. 水印（BUG-1：按当前（变换后）输出尺寸生成水印图层，
  //    避免 resize/crop 缩底图后叠加层 > 底图导致 sharp 抛错 500）
  if (config.watermark.enabled) {
    // BUG-3：opacity<=0 的透明水印无意义，直接跳过
    if (config.watermark.opacity > 0) {
      // 仅当存在会改变输出尺寸的变换时才探测当前尺寸（避免不必要的整幅渲染）
      const sizeMayChange =
        (config.resize.enabled &&
          (config.resize.width > 0 || config.resize.height > 0)) ||
        (config.crop.enabled &&
          config.crop.width > 0 &&
          config.crop.height > 0) ||
        (config.rotate.enabled && config.rotate.angle % 90 !== 0);

      let wmWidth = imgWidth;
      let wmHeight = imgHeight;
      if (sizeMayChange) {
        const dims = await probeOutputDimensions(image);
        wmWidth = dims.width;
        wmHeight = dims.height;
      }

      await applyWatermark(image, config.watermark, wmWidth, wmHeight);
    }
  }

  // F-05：保留元数据（在格式转换前调用，sharp 输出时带上 EXIF/ICC）
  if (config.preserveMetadata) {
    image.withMetadata();
  }

  // 8. 格式转换和输出
  const outputFormat = config.convert.enabled
    ? config.convert.format
    : getFormatFromFilename(originalName);

  const outputBuffer = await convertFormat(
    image,
    outputFormat,
    config.convert,
    config.compression
  );

  // 9. 生成文件名
  const filename = generateFilename(
    originalName,
    outputFormat,
    config.rename,
    counter,
    metadata
  );

  return {
    buffer: outputBuffer,
    filename,
    metadata: {
      width: imgWidth,
      height: imgHeight,
      format: FORMAT_MAP[outputFormat] || outputFormat,
      size: outputBuffer.length,
    },
  };
}

// =============================================
// 辅助函数
// =============================================

function mapResizeMode(mode: ResizeMode): keyof sharp.FitEnum {
  const modeMap: Record<ResizeMode, keyof sharp.FitEnum> = {
    contain: 'contain',
    cover: 'cover',
    stretch: 'fill',
    fill: 'inside',
  };
  return modeMap[mode] || 'contain';
}

function applyFilter(
  image: sharp.Sharp,
  type: FilterType,
  intensity: number
): void {
  switch (type) {
    case 'grayscale':
      image.grayscale();
      break;
    case 'sepia':
      image.tint({ r: 112, g: 66, b: 20 });
      break;
    case 'invert':
      image.negate();
      break;
    case 'blur':
      image.blur(Math.max(0.3, intensity * 5));
      break;
    case 'sharpen':
      image.sharpen(Math.max(0.1, intensity * 3));
      break;
    case 'emboss':
      image.convolve({
        width: 3,
        height: 3,
        kernel: [-2, -1, 0, -1, 1, 1, 0, 1, 2],
      });
      break;
    case 'edge':
      image.convolve({
        width: 3,
        height: 3,
        kernel: [-1, -1, -1, -1, 8, -1, -1, -1, -1],
      });
      break;
    case 'contrast':
      image.linear(intensity, -(128 * intensity) + 128);
      break;
    case 'brightness':
      image.modulate({ brightness: Math.max(0, intensity) });
      break;
    case 'vintage':
      image.tint({ r: 180, g: 130, b: 90 });
      break;
    case 'cool':
      image.tint({ r: 120, g: 160, b: 200 });
      break;
    case 'warm':
      image.tint({ r: 220, g: 150, b: 100 });
      break;
    case 'dramatic':
      image.linear(1.3, -30).modulate({ saturation: 1.2 });
      break;
    case 'noir':
      image.grayscale().linear(1.15, -20);
      break;
    default:
      break;
  }
}

function applyBorder(
  image: sharp.Sharp,
  border: { width: number; color: string; radius: number }
): void {
  image.extend({
    top: border.width,
    bottom: border.width,
    left: border.width,
    right: border.width,
    background: border.color,
  });
}

/** 探测当前管线（不含水印）的输出尺寸，用于按实际尺寸生成水印图层 */
async function probeOutputDimensions(
  image: sharp.Sharp
): Promise<{ width: number; height: number }> {
  const probe = await image.clone().toBuffer({ resolveWithObject: true });
  return { width: probe.info.width, height: probe.info.height };
}

/** 将水印图层缩放到不超过底图尺寸（兜底，防止 overlay > base 抛错） */
async function clampOverlayToBase(
  buffer: Buffer,
  baseWidth: number,
  baseHeight: number
): Promise<Buffer> {
  const meta = await safeSharp(buffer).metadata();
  const wmW = meta.width || 0;
  const wmH = meta.height || 0;
  if (wmW <= baseWidth && wmH <= baseHeight) return buffer;
  return safeSharp(buffer)
    .resize(Math.min(wmW, baseWidth), Math.min(wmH, baseHeight), {
      fit: 'inside',
      withoutEnlargement: true,
    })
    .png()
    .toBuffer();
}

// 安全类错误（SSRF 防护命中）需要保持抛出 → 路由返回 400 INVALID_CONFIG；
// 操作类错误（超时/404/非图片/重定向异常等）属于资源可用性问题，友好降级为跳过水印。
const WATERMARK_SECURITY_ERROR_CODES = new Set([
  'INVALID_URL',
  'INVALID_URL_PROTOCOL',
  'PRIVATE_IP_BLOCKED',
  'DNS_LOOKUP_EMPTY',
]);

/** 安全获取水印图；操作类失败返回 null（调用方跳过水印），安全类错误继续抛出 */
async function fetchWatermarkImageOrNull(
  imageUrl: string
): Promise<Buffer | null> {
  try {
    return await fetchWatermarkImage(imageUrl);
  } catch (error) {
    if (
      error instanceof WatermarkFetchError &&
      WATERMARK_SECURITY_ERROR_CODES.has(error.code)
    ) {
      throw error;
    }
    if (error instanceof WatermarkFetchError) {
      console.warn('[watermark] skipping image watermark (fetch failed):', error.code);
      return null;
    }
    throw error;
  }
}

async function applyWatermark(
  image: sharp.Sharp,
  watermark: WatermarkConfig,
  imageWidth: number,
  imageHeight: number
): Promise<void> {
  if (!imageWidth || !imageHeight) return;

  // F-06：tile 平铺模式
  if (watermark.position === 'tile') {
    await applyTileWatermark(image, watermark, imageWidth, imageHeight);
    return;
  }

  // 创建单枚水印图层
  let watermarkBuffer: Buffer;

  if (watermark.type === 'text' && watermark.text) {
    const svgText = createTextWatermarkSVG(
      watermark.text,
      watermark.fontSize,
      watermark.color,
      watermark.opacity,
      imageWidth,
      imageHeight,
      watermark.position,
      watermark.rotation,
      watermark.margin
    );
    watermarkBuffer = Buffer.from(svgText);
  } else if (watermark.type === 'image' && watermark.imageUrl) {
    // S-01：图片水印统一走安全获取函数（操作类失败友好降级跳过）
    const fetched = await fetchWatermarkImageOrNull(watermark.imageUrl);
    if (!fetched) return;
    // 兜底：水印图大于底图时缩放到不超过底图尺寸
    watermarkBuffer = await clampOverlayToBase(
      fetched,
      imageWidth,
      imageHeight
    );
  } else {
    return;
  }

  image.composite([
    {
      input: watermarkBuffer,
      gravity: mapPositionToGravity(watermark.position),
      blend: 'over',
    },
  ]);
}

/** F-06：平铺水印实现 */
async function applyTileWatermark(
  image: sharp.Sharp,
  watermark: WatermarkConfig,
  imageWidth: number,
  imageHeight: number
): Promise<void> {
  const spacing = Math.max(
    watermark.tileSpacing > 0 ? watermark.tileSpacing : 100,
    1
  );

  if (watermark.type === 'text' && watermark.text) {
    // 文本平铺：生成整幅 SVG <pattern>，一次 composite
    const svg = createTileTextWatermarkSVG(
      watermark.text,
      watermark.fontSize,
      watermark.color,
      watermark.opacity,
      imageWidth,
      imageHeight,
      watermark.rotation,
      spacing
    );
    image.composite([
      { input: Buffer.from(svg), gravity: 'center', blend: 'over' },
    ]);
    return;
  }

  if (watermark.type === 'image' && watermark.imageUrl) {
    // 图片平铺：先安全获取（操作类失败友好降级跳过），再按间距循环 composite
    const raw = await fetchWatermarkImageOrNull(watermark.imageUrl);
    if (!raw) return;

    let tileBuffer = raw;
    const rotation = ((watermark.rotation % 360) + 360) % 360;
    if (rotation !== 0) {
      tileBuffer = await safeSharp(raw)
        .rotate(rotation, { background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png()
        .toBuffer();
    }

    // 兜底：平铺单元大于底图时缩放到不超过底图尺寸
    tileBuffer = await clampOverlayToBase(tileBuffer, imageWidth, imageHeight);

    const tileMeta = await safeSharp(tileBuffer).metadata();
    const tileW = tileMeta.width || 100;
    const tileH = tileMeta.height || 100;

    const composites: sharp.OverlayOptions[] = [];
    const stepX = Math.max(spacing, tileW);
    const stepY = Math.max(spacing, tileH);

    for (let top = 0; top < imageHeight; top += stepY) {
      for (let left = 0; left < imageWidth; left += stepX) {
        composites.push({ input: tileBuffer, left, top, blend: 'over' });
      }
    }

    if (composites.length > 0) {
      image.composite(composites);
    }
  }
}

function createTextWatermarkSVG(
  text: string,
  fontSize: number,
  color: string,
  opacity: number,
  imageWidth: number,
  imageHeight: number,
  position: Exclude<WatermarkPosition, 'tile'>,
  rotation: number,
  margin: number
): string {
  const rgbaColor = hexToRgba(color, opacity);

  // 计算文本位置
  let x = margin;
  let y = imageHeight - margin;
  let textAnchor = 'start';

  switch (position) {
    case 'top-left':
      y = margin + fontSize;
      break;
    case 'top-center':
      x = imageWidth / 2;
      y = margin + fontSize;
      textAnchor = 'middle';
      break;
    case 'top-right':
      x = imageWidth - margin;
      y = margin + fontSize;
      textAnchor = 'end';
      break;
    case 'center-left':
      y = imageHeight / 2;
      break;
    case 'center':
      x = imageWidth / 2;
      y = imageHeight / 2;
      textAnchor = 'middle';
      break;
    case 'center-right':
      x = imageWidth - margin;
      y = imageHeight / 2;
      textAnchor = 'end';
      break;
    case 'bottom-left':
      y = imageHeight - margin;
      break;
    case 'bottom-center':
      x = imageWidth / 2;
      y = imageHeight - margin;
      textAnchor = 'middle';
      break;
    case 'bottom-right':
      x = imageWidth - margin;
      y = imageHeight - margin;
      textAnchor = 'end';
      break;
  }

  return `
    <svg width="${imageWidth}" height="${imageHeight}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
          .watermark-text {
            font-family: Arial, sans-serif;
            font-size: ${fontSize}px;
            font-weight: bold;
            fill: ${rgbaColor};
          }
        </style>
      </defs>
      <text
        x="${x}"
        y="${y}"
        class="watermark-text"
        text-anchor="${textAnchor}"
        transform="rotate(${rotation}, ${x}, ${y})"
      >${escapeXml(text)}</text>
    </svg>
  `;
}

/** F-06：文本平铺水印 SVG（使用 <pattern>，tileSpacing 控制间距，rotation 应用旋转） */
function createTileTextWatermarkSVG(
  text: string,
  fontSize: number,
  color: string,
  opacity: number,
  imageWidth: number,
  imageHeight: number,
  rotation: number,
  tileSpacing: number
): string {
  const rgbaColor = hexToRgba(color, opacity);
  const spacing = Math.max(tileSpacing, fontSize * 1.2, 1);
  const center = spacing / 2;

  return `
    <svg width="${imageWidth}" height="${imageHeight}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
          .watermark-tile {
            font-family: Arial, sans-serif;
            font-size: ${fontSize}px;
            font-weight: bold;
            fill: ${rgbaColor};
          }
        </style>
        <pattern id="wm-tile" width="${spacing}" height="${spacing}" patternUnits="userSpaceOnUse">
          <text
            x="${center}"
            y="${center}"
            class="watermark-tile"
            text-anchor="middle"
            dominant-baseline="central"
            transform="rotate(${rotation}, ${center}, ${center})"
          >${escapeXml(text)}</text>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#wm-tile)" />
    </svg>
  `;
}

function hexToRgba(hex: string, alpha: number): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return `rgba(255, 255, 255, ${alpha})`;

  const r = parseInt(result[1], 16);
  const g = parseInt(result[2], 16);
  const b = parseInt(result[3], 16);

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function mapPositionToGravity(
  position: Exclude<WatermarkPosition, 'tile'>
): sharp.Gravity {
  const gravityMap: Record<Exclude<WatermarkPosition, 'tile'>, sharp.Gravity> = {
    'top-left': 'northwest',
    'top-center': 'north',
    'top-right': 'northeast',
    'center-left': 'west',
    center: 'center',
    'center-right': 'east',
    'bottom-left': 'southwest',
    'bottom-center': 'south',
    'bottom-right': 'southeast',
  };
  return gravityMap[position] || 'southeast';
}

async function convertFormat(
  image: sharp.Sharp,
  format: string,
  convertConfig: ConvertConfig,
  compression: CompressionConfig
): Promise<Buffer> {
  const sharpFormat = FORMAT_MAP[format] || 'jpeg';

  // 直接编码（无压缩目标）
  const buffer = await encodeWithQuality(image, sharpFormat, convertConfig);

  // F-12：targetSize 压缩仅在 JPEG/WebP 输出时生效
  if (
    compression.enabled &&
    (sharpFormat === 'jpeg' || sharpFormat === 'webp')
  ) {
    return compressToTarget(image, sharpFormat, compression, convertConfig);
  }

  return buffer;
}

async function encodeWithQuality(
  image: sharp.Sharp,
  sharpFormat: string,
  convertConfig: ConvertConfig,
  quality?: number
): Promise<Buffer> {
  const q = quality ?? convertConfig.quality;
  const options: Record<string, unknown> = {};

  if (sharpFormat === 'jpeg') {
    options.quality = q;
    options.progressive = convertConfig.progressive;
    options.mozjpeg = convertConfig.optimize;
  } else if (sharpFormat === 'png') {
    options.compressionLevel = Math.floor((100 - q) / 10);
  } else if (sharpFormat === 'webp') {
    options.quality = q;
  } else if (sharpFormat === 'avif') {
    options.quality = q;
  } else if (sharpFormat === 'tiff') {
    options.quality = q;
  }

  return image
    .clone()
    .toFormat(sharpFormat as keyof sharp.FormatEnum, options)
    .toBuffer();
}

/**
 * F-12：二分法调整 quality 逼近 targetSize。
 * - targetSize 单位约定为 KB（默认值 500 即 500KB；与预设「Web 优化」语义一致）
 * - 最多尝试 8 次，最低 quality 20%
 * - 无法达到时返回最接近目标的一次结果
 */
async function compressToTarget(
  image: sharp.Sharp,
  sharpFormat: 'jpeg' | 'webp',
  compression: CompressionConfig,
  convertConfig: ConvertConfig
): Promise<Buffer> {
  const targetBytes = Math.max(1, Math.round(compression.targetSize) * 1024);
  const baseQuality = Math.min(
    100,
    Math.max(1, Math.round(convertConfig.quality || 85))
  );

  let low = 20;
  let high = Math.max(low, baseQuality);
  let best: { buffer: Buffer; size: number } | null = null;
  let attempts = 0;

  while (low <= high && attempts < 8) {
    const q = Math.round((low + high) / 2);
    const buffer = await encodeWithQuality(image, sharpFormat, convertConfig, q);
    attempts++;

    if (
      !best ||
      Math.abs(buffer.length - targetBytes) < Math.abs(best.size - targetBytes)
    ) {
      best = { buffer, size: buffer.length };
    }

    if (buffer.length <= targetBytes) {
      low = q + 1; // 还能提高质量
    } else {
      high = q - 1; // 太大，降低质量
    }
  }

  return best ? best.buffer : encodeWithQuality(image, sharpFormat, convertConfig, baseQuality);
}

function getFormatFromFilename(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || 'jpg';
  return FORMAT_MAP[ext] || 'jpeg';
}

function generateFilename(
  originalName: string,
  format: string,
  renameConfig: ProcessConfig['rename'],
  counter: number,
  metadata: sharp.Metadata
): string {
  if (!renameConfig.enabled) {
    const baseName = originalName.replace(/\.[^/.]+$/, '');
    return `${baseName}.${format}`;
  }

  const now = new Date();
  const context: Record<string, string | number> = {
    prefix: renameConfig.prefix,
    counter: counter + renameConfig.startNumber - 1,
    original_filename: originalName.replace(/\.[^/.]+$/, ''),
    width: metadata.width || 0,
    height: metadata.height || 0,
    date: now.toISOString().split('T')[0].replace(/-/g, ''),
    time: now.toTimeString().split(' ')[0].replace(/:/g, ''),
    format: format,
  };

  let filename = renameConfig.namingTemplate;

  // 替换模板变量
  for (const [key, value] of Object.entries(context)) {
    const regex = new RegExp(`\\{${key}(:\\d+d)?\\}`, 'g');
    filename = filename.replace(regex, (_, fmt: string | undefined) => {
      if (fmt && typeof value === 'number') {
        const padding = parseInt(fmt.replace(':', '').replace('d', ''), 10);
        return value.toString().padStart(padding, '0');
      }
      return String(value);
    });
  }

  return `${filename}.${format}`;
}

// =============================================
// 元数据接口
// =============================================

export interface ImageMetadata {
  width: number;
  height: number;
  format: string;
  size: number;
}

// =============================================
// 图像信息提取
// =============================================

export async function getImageInfo(buffer: Buffer): Promise<{
  width: number;
  height: number;
  format: string;
  size: number;
  hasAlpha: boolean;
}> {
  const metadata = await safeSharp(buffer).metadata();

  return {
    width: metadata.width || 0,
    height: metadata.height || 0,
    format: metadata.format || 'unknown',
    size: buffer.length,
    hasAlpha: metadata.hasAlpha || false,
  };
}

// =============================================
// 重复图像检测 (基于感知哈希)
// =============================================

export async function calculateImageHash(buffer: Buffer): Promise<string> {
  const hash = await safeSharp(buffer)
    .resize(8, 8, { fit: 'fill' })
    .grayscale()
    .raw()
    .toBuffer();

  // 简单的平均哈希
  const mean = hash.reduce((a, b) => a + b, 0) / hash.length;
  const binaryHash = Array.from(hash)
    .map((v) => (v > mean ? '1' : '0'))
    .join('');

  return binaryHash;
}

export function calculateHashSimilarity(hash1: string, hash2: string): number {
  if (hash1.length !== hash2.length) return 0;

  let same = 0;
  for (let i = 0; i < hash1.length; i++) {
    if (hash1[i] === hash2[i]) same++;
  }

  return same / hash1.length;
}
