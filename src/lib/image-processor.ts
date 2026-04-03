// =============================================
// 图像处理核心库 (基于 Sharp)
// =============================================

import sharp from 'sharp';
import {
  ProcessConfig,
  ResizeMode,
  FilterType,
  WatermarkPosition,
} from '@/types';

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
  let image = sharp(inputBuffer);
  const metadata = await image.metadata();
  
  // 1. 裁剪
  if (config.crop.enabled && config.crop.width > 0 && config.crop.height > 0) {
    image = image.extract({
      left: Math.max(0, config.crop.x),
      top: Math.max(0, config.crop.y),
      width: Math.min(config.crop.width, metadata.width! - config.crop.x),
      height: Math.min(config.crop.height, metadata.height! - config.crop.y),
    });
  }
  
  // 2. 旋转
  if (config.rotate.enabled && config.rotate.angle !== 0) {
    const rotation = ((config.rotate.angle % 360) + 360) % 360;
    if (rotation === 90) {
      image = image.rotate(90);
    } else if (rotation === 180) {
      image = image.rotate(180);
    } else if (rotation === 270) {
      image = image.rotate(270);
    } else {
      // 任意角度旋转
      const fillColor = config.rotate.fillColor || '#ffffff';
      image = image.rotate(config.rotate.angle, {
        background: fillColor,
      });
    }
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
    image = image.resize(resizeOptions);
  }
  
  // 4. 特效 (亮度、对比度、饱和度)
  if (config.effects.enabled) {
    const { brightness, contrast, saturation, sharpness } = config.effects;
    
    if (brightness !== 1) {
      image = image.modulate({
        brightness,
      });
    }
    
    if (contrast !== 1) {
      image = image.linear(contrast, -(128 * contrast) + 128);
    }
    
    if (saturation !== 1) {
      image = image.modulate({
        saturation,
      });
    }
    
    if (sharpness !== 1) {
      image = image.sharpen(sharpness * 2);
    }
  }
  
  // 5. 滤镜
  if (config.filter.enabled) {
    image = applyFilter(image, config.filter.type, config.filter.intensity);
  }
  
  // 6. 边框
  if (config.border.enabled && config.border.width > 0) {
    image = applyBorder(image, config.border);
  }
  
  // 7. 水印
  if (config.watermark.enabled) {
    image = await applyWatermark(image, config.watermark);
  }
  
  // 8. 格式转换和输出
  const outputFormat = config.convert.enabled
    ? config.convert.format
    : getFormatFromFilename(originalName);
  
  const outputBuffer = await convertFormat(image, outputFormat, config.convert);
  
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
      width: metadata.width!,
      height: metadata.height!,
      format: metadata.format!,
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
): sharp.Sharp {
  switch (type) {
    case 'grayscale':
      return image.grayscale();
    case 'sepia':
      return image.tint({ r: 112, g: 66, b: 20 });
    case 'invert':
      return image.negate();
    case 'blur':
      return image.blur(intensity * 5);
    case 'sharpen':
      return image.sharpen(intensity * 3);
    case 'emboss':
      return image.convolve({
        width: 3,
        height: 3,
        kernel: [-2, -1, 0, -1, 1, 1, 0, 1, 2],
      });
    case 'edge':
      return image.convolve({
        width: 3,
        height: 3,
        kernel: [-1, -1, -1, -1, 8, -1, -1, -1, -1],
      });
    case 'contrast':
      return image.linear(intensity, -(128 * intensity) + 128);
    case 'brightness':
      return image.modulate({ brightness: intensity });
    default:
      return image;
  }
}

function applyBorder(
  image: sharp.Sharp,
  border: { width: number; color: string; radius: number }
): sharp.Sharp {
  // 使用 extend 添加边框
  return image.extend({
    top: border.width,
    bottom: border.width,
    left: border.width,
    right: border.width,
    background: border.color,
  });
}

async function applyWatermark(
  image: sharp.Sharp,
  watermark: {
    type: 'text' | 'image';
    text?: string;
    imageUrl?: string;
    fontSize: number;
    color: string;
    opacity: number;
    position: WatermarkPosition;
    rotation: number;
    margin: number;
  }
): Promise<sharp.Sharp> {
  // 获取图像元数据
  const metadata = await image.metadata();
  const { width, height } = metadata;
  
  if (!width || !height) return image;
  
  // 创建水印图层
  let watermarkBuffer: Buffer;
  
  if (watermark.type === 'text' && watermark.text) {
    // 使用 SVG 创建文本水印
    const svgText = createTextWatermarkSVG(
      watermark.text,
      watermark.fontSize,
      watermark.color,
      watermark.opacity,
      width,
      height,
      watermark.position,
      watermark.rotation,
      watermark.margin
    );
    watermarkBuffer = Buffer.from(svgText);
  } else if (watermark.type === 'image' && watermark.imageUrl) {
    // 图片水印
    const response = await fetch(watermark.imageUrl);
    const arrayBuffer = await response.arrayBuffer();
    watermarkBuffer = Buffer.from(arrayBuffer);
  } else {
    return image;
  }
  
  return image.composite([
    {
      input: watermarkBuffer,
      gravity: mapPositionToGravity(watermark.position),
      blend: 'over',
    },
  ]);
}

function createTextWatermarkSVG(
  text: string,
  fontSize: number,
  color: string,
  opacity: number,
  imageWidth: number,
  imageHeight: number,
  position: WatermarkPosition,
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

function mapPositionToGravity(position: WatermarkPosition): sharp.Gravity {
  const gravityMap: Record<WatermarkPosition, sharp.Gravity> = {
    'top-left': 'northwest',
    'top-center': 'north',
    'top-right': 'northeast',
    'center-left': 'west',
    center: 'center',
    'center-right': 'east',
    'bottom-left': 'southwest',
    'bottom-center': 'south',
    'bottom-right': 'southeast',
    'tile': 'center', // tile 模式使用 center 作为默认
  };
  return gravityMap[position] || 'southeast';
}

async function convertFormat(
  image: sharp.Sharp,
  format: string,
  convertConfig: ProcessConfig['convert']
): Promise<Buffer> {
  const sharpFormat = FORMAT_MAP[format] || 'jpeg';
  
  const options: Record<string, unknown> = {};
  
  if (sharpFormat === 'jpeg') {
    options.quality = convertConfig.quality;
    options.progressive = convertConfig.progressive;
    options.mozjpeg = convertConfig.optimize;
  } else if (sharpFormat === 'png') {
    options.compressionLevel = Math.floor((100 - convertConfig.quality) / 10);
  } else if (sharpFormat === 'webp') {
    options.quality = convertConfig.quality;
  } else if (sharpFormat === 'avif') {
    options.quality = convertConfig.quality;
  } else if (sharpFormat === 'tiff') {
    options.quality = convertConfig.quality;
  }
  
  return image.toFormat(sharpFormat as keyof sharp.FormatEnum, options).toBuffer();
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
    filename = filename.replace(regex, (_, format) => {
      if (format && typeof value === 'number') {
        const padding = parseInt(format.replace(':', '').replace('d', ''));
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
  const metadata = await sharp(buffer).metadata();
  
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
  const hash = await sharp(buffer)
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
