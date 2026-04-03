import { NextRequest, NextResponse } from 'next/server';

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
const MAX_FILES_PER_REQUEST = 50;

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

// 安全的文件名处理 - 防止路径遍历
function sanitizeFilename(filename: string): string {
  // 移除路径分隔符和特殊字符
  return filename
    .replace(/[\/\\]/g, '_')
    .replace(/\.\./g, '')
    .replace(/[<>:"|?*\x00-\x1f]/g, '_')
    .slice(0, 255); // 限制文件名长度
}

// 延迟加载 image-processor 避免循环依赖问题
async function getImageInfo(buffer: Buffer) {
  const { getImageInfo: getInfo } = await import('@/lib/image-processor');
  return getInfo(buffer);
}

export async function POST(request: NextRequest) {
  try {
    // 检查 Content-Type
    const contentType = request.headers.get('content-type') || '';
    if (!contentType.includes('multipart/form-data')) {
      return NextResponse.json(
        { error: 'Invalid content type. Expected multipart/form-data' },
        { status: 400 }
      );
    }

    // 限制请求体大小
    const contentLength = parseInt(request.headers.get('content-length') || '0');
    if (contentLength > MAX_FILE_SIZE * 2) {
      return NextResponse.json(
        { error: 'Request body too large' },
        { status: 413 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: `File too large. Maximum size: ${MAX_FILE_SIZE / 1024 / 1024}MB` },
        { status: 400 }
      );
    }

    // 验证 MIME 类型
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json(
        { error: `Invalid file type. Supported: ${ALLOWED_TYPES.map(t => t.split('/')[1].toUpperCase()).join(', ')}` },
        { status: 400 }
      );
    }

    // 读取文件内容
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // 验证真实文件类型（Magic Number）
    if (!validateFileType(buffer, file.type)) {
      return NextResponse.json(
        { error: 'File content does not match the claimed file type' },
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
    
    return NextResponse.json({
      name: safeName,
      size: file.size,
      type: file.type,
      width: info.width,
      height: info.height,
      format: info.format,
      hasAlpha: info.hasAlpha,
      preview: previewBase64,
    });
  } catch (error) {
    console.error('Upload error:', error);
    
    // 不暴露内部错误细节
    const message = error instanceof Error && error.message.includes('Invalid') 
      ? error.message 
      : 'Upload failed. Please try again.';
    
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
