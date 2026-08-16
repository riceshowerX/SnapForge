// =============================================
// SnapForge 类型定义 - 完整版
// =============================================

// 图像格式枚举
export type ImageFormat = 'jpeg' | 'jpg' | 'png' | 'webp' | 'gif' | 'bmp' | 'tiff' | 'avif';

// 缩放模式
export type ResizeMode = 'contain' | 'cover' | 'stretch' | 'fill';

// 滤镜类型
export type FilterType = 
  | 'grayscale' 
  | 'sepia' 
  | 'invert' 
  | 'blur' 
  | 'sharpen'
  | 'emboss'
  | 'edge'
  | 'contrast'
  | 'brightness'
  | 'vintage'
  | 'cool'
  | 'warm'
  | 'dramatic'
  | 'noir';

// 水印位置
export type WatermarkPosition = 
  | 'top-left' 
  | 'top-center' 
  | 'top-right'
  | 'center-left' 
  | 'center' 
  | 'center-right'
  | 'bottom-left' 
  | 'bottom-center' 
  | 'bottom-right'
  | 'tile';

// =============================================
// 配置接口
// =============================================

// 重命名配置
export interface RenameConfig {
  enabled: boolean;
  prefix: string;
  startNumber: number;
  namingTemplate: string;
}

// 格式转换配置
export interface ConvertConfig {
  enabled: boolean;
  format: ImageFormat;
  quality: number;
  progressive: boolean;
  optimize: boolean;
}

// 缩放配置
export interface ResizeConfig {
  enabled: boolean;
  width: number;
  height: number;
  mode: ResizeMode;
  onlyShrink: boolean;
  aspectRatio: string;
}

// 裁剪配置
export interface CropConfig {
  enabled: boolean;
  x: number;
  y: number;
  width: number;
  height: number;
  aspectRatio: string;
  preset: 'custom' | 'square' | '16:9' | '4:3' | '3:2' | '2:1';
}

// 旋转配置
export interface RotateConfig {
  enabled: boolean;
  angle: number;
  expand: boolean;
  fillColor?: string;
  flip: boolean;
  flop: boolean;
}

// 滤镜配置
export interface FilterConfig {
  enabled: boolean;
  type: FilterType;
  intensity: number;
}

// 水印配置
export interface WatermarkConfig {
  enabled: boolean;
  type: 'text' | 'image';
  text?: string;
  imageUrl?: string;
  fontSize: number;
  color: string;
  opacity: number;
  position: WatermarkPosition;
  rotation: number;
  margin: number;
  fontFamily: string;
  shadow: boolean;
  tileSpacing: number;
}

// 特效配置
export interface EffectsConfig {
  enabled: boolean;
  brightness: number;
  contrast: number;
  saturation: number;
  sharpness: number;
  hue: number;
  gamma: number;
  noise: number;
  vignette: number;
}

// 边框配置
export interface BorderConfig {
  enabled: boolean;
  width: number;
  color: string;
  radius: number;
  style: 'solid' | 'double' | 'rounded';
}

// 压缩配置
export interface CompressionConfig {
  enabled: boolean;
  mode: 'quality' | 'size';
  targetSize: number;
  quality: number;
  preserveMetadata: boolean;
}

// =============================================
// 主配置接口
// =============================================

export interface ProcessConfig {
  rename: RenameConfig;
  convert: ConvertConfig;
  resize: ResizeConfig;
  crop: CropConfig;
  rotate: RotateConfig;
  filter: FilterConfig;
  watermark: WatermarkConfig;
  effects: EffectsConfig;
  border: BorderConfig;
  compression: CompressionConfig;
  preserveMetadata: boolean;
}

// ProcessConfig 键类型
export type ProcessConfigKey = keyof ProcessConfig;

// =============================================
// 图像文件接口
// =============================================

export interface ImageFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  preview?: string;
  /** >2MB 图片的完整原始 base64（仅内存中短暂持有，写入 IndexedDB 后可清空） */
  originalDataUrl?: string;
  /** IndexedDB 中的原始 Blob key（优先于 originalDataUrl/preview 作为处理数据源） */
  blobKey?: string;
  width?: number;
  height?: number;
  /** 冗余字段：上传时置 true，UI 渲染一律以 selectedImageIds 为准 */
  selected: boolean;
  processed?: boolean;
  processedUrl?: string;
  error?: string;
  exif?: ExifData;
  hash?: string;
}

// EXIF 数据
export interface ExifData {
  make?: string;
  model?: string;
  software?: string;
  dateTime?: string;
  exposureTime?: string;
  fNumber?: number;
  iso?: number;
  focalLength?: number;
  gps?: {
    latitude?: number;
    longitude?: number;
  };
  orientation?: number;
  xResolution?: number;
  yResolution?: number;
  colorSpace?: string;
}

// 处理结果
export interface ProcessResult {
  id: string;
  originalName: string;
  status: 'pending' | 'processing' | 'success' | 'error';
  processedUrl?: string;
  error?: string;
  processingTime?: number;
  originalSize?: number;
  processedSize?: number;
}

// 批量处理任务
export interface BatchTask {
  id: string;
  name?: string;
  files: ImageFile[];
  config: ProcessConfig;
  results: ProcessResult[];
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  startTime?: number;
  endTime?: number;
  totalOriginalSize?: number;
  totalProcessedSize?: number;
}

// =============================================
// 处理方案/模板
// =============================================

export interface ProcessingScheme {
  id: string;
  name: string;
  description: string;
  /** 预设方案双语名称（可选；自定义方案无此字段时直接使用 name/description） */
  nameI18n?: { zh: string; en: string };
  descriptionI18n?: { zh: string; en: string };
  category: 'basic' | 'advanced' | 'preset';
  icon?: string;
  config: ProcessConfig;
  createdAt: number;
  updatedAt: number;
  isFavorite?: boolean;
  usageCount?: number;
}

// =============================================
// 重复图像检测
// =============================================

export interface DuplicateGroup {
  id: string;
  images: ImageFile[];
  similarity: number;
  hash?: string;
}

export interface DuplicateDetectionResult {
  groups: DuplicateGroup[];
  totalScanned: number;
  duplicatesFound: number;
}

// =============================================
// 统计数据
// =============================================

export interface ProcessingStats {
  totalProcessed: number;
  totalImages: number;
  totalSizeSaved: number;
  averageProcessingTime: number;
  successRate: number;
  mostUsedFeatures: { feature: string; count: number }[];
  processingHistory: {
    date: string;
    count: number;
  }[];
}

// =============================================
// 默认配置
// =============================================

export const defaultRenameConfig: RenameConfig = {
  enabled: false,
  prefix: 'image',
  startNumber: 1,
  namingTemplate: '{prefix}_{counter:04d}',
};

export const defaultConvertConfig: ConvertConfig = {
  enabled: false,
  format: 'jpeg',
  quality: 85,
  progressive: false,
  optimize: true,
};

export const defaultResizeConfig: ResizeConfig = {
  enabled: false,
  width: 800,
  height: 600,
  mode: 'contain',
  onlyShrink: true,
  aspectRatio: 'auto',
};

export const defaultCropConfig: CropConfig = {
  enabled: false,
  x: 0,
  y: 0,
  width: 100,
  height: 100,
  aspectRatio: 'auto',
  preset: 'custom',
};

export const defaultRotateConfig: RotateConfig = {
  enabled: false,
  angle: 0,
  expand: true,
  fillColor: '#ffffff',
  flip: false,
  flop: false,
};

export const defaultFilterConfig: FilterConfig = {
  enabled: false,
  type: 'grayscale',
  intensity: 1,
};

export const defaultWatermarkConfig: WatermarkConfig = {
  enabled: false,
  type: 'text',
  text: 'SnapForge',
  fontSize: 32,
  color: '#ffffff',
  opacity: 0.5,
  position: 'bottom-right',
  rotation: 0,
  margin: 20,
  fontFamily: 'Arial',
  shadow: true,
  tileSpacing: 100,
};

export const defaultEffectsConfig: EffectsConfig = {
  enabled: false,
  brightness: 1,
  contrast: 1,
  saturation: 1,
  sharpness: 1,
  hue: 0,
  gamma: 1,
  noise: 0,
  vignette: 0,
};

export const defaultBorderConfig: BorderConfig = {
  enabled: false,
  width: 5,
  color: '#ffffff',
  radius: 0,
  style: 'solid',
};

export const defaultCompressionConfig: CompressionConfig = {
  enabled: false,
  mode: 'quality',
  targetSize: 500,
  quality: 80,
  preserveMetadata: false,
};

export const defaultProcessConfig: ProcessConfig = {
  rename: defaultRenameConfig,
  convert: defaultConvertConfig,
  resize: defaultResizeConfig,
  crop: defaultCropConfig,
  rotate: defaultRotateConfig,
  filter: defaultFilterConfig,
  watermark: defaultWatermarkConfig,
  effects: defaultEffectsConfig,
  border: defaultBorderConfig,
  compression: defaultCompressionConfig,
  preserveMetadata: true,
};

// =============================================
// 预设处理方案
// =============================================

export const presetSchemes: ProcessingScheme[] = [
  {
    id: 'web-optimized',
    name: 'Web 优化',
    description: '适合网页展示，压缩体积同时保持质量',
    nameI18n: { zh: 'Web 优化', en: 'Web Optimized' },
    descriptionI18n: {
      zh: '适合网页展示，压缩体积同时保持质量',
      en: 'Optimized for web display: smaller size while keeping quality',
    },
    category: 'preset',
    config: {
      ...defaultProcessConfig,
      convert: { enabled: true, format: 'webp', quality: 80, progressive: true, optimize: true },
      resize: { ...defaultResizeConfig, enabled: true, width: 1920, height: 1080, mode: 'contain', onlyShrink: true, aspectRatio: 'auto' },
      compression: { enabled: true, mode: 'quality', targetSize: 500, quality: 80, preserveMetadata: false },
    },
    createdAt: Date.now(),
    updatedAt: Date.now(),
    isFavorite: true,
    usageCount: 0,
  },
  {
    id: 'thumbnail',
    name: '缩略图生成',
    description: '快速生成小尺寸缩略图',
    nameI18n: { zh: '缩略图生成', en: 'Thumbnail' },
    descriptionI18n: {
      zh: '快速生成小尺寸缩略图',
      en: 'Quickly generate small-size thumbnails',
    },
    category: 'preset',
    config: {
      ...defaultProcessConfig,
      resize: { enabled: true, width: 200, height: 200, mode: 'cover', onlyShrink: true, aspectRatio: '1:1' },
      convert: { enabled: true, format: 'jpeg', quality: 75, progressive: false, optimize: true },
    },
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
  },
  {
    id: 'social-media',
    name: '社交媒体',
    description: '适合 Instagram、微博等社交平台',
    nameI18n: { zh: '社交媒体', en: 'Social Media' },
    descriptionI18n: {
      zh: '适合 Instagram、微博等社交平台',
      en: 'Optimized for Instagram, Weibo and other social platforms',
    },
    category: 'preset',
    config: {
      ...defaultProcessConfig,
      resize: { enabled: true, width: 1080, height: 1080, mode: 'cover', onlyShrink: false, aspectRatio: '1:1' },
      convert: { enabled: true, format: 'jpeg', quality: 90, progressive: true, optimize: true },
    },
    createdAt: Date.now(),
    updatedAt: Date.now(),
    isFavorite: true,
    usageCount: 0,
  },
  {
    id: 'watermark-protect',
    name: '水印保护',
    description: '添加防伪水印，保护原创图片',
    nameI18n: { zh: '水印保护', en: 'Watermark Protect' },
    descriptionI18n: {
      zh: '添加防伪水印，保护原创图片',
      en: 'Add anti-counterfeit watermark to protect original images',
    },
    category: 'preset',
    config: {
      ...defaultProcessConfig,
      watermark: {
        enabled: true,
        type: 'text',
        text: '© SnapForge',
        fontSize: 48,
        color: '#ffffff',
        opacity: 0.3,
        position: 'tile',
        rotation: -30,
        margin: 20,
        fontFamily: 'Arial',
        shadow: true,
        tileSpacing: 150,
      },
    },
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
  },
  {
    id: 'print-ready',
    name: '印刷准备',
    description: '高分辨率输出，适合打印',
    nameI18n: { zh: '印刷准备', en: 'Print Ready' },
    descriptionI18n: {
      zh: '高分辨率输出，适合打印',
      en: 'High-resolution output for printing',
    },
    category: 'preset',
    config: {
      ...defaultProcessConfig,
      convert: { enabled: true, format: 'tiff', quality: 100, progressive: false, optimize: false },
      effects: { enabled: true, brightness: 1.02, contrast: 1.05, saturation: 1, sharpness: 1.2, hue: 0, gamma: 1, noise: 0, vignette: 0 },
      preserveMetadata: true,
    },
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
  },
];

// =============================================
// 工具函数
// =============================================

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(0)}s`;
}
