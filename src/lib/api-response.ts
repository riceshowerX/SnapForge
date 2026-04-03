// =============================================
// SnapForge API 响应格式统一工具
// =============================================

// 统一的 API 响应接口
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: number;
}

// 错误码枚举
export const ErrorCodes = {
  // 通用错误 (1xxx)
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  INVALID_REQUEST: 'INVALID_REQUEST',
  MISSING_FIELD: 'MISSING_FIELD',
  
  // 文件相关错误 (2xxx)
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_SIGNATURE_MISMATCH: 'FILE_SIGNATURE_MISMATCH',
  NO_FILE_PROVIDED: 'NO_FILE_PROVIDED',
  REQUEST_BODY_TOO_LARGE: 'REQUEST_BODY_TOO_LARGE',
  
  // 配置相关错误 (3xxx)
  INVALID_CONFIG: 'INVALID_CONFIG',
  CONFIG_TOO_LARGE: 'CONFIG_TOO_LARGE',
  CONFIG_PARAMS_OUT_OF_RANGE: 'CONFIG_PARAMS_OUT_OF_RANGE',
  INVALID_JSON: 'INVALID_JSON',
  
  // 业务逻辑错误 (4xxx)
  NO_IMAGES_SELECTED: 'NO_IMAGES_SELECTED',
  TOO_MANY_FILES: 'TOO_MANY_FILES',
  TOTAL_SIZE_EXCEEDED: 'TOTAL_SIZE_EXCEEDED',
  INVALID_THRESHOLD: 'INVALID_THRESHOLD',
  
  // 处理错误 (5xxx)
  PROCESSING_FAILED: 'PROCESSING_FAILED',
  DETECTION_FAILED: 'DETECTION_FAILED',
  
  // 限流错误 (6xxx)
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  
  // 服务器错误 (9xxx)
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;

export type ErrorCode = typeof ErrorCodes[keyof typeof ErrorCodes];

// 创建成功响应
export function successResponse<T>(data: T): ApiResponse<T> {
  return {
    success: true,
    data,
    timestamp: Date.now(),
  };
}

// 创建错误响应
export function errorResponse(
  code: ErrorCode,
  message: string,
  details?: Record<string, unknown>
): ApiResponse<never> {
  return {
    success: false,
    error: {
      code,
      message,
      details,
    },
    timestamp: Date.now(),
  };
}
