// =============================================
// SnapForge 请求速率限制工具
// =============================================
// S-02 加固：
// - 客户端标识只信任 Next.js 提供的真实连接 IP（request.ip），
//   绝不信任任何可由客户端伪造的转发头（本项目无可信反向代理）。
// - rateLimitStore 增加容量上限，超限拒绝新 key 并记日志。
// - cleanup 改为按请求概率抽样触发，避免长时间无请求时 Map 无限增长。
// - 无 IP 时回退到 'unknown' 单独限流桶。

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

// Map 容量上限：防止攻击者通过伪造 IP 数量耗尽内存
const MAX_STORE_ENTRIES = 100_000;

// 每次请求触发全量清理的概率（1%）
const CLEANUP_PROBABILITY = 0.01;

// 速率限制配置
const RATE_LIMITS: Record<string, RateLimitConfig> = {
  upload: { windowMs: 60 * 1000, maxRequests: 30 }, // 每分钟 30 次上传
  process: { windowMs: 60 * 1000, maxRequests: 20 }, // 每分钟 20 次处理
  duplicates: { windowMs: 60 * 1000, maxRequests: 10 }, // 每分钟 10 次重复检测
  default: { windowMs: 60 * 1000, maxRequests: 60 }, // 默认每分钟 60 次
};

/**
 * 获取客户端标识。
 * 只信任 Next.js 运行时注入的真实连接地址（request.ip）。
 * 注意：NextRequest 类型未暴露 ip 字段，但 Node/Edge 运行时会在请求对象上注入；
 * 此处做类型收窄的安全读取。绝不信任任何可由客户端伪造的转发头。
 * 无 IP 时回退 'unknown' 单独限流桶（避免所有无 IP 请求合桶逃逸限流）。
 */
function getClientIdentifier(request: NextRequest): string {
  const ip = (request as NextRequest & { ip?: string }).ip;
  return ip || 'unknown';
}

/** 清理所有已过期条目 */
function cleanupExpiredEntries(now: number): void {
  let cleaned = 0;
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetTime < now) {
      rateLimitStore.delete(key);
      cleaned++;
    }
  }
  if (cleaned > 0) {
    console.log(`[rate-limit] cleaned ${cleaned} expired entries`);
  }
}

// 检查速率限制
export function checkRateLimit(
  request: NextRequest,
  endpoint: keyof typeof RATE_LIMITS = 'default'
): { allowed: boolean; response?: NextResponse } {
  const now = Date.now();

  // 按概率抽样清理过期条目（避免每次请求全量扫描，同时防止 Map 无限增长）
  if (Math.random() < CLEANUP_PROBABILITY) {
    cleanupExpiredEntries(now);
  }

  const config = RATE_LIMITS[endpoint] || RATE_LIMITS.default;
  const clientId = getClientIdentifier(request);
  const key = `${endpoint}:${clientId}`;

  let entry = rateLimitStore.get(key);

  // 检查是否需要重置
  if (!entry || entry.resetTime < now) {
    entry = {
      count: 0,
      resetTime: now + config.windowMs,
    };
  }

  // 容量上限：新 key 且 Map 已满时直接拒绝（防内存耗尽）
  if (!rateLimitStore.has(key) && rateLimitStore.size >= MAX_STORE_ENTRIES) {
    console.warn(
      `[rate-limit] store at capacity (${rateLimitStore.size}), rejecting new key`
    );
    return {
      allowed: false,
      response: NextResponse.json(
        errorResponse(
          ErrorCodes.RATE_LIMIT_EXCEEDED,
          'Rate limit store is full. Please try again later.',
          { limit: config.maxRequests, windowMs: config.windowMs, retryAfter: config.windowMs / 1000 }
        ),
        {
          status: 429,
          headers: {
            'Retry-After': String(Math.ceil(config.windowMs / 1000)),
            'X-RateLimit-Limit': String(config.maxRequests),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': String(entry.resetTime),
          },
        }
      ),
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
