// =============================================
// SnapForge 请求速率限制工具
// =============================================

import { NextRequest, NextResponse } from 'next/server';
import { errorResponse, ErrorCodes } from './api-response';

// 速率限制配置
interface RateLimitConfig {
  windowMs: number; // 时间窗口（毫秒）
  maxRequests: number; // 最大请求数
}

// 存储请求记录
interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const rateLimitStore = new Map<string, RateLimitEntry>();

// 清理过期记录（每小时清理一次）
const CLEANUP_INTERVAL = 60 * 60 * 1000;
let lastCleanup = Date.now();

function cleanupExpiredEntries() {
  const now = Date.now();
  if (now - lastCleanup < CLEANUP_INTERVAL) return;
  
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetTime < now) {
      rateLimitStore.delete(key);
    }
  }
  lastCleanup = now;
}

// 速率限制配置
const RATE_LIMITS: Record<string, RateLimitConfig> = {
  upload: { windowMs: 60 * 1000, maxRequests: 30 }, // 每分钟 30 次上传
  process: { windowMs: 60 * 1000, maxRequests: 20 }, // 每分钟 20 次处理
  duplicates: { windowMs: 60 * 1000, maxRequests: 10 }, // 每分钟 10 次重复检测
  default: { windowMs: 60 * 1000, maxRequests: 60 }, // 默认每分钟 60 次
};

// 获取客户端标识
function getClientIdentifier(request: NextRequest): string {
  // 优先使用 X-Forwarded-For（支持代理）
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  
  // 其次使用 X-Real-IP
  const realIp = request.headers.get('x-real-ip');
  if (realIp) {
    return realIp;
  }
  
  // 最后使用 CF-Connecting-IP（Cloudflare）
  const cfIp = request.headers.get('cf-connecting-ip');
  if (cfIp) {
    return cfIp;
  }
  
  // 默认回退
  return '127.0.0.1';
}

// 检查速率限制
export function checkRateLimit(
  request: NextRequest,
  endpoint: keyof typeof RATE_LIMITS = 'default'
): { allowed: boolean; response?: NextResponse } {
  // 清理过期记录
  cleanupExpiredEntries();
  
  const config = RATE_LIMITS[endpoint] || RATE_LIMITS.default;
  const clientId = getClientIdentifier(request);
  const key = `${endpoint}:${clientId}`;
  const now = Date.now();
  
  let entry = rateLimitStore.get(key);
  
  // 检查是否需要重置
  if (!entry || entry.resetTime < now) {
    entry = {
      count: 0,
      resetTime: now + config.windowMs,
    };
  }
  
  // 检查是否超限
  if (entry.count >= config.maxRequests) {
    const retryAfter = Math.ceil((entry.resetTime - now) / 1000);
    return {
      allowed: false,
      response: NextResponse.json(
        errorResponse(
          ErrorCodes.RATE_LIMIT_EXCEEDED,
          `Rate limit exceeded. Please try again in ${retryAfter} seconds.`,
          {
            limit: config.maxRequests,
            windowMs: config.windowMs,
            retryAfter,
          }
        ),
        {
          status: 429,
          headers: {
            'Retry-After': String(retryAfter),
            'X-RateLimit-Limit': String(config.maxRequests),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': String(entry.resetTime),
          },
        }
      ),
    };
  }
  
  // 更新计数
  entry.count++;
  rateLimitStore.set(key, entry);
  
  return { allowed: true };
}

// 获取速率限制信息（用于响应头）
export function getRateLimitHeaders(
  endpoint: keyof typeof RATE_LIMITS = 'default'
): Record<string, string> {
  const config = RATE_LIMITS[endpoint] || RATE_LIMITS.default;
  return {
    'X-RateLimit-Limit': String(config.maxRequests),
    'X-RateLimit-Window': String(config.windowMs / 1000) + 's',
  };
}
