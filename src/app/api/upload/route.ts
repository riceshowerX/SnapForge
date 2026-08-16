import { NextRequest, NextResponse } from 'next/server';
import {
  successResponse,
  errorResponse,
  ErrorCodes,
} from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';
import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  MAX_UPLOAD_BODY_SIZE,
  sanitizeFilename,
  validateFileType,
} from '@/lib/file-validation';
import { enforceContentLength } from '@/lib/request-guard';

// =============================================
// POST /api/upload - 上传并获取图片信息
// =============================================
// F-01 / P-02：返回 preview（≤2MB 为原始 data URL，>2MB 为 800×800 缩略图）
// 与 originalDataUrl（>2MB 时返回完整原始 base64，供前端写入 IndexedDB）。
// S-03：在解析 formData 前做强 Content-Length 校验。

const THUMBNAIL_MAX_SIZE = 2 * 1024 * 1024; // 2MB
const THUMBNAIL_DIMENSION = 800;

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
        errorResponse(
          ErrorCodes.INVALID_REQUEST,
          'Invalid content type. Expected multipart/form-data'
        ),
        { status: 400 }
      );
    }

    // S-03：在 request.formData() 之前做强 Content-Length 校验
    const bodyTooLarge = enforceContentLength(request, MAX_UPLOAD_BODY_SIZE);
    if (bodyTooLarge) {
      return bodyTooLarge;
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

    // 验证 MIME 类型（白名单，拒绝 SVG/PDF 等矢量）
    if (!ALLOWED_TYPES.includes(file.type as (typeof ALLOWED_TYPES)[number])) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_FILE_TYPE,
          `Invalid file type. Supported: ${ALLOWED_TYPES.map((t) => t.split('/')[1].toUpperCase()).join(', ')}`,
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

    // 获取图片信息（sharp 已带像素上限）
    const info = await getImageInfo(buffer);

    // F-01 / P-02：preview 与 originalDataUrl 分离
    let previewBase64: string;
    let originalDataUrl = '';

    if (buffer.length > THUMBNAIL_MAX_SIZE) {
      // 大图片：生成缩略图预览（P-05：显式像素上限），并返回完整原始 base64
      const sharp = (await import('sharp')).default;
      const thumbnail = await sharp(buffer, {
        limitInputPixels: 64_000_000,
        failOn: 'error',
      })
        .resize(THUMBNAIL_DIMENSION, THUMBNAIL_DIMENSION, {
          fit: 'inside',
          withoutEnlargement: true,
        })
        .jpeg({ quality: 80 })
        .toBuffer();
      previewBase64 = `data:image/jpeg;base64,${thumbnail.toString('base64')}`;
      originalDataUrl = `data:${file.type};base64,${buffer.toString('base64')}`;
    } else {
      // ≤2MB：preview 即原始数据（originalDataUrl 留空，前端直接用 preview 作为原始）
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
        originalDataUrl,
      }),
      {
        headers: getRateLimitHeaders('upload'),
      }
    );
  } catch (error) {
    console.error('Upload error:', error);

    // 不暴露内部错误细节
    const message =
      error instanceof Error && error.message.includes('Invalid')
        ? error.message
        : 'Upload failed. Please try again.';

    return NextResponse.json(
      errorResponse(ErrorCodes.INTERNAL_ERROR, message),
      { status: 500 }
    );
  }
}
