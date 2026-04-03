import { NextRequest, NextResponse } from 'next/server';
import { processImage } from '@/lib/image-processor';
import { ProcessConfig, defaultProcessConfig } from '@/types';
import { 
  errorResponse, 
  ErrorCodes 
} from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';

// =============================================
// POST /api/process - 处理单张图片
// =============================================

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const MAX_CONFIG_SIZE = 10 * 1024; // 10KB for config JSON

// 验证配置对象，防止恶意配置
function validateConfig(config: unknown): config is ProcessConfig {
  if (!config || typeof config !== 'object') return false;
  
  const c = config as Record<string, unknown>;
  
  // 验证各个配置项的类型
  const validators: Record<string, (v: unknown) => boolean> = {
    convert: (v) => !v || typeof v === 'object',
    resize: (v) => !v || typeof v === 'object',
    crop: (v) => !v || typeof v === 'object',
    rotate: (v) => !v || typeof v === 'object',
    filter: (v) => !v || typeof v === 'object',
    watermark: (v) => !v || typeof v === 'object',
    effects: (v) => !v || typeof v === 'object',
    border: (v) => !v || typeof v === 'object',
    rename: (v) => !v || typeof v === 'object',
    compression: (v) => !v || typeof v === 'object',
    preserveMetadata: (v) => v === undefined || typeof v === 'boolean',
  };

  for (const [key, validator] of Object.entries(validators)) {
    if (c[key] !== undefined && !validator(c[key])) {
      return false;
    }
  }

  return true;
}

// 增强的文件名安全处理 - 防止路径遍历和 Unicode 攻击
function sanitizeFilename(filename: string): string {
  // 1. 移除所有路径分隔符
  let safe = filename.replace(/[\/\\]/g, '_');
  
  // 2. 移除路径遍历尝试
  safe = safe.replace(/\.\./g, '');
  
  // 3. 移除 Unicode 控制字符和危险字符
  safe = safe.replace(/[<>:"|?*\x00-\x1f\x7f]/g, '_');
  
  // 4. 移除 Unicode 规范化攻击（NFC/NFD）
  safe = safe.normalize('NFC');
  
  // 5. 移除空白字符
  safe = safe.trim().replace(/\s+/g, '_');
  
  // 6. 限制长度
  safe = safe.slice(0, 255);
  
  // 7. 确保不为空
  if (!safe || safe === '.' || safe === '..') {
    safe = 'unnamed_image';
  }
  
  return safe;
}

// 验证数值参数在安全范围内
function validateNumericParams(config: ProcessConfig): boolean {
  // 尺寸限制
  if (config.resize.enabled) {
    if (config.resize.width < 1 || config.resize.width > 20000) return false;
    if (config.resize.height < 1 || config.resize.height > 20000) return false;
  }
  
  // 裁剪限制
  if (config.crop.enabled) {
    if (config.crop.width < 1 || config.crop.width > 50000) return false;
    if (config.crop.height < 1 || config.crop.height > 50000) return false;
    if (config.crop.x < 0 || config.crop.y < 0) return false;
  }
  
  // 质量限制
  if (config.convert.quality < 1 || config.convert.quality > 100) return false;
  
  // 特效限制
  if (config.effects.enabled) {
    if (config.effects.brightness < 0 || config.effects.brightness > 10) return false;
    if (config.effects.contrast < 0 || config.effects.contrast > 10) return false;
    if (config.effects.saturation < 0 || config.effects.saturation > 10) return false;
  }
  
  // 边框限制
  if (config.border.enabled && config.border.width > 100) return false;
  
  return true;
}

export async function POST(request: NextRequest) {
  try {
    // 检查速率限制
    const rateLimit = checkRateLimit(request, 'process');
    if (!rateLimit.allowed && rateLimit.response) {
      return rateLimit.response;
    }

    // 检查 Content-Type
    const contentType = request.headers.get('content-type') || '';
    if (!contentType.includes('multipart/form-data')) {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_REQUEST, 'Invalid content type. Expected multipart/form-data'),
        { status: 400 }
      );
    }

    const formData = await request.formData();
    
    const file = formData.get('file') as File | null;
    const configJson = formData.get('config') as string | null;
    const counterStr = formData.get('counter') as string | null;
    
    if (!file || !configJson) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.MISSING_FIELD, 
          'Missing required fields: file and config'
        ),
        { status: 400 }
      );
    }

    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.FILE_TOO_LARGE, 
          `File too large. Maximum size: ${MAX_FILE_SIZE / 1024 / 1024}MB`,
          { maxSize: MAX_FILE_SIZE, actualSize: file.size }
        ),
        { status: 400 }
      );
    }

    // 验证配置大小
    if (configJson.length > MAX_CONFIG_SIZE) {
      return NextResponse.json(
        errorResponse(ErrorCodes.CONFIG_TOO_LARGE, 'Configuration too large'),
        { status: 400 }
      );
    }

    // 解析并验证配置
    let config: ProcessConfig;
    try {
      const parsed = JSON.parse(configJson);
      if (!validateConfig(parsed)) {
        return NextResponse.json(
          errorResponse(ErrorCodes.INVALID_CONFIG, 'Invalid configuration format'),
          { status: 400 }
        );
      }
      config = { ...defaultProcessConfig, ...parsed };
    } catch {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_JSON, 'Invalid JSON configuration'),
        { status: 400 }
      );
    }

    // 验证数值参数
    if (!validateNumericParams(config)) {
      return NextResponse.json(
        errorResponse(ErrorCodes.CONFIG_PARAMS_OUT_OF_RANGE, 'Configuration parameters out of valid range'),
        { status: 400 }
      );
    }

    // 验证计数器
    const counter = counterStr ? parseInt(counterStr, 10) : 1;
    if (isNaN(counter) || counter < 1 || counter > 10000) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_CONFIG, 
          'Invalid counter value',
          { min: 1, max: 10000, actual: counter }
        ),
        { status: 400 }
      );
    }

    // 安全处理文件名
    const safeName = sanitizeFilename(file.name);
    
    // 处理图片
    const buffer = Buffer.from(await file.arrayBuffer());
    const result = await processImage(buffer, config, safeName, counter);
    
    // 返回处理后的图片
    const headers = new Headers({
      'Content-Type': `image/${result.metadata.format}`,
      'Content-Disposition': `attachment; filename="${encodeURIComponent(result.filename)}"`,
      'X-Image-Width': result.metadata.width.toString(),
      'X-Image-Height': result.metadata.height.toString(),
      'X-Image-Size': result.metadata.size.toString(),
      'Cache-Control': 'no-store',
      ...getRateLimitHeaders('process'),
    });
    
    return new NextResponse(new Uint8Array(result.buffer), { headers });
  } catch (error) {
    console.error('Image processing error:', error);
    
    // 不暴露内部错误细节
    const message = error instanceof Error 
      ? (error.message.includes('Invalid') ? error.message : 'Processing failed')
      : 'Processing failed';
    
    return NextResponse.json(
      errorResponse(ErrorCodes.PROCESSING_FAILED, message),
      { status: 500 }
    );
  }
}
