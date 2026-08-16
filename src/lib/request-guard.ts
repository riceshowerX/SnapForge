// =============================================
// SnapForge 请求体大小守卫（仅服务端使用）
// =============================================
// S-03：在解析 multipart body 之前做强 Content-Length 校验。
// 单独成文件以避免把 next/server 拉进客户端 bundle。

import { NextRequest, NextResponse } from 'next/server';
import { errorResponse, ErrorCodes } from './api-response';

/**
 * 在解析 multipart body 之前做强 Content-Length 校验（S-03）。
 * 缺失或超过上限直接返回 413 响应；通过则返回 null。
 */
export function enforceContentLength(
  request: NextRequest,
  maxBytes: number
): NextResponse | null {
  const header = request.headers.get('content-length');

  if (!header) {
    return NextResponse.json(
      errorResponse(
        ErrorCodes.REQUEST_BODY_TOO_LARGE,
        'Missing Content-Length header. Chunked uploads are not allowed.'
      ),
      { status: 413 }
    );
  }

  const length = parseInt(header, 10);
  if (Number.isNaN(length) || length <= 0 || length > maxBytes) {
    return NextResponse.json(
      errorResponse(
        ErrorCodes.REQUEST_BODY_TOO_LARGE,
        `Request body too large. Maximum allowed: ${Math.floor(maxBytes / 1024 / 1024)}MB`,
        { maxBytes, actualLength: Number.isNaN(length) ? null : length }
      ),
      { status: 413 }
    );
  }

  return null;
}
