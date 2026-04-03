import { NextRequest, NextResponse } from 'next/server';
import { 
  successResponse, 
  errorResponse, 
  ErrorCodes 
} from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';

// =============================================
// POST /api/upload - 上传并获取图片信息
// =============================================

// 文件类型验证 - 通过 Magic Number 验证真实文件类型
const FILE_SIGNATURES: Record<string, { signature: number[]; offset: number }> = {
  'image/jpeg': { signature: [0xff, 0xd8, 0xff], offset: 0 },
  'image/png': { signature: [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a], offset: 0 },
  'image/gif': { signature: [0x47, 0x49, 0x46, 0x38], offset: 0 },
  'image/webp': { signature: [0x52, 0x49, 0x46, 0x46], offset: 0 }, // RIFF, need additional check
  'image/bmp': { signature: [0x42, 0x4d], offset: 0 },
  'image/tiff': { signature: [0x49, 0x49, 0x2a, 0x00], offset: 0 }, // Little-endian
};

const ALLOWED_TYPES = Object.keys(FILE_SIGNATURES);
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

// 验证文件 Magic Number
function validateFileType(buffer: Buffer, claimedType: string): boolean {
  const signatureInfo = FILE_SIGNATURES[claimedType];
  if (!signatureInfo) return false;

  const { signature, offset } = signatureInfo;
  
  // 特殊处理 WebP (RIFF....WEBP)
  if (claimedType === 'image/webp') {
    if (buffer.length < 12) return false;
    const riffMatch = buffer.slice(0, 4).equals(Buffer.from([0x52, 0x49, 0x46, 0x46]));
    const webpMatch = buffer.slice(8, 12).equals(Buffer.from([0x57, 0x45, 0x42, 0x50]));
    return riffMatch && webpMatch;
  }

  // 特殊处理 TIFF (也支持 Big-endian)
  if (claimedType === 'image/tiff') {
    const littleEndian = buffer.slice(0, 4).equals(Buffer.from([0x49, 0x49, 0x2a, 0x00]));
    const bigEndian = buffer.slice(0, 4).equals(Buffer.from([0x4d, 0x4d, 0x00, 0x2a]));
    return littleEndian || bigEndian;
  }

  // 常规验证
  if (buffer.length < signature.length + offset) return false;
  
  for (let i = 0; i < signature.length; i++) {
    if (buffer[offset + i] !== signature[i]) return false;
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

// 延迟加载 image-processor 避免循环依赖问题
async function getImageInfo(buffer: Buffer) {
  const { getImageInfo: getInfo } = await import('@/lib/image-processor');
  return getInfo(buffer);
}

export async function POST(request: NextRequest) {
  try {
    // 检查速率限制
    const rateLimit = checkRateLimit(request, 'upload');
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

    // 限制请求体大小
    const contentLength = parseInt(request.headers.get('content-length') || '0');
    if (contentLength > MAX_FILE_SIZE * 2) {
      return NextResponse.json(
        errorResponse(ErrorCodes.REQUEST_BODY_TOO_LARGE, 'Request body too large'),
        { status: 413 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    
    if (!file) {
      return NextResponse.json(
        errorResponse(ErrorCodes.NO_FILE_PROVIDED, 'No file provided'),
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

    // 验证 MIME 类型
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_FILE_TYPE, 
          `Invalid file type. Supported: ${ALLOWED_TYPES.map(t => t.split('/')[1].toUpperCase()).join(', ')}`,
          { allowedTypes: ALLOWED_TYPES, actualType: file.type }
        ),
        { status: 400 }
      );
    }

    // 读取文件内容
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // 验证真实文件类型（Magic Number）
    if (!validateFileType(buffer, file.type)) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.FILE_SIGNATURE_MISMATCH, 
          'File content does not match the claimed file type',
          { claimedType: file.type }
        ),
        { status: 400 }
      );
    }

    // 安全处理文件名
    const safeName = sanitizeFilename(file.name);

    // 获取图片信息
    const info = await getImageInfo(buffer);
    
    // 将图片转为 base64 用于预览（限制预览图大小以提高性能）
    let previewBase64: string;
    const maxPreviewSize = 2 * 1024 * 1024; // 2MB
    if (buffer.length > maxPreviewSize) {
      // 大图片：生成缩略图预览
      const sharp = (await import('sharp')).default;
      const thumbnail = await sharp(buffer)
        .resize(800, 800, { fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: 80 })
        .toBuffer();
      previewBase64 = `data:image/jpeg;base64,${thumbnail.toString('base64')}`;
    } else {
      previewBase64 = `data:${file.type};base64,${buffer.toString('base64')}`;
    }
    
    return NextResponse.json(
      successResponse({
        name: safeName,
        size: file.size,
        type: file.type,
        width: info.width,
        height: info.height,
        format: info.format,
        hasAlpha: info.hasAlpha,
        preview: previewBase64,
      }),
      {
        headers: getRateLimitHeaders('upload'),
      }
    );
  } catch (error) {
    console.error('Upload error:', error);
    
    // 不暴露内部错误细节
    const message = error instanceof Error && error.message.includes('Invalid') 
      ? error.message 
      : 'Upload failed. Please try again.';
    
    return NextResponse.json(
      errorResponse(ErrorCodes.INTERNAL_ERROR, message),
      { status: 500 }
    );
  }
}
