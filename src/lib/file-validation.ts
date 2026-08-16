// =============================================
// SnapForge 文件校验与文件名清洗（纯函数，可被客户端/服务端共享）
// =============================================
// 统一三处 API 路由（upload / process / duplicates）使用的：
// - 允许类型白名单（仅位图，拒绝 SVG/PDF 等矢量）
// - 单文件大小上限
// - Magic Number 类型校验
// - 安全文件名清洗（含 Windows 保留设备名、前导点、全角反斜杠）
//
// 注意：本模块刻意不 import next/server，保证可被客户端组件安全引用。
// Content-Length 守卫见 src/lib/request-guard.ts（仅服务端）。

// 允许的图片类型（仅位图；SVG/PDF/AVIF 等矢量或未经验证格式一律拒绝）
export const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
] as const;

export type AllowedImageType = (typeof ALLOWED_TYPES)[number];

// 单文件最大 50MB（与 AGENTS.md 一致）
export const MAX_FILE_SIZE = 50 * 1024 * 1024;

// 各路由请求体上限（multipart 编码会比文件本身略大，留 5MB 余量）
export const MAX_UPLOAD_BODY_SIZE = 55 * 1024 * 1024; // upload：单文件 + 表单开销
export const MAX_PROCESS_BODY_SIZE = 55 * 1024 * 1024; // process：单文件 + config
export const MAX_DUPLICATES_BODY_SIZE = 105 * 1024 * 1024; // duplicates：多文件总量

// Windows 保留设备名（不含扩展名比对）
const WINDOWS_RESERVED_NAMES = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i;

/**
 * 清洗文件名，防止路径遍历 / 控制字符 / Windows 保留设备名 / 前导点攻击。
 * 保留中文字符（CJK），其余不可信字符统一替换为下划线。
 */
export function sanitizeFilename(filename: string): string {
  let safe = String(filename || '');

  // 1. Unicode NFC 规范化（防 NFC/NFD 攻击）
  safe = safe.normalize('NFC');

  // 2. 替换路径分隔符：正斜杠 / 反斜杠 / 全角反斜杠 / 全角正斜杠
  safe = safe.replace(/[\\/＼／]/g, '_');

  // 3. 移除路径遍历尝试
  safe = safe.replace(/\.\./g, '');

  // 4. 移除 Unicode 控制字符与危险字符
  safe = safe.replace(/[<>:"|?*\x00-\x1f\x7f]/g, '_');

  // 5. 空白归一
  safe = safe.trim().replace(/\s+/g, '_');

  // 6. 前导点处理（.env 等隐藏文件）
  safe = safe.replace(/^\.+/, '');

  // 7. 白名单兜底：仅保留 ASCII 字母数字、._- 以及 CJK 常用字符
  safe = safe.replace(/[^a-zA-Z0-9._\-\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef]/g, '_');

  // 8. Windows 保留设备名黑名单（CON / NUL / COM1-9 / LPT1-9 / PRN / AUX）
  const baseWithoutExt = safe.replace(/\.[^/.]+$/, '');
  if (WINDOWS_RESERVED_NAMES.test(baseWithoutExt)) {
    safe = `_${safe}`;
  }

  // 9. 限制长度（255 字符以内，避免文件系统限制）
  safe = safe.slice(0, 255);

  // 10. 确保非空且不是 "." / ".."
  if (!safe || safe === '.' || safe === '..') {
    safe = 'unnamed_image';
  }

  return safe;
}

/**
 * 通过 Magic Number 验证文件真实类型（与声明类型一致才返回 true）。
 * 支持：JPEG(FFD8FF)、PNG(89504E47)、GIF(47494638)、WebP(RIFF....WEBP)。
 */
export function validateFileType(buffer: Buffer, claimedType: string): boolean {
  if (!ALLOWED_TYPES.includes(claimedType as AllowedImageType)) return false;

  switch (claimedType) {
    case 'image/jpeg':
      return (
        buffer.length >= 3 &&
        buffer[0] === 0xff &&
        buffer[1] === 0xd8 &&
        buffer[2] === 0xff
      );
    case 'image/png':
      return buffer
        .slice(0, 8)
        .equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
    case 'image/gif':
      return buffer
        .slice(0, 4)
        .equals(Buffer.from([0x47, 0x49, 0x46, 0x38]));
    case 'image/webp':
      return (
        buffer.length >= 12 &&
        buffer.slice(0, 4).equals(Buffer.from([0x52, 0x49, 0x46, 0x46])) && // RIFF
        buffer.slice(8, 12).equals(Buffer.from([0x57, 0x45, 0x42, 0x50])) // WEBP
      );
    default:
      return false;
  }
}

/**
 * 从文件头推断图片 MIME 类型（不依赖客户端声明）。
 * 无法识别时返回 null。
 */
export function detectImageMime(buffer: Buffer): string | null {
  if (!buffer || buffer.length < 3) return null;

  if (buffer[0] === 0xff && buffer[1] === 0xd8 && buffer[2] === 0xff) {
    return 'image/jpeg';
  }
  if (
    buffer.length >= 8 &&
    buffer
      .slice(0, 8)
      .equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
  ) {
    return 'image/png';
  }
  if (
    buffer.length >= 4 &&
    buffer.slice(0, 4).equals(Buffer.from([0x47, 0x49, 0x46, 0x38]))
  ) {
    return 'image/gif';
  }
  if (
    buffer.length >= 12 &&
    buffer.slice(0, 4).equals(Buffer.from([0x52, 0x49, 0x46, 0x46])) &&
    buffer.slice(8, 12).equals(Buffer.from([0x57, 0x45, 0x42, 0x50]))
  ) {
    return 'image/webp';
  }
  return null;
}
