import { NextRequest, NextResponse } from 'next/server';
import { processImage, getImageInfo, WatermarkFetchError } from '@/lib/image-processor';
import { errorResponse, ErrorCodes } from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';
import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  MAX_PROCESS_BODY_SIZE,
  sanitizeFilename,
  detectImageMime,
} from '@/lib/file-validation';
import { enforceContentLength } from '@/lib/request-guard';
import { processConfigSchema, deepMergeProcessConfig } from '@/lib/config-schema';

// =============================================
// POST /api/process - 处理单张图片
// =============================================
// S-03：Content-Length 强校验；S-04：magic number 校验；
// Q-03：zod schema 校验 + 深合并，校验失败返回 400；
// F-11：crop 越界返回 400 CONFIG_PARAMS_OUT_OF_RANGE；
// F-07：Content-Disposition 同时输出 filename*（RFC 5987）。

const MAX_CONFIG_SIZE = 10 * 1024; // 10KB for config JSON

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
        errorResponse(
          ErrorCodes.INVALID_REQUEST,
          'Invalid content type. Expected multipart/form-data'
        ),
        { status: 400 }
      );
    }

    // S-03：在 request.formData() 之前做强 Content-Length 校验
    const bodyTooLarge = enforceContentLength(request, MAX_PROCESS_BODY_SIZE);
    if (bodyTooLarge) {
      return bodyTooLarge;
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

    // 读取文件内容
    const buffer = Buffer.from(await file.arrayBuffer());

    // S-04：magic number 校验（不信任客户端 MIME）
    const detectedMime = detectImageMime(buffer);
    if (
      !detectedMime ||
      !ALLOWED_TYPES.includes(detectedMime as (typeof ALLOWED_TYPES)[number])
    ) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_FILE_TYPE,
          'Unsupported or invalid image file. Only JPEG, PNG, WebP and GIF are supported.',
          { detectedMime: detectedMime || null }
        ),
        { status: 400 }
      );
    }

    // Q-03：zod schema 校验 + 深合并（替代手写 validateConfig 浅合并）
    let parsed: unknown;
    try {
      parsed = JSON.parse(configJson);
    } catch {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_JSON, 'Invalid JSON configuration'),
        { status: 400 }
      );
    }

    const schemaResult = processConfigSchema.safeParse(parsed);
    if (!schemaResult.success) {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_CONFIG, 'Invalid configuration format', {
          issues: schemaResult.error.issues.map((i) => ({
            path: i.path.join('.'),
            message: i.message,
          })),
        }),
        { status: 400 }
      );
    }

    const config = deepMergeProcessConfig(schemaResult.data);

    // 验证计数器
    const counter = counterStr ? parseInt(counterStr, 10) : 1;
    if (Number.isNaN(counter) || counter < 1 || counter > 10000) {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_CONFIG, 'Invalid counter value', {
          min: 1,
          max: 10000,
          actual: counter,
        }),
        { status: 400 }
      );
    }

    // F-11：crop 越界返回 400（先获取图片尺寸再校验）
    const info = await getImageInfo(buffer);
    if (
      config.crop.enabled &&
      (config.crop.x + config.crop.width > info.width ||
        config.crop.y + config.crop.height > info.height)
    ) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.CONFIG_PARAMS_OUT_OF_RANGE,
          'Crop area exceeds image bounds',
          {
            imageWidth: info.width,
            imageHeight: info.height,
            cropX: config.crop.x,
            cropY: config.crop.y,
            cropWidth: config.crop.width,
            cropHeight: config.crop.height,
          }
        ),
        { status: 400 }
      );
    }

    // 安全处理文件名
    const safeName = sanitizeFilename(file.name);

    // 处理图片
    const result = await processImage(buffer, config, safeName, counter);

    // 返回处理后的图片
    const headers = new Headers({
      'Content-Type': `image/${result.metadata.format}`,
      // F-07：RFC 5987 filename*，保证中文/特殊字符文件名可正常下载
      'Content-Disposition': `attachment; filename="${encodeURIComponent(result.filename)}"; filename*=UTF-8''${encodeURIComponent(result.filename)}`,
      'X-Image-Width': result.metadata.width.toString(),
      'X-Image-Height': result.metadata.height.toString(),
      'X-Image-Size': result.metadata.size.toString(),
      'Cache-Control': 'no-store',
      ...getRateLimitHeaders('process'),
    });

    return new NextResponse(new Uint8Array(result.buffer), { headers });
  } catch (error) {
    // S-01：水印远程 URL 校验失败（内网/保留网段/协议/超时/重定向等）返回 400
    if (error instanceof WatermarkFetchError) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_CONFIG,
          'Watermark image URL is not allowed or unreachable.',
          { reason: error.code }
        ),
        { status: 400 }
      );
    }

    console.error('Image processing error:', error);

    // 不暴露内部错误细节
    const message =
      error instanceof Error && error.message.includes('Invalid')
        ? error.message
        : 'Processing failed';

    return NextResponse.json(
      errorResponse(ErrorCodes.PROCESSING_FAILED, message),
      { status: 500 }
    );
  }
}
