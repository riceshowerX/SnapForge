// =============================================
// SnapForge 处理配置运行时校验（zod）
// =============================================
// 用途：
// - /api/process 路由：校验并深合并客户端传入的 ProcessConfig（Q-03）
// - SchemeManager 导入方案：safeParse 校验，畸形 JSON 不崩溃（S-06）
// - 数值范围统一收紧，避免 sharp 抛错 / 资源滥用

import { z } from 'zod';
import {
  ProcessConfig,
  defaultRenameConfig,
  defaultConvertConfig,
  defaultResizeConfig,
  defaultCropConfig,
  defaultRotateConfig,
  defaultFilterConfig,
  defaultWatermarkConfig,
  defaultEffectsConfig,
  defaultBorderConfig,
  defaultCompressionConfig,
  defaultProcessConfig,
} from '@/types';

// 各嵌套配置 schema（全部字段可选，缺失字段由深合并用默认值补齐）
const renameSchema = z.object({
  enabled: z.boolean().optional(),
  prefix: z.string().max(100).optional(),
  startNumber: z.number().int().min(0).max(1_000_000).optional(),
  namingTemplate: z.string().max(200).optional(),
});

const convertSchema = z.object({
  enabled: z.boolean().optional(),
  format: z
    .enum(['jpeg', 'jpg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'avif'])
    .optional(),
  quality: z.number().min(1).max(100).optional(),
  progressive: z.boolean().optional(),
  optimize: z.boolean().optional(),
});

const resizeSchema = z.object({
  enabled: z.boolean().optional(),
  width: z.number().min(0).max(10000).optional(), // 0 = 自动
  height: z.number().min(0).max(10000).optional(),
  mode: z.enum(['contain', 'cover', 'stretch', 'fill']).optional(),
  onlyShrink: z.boolean().optional(),
  aspectRatio: z.string().max(50).optional(),
});

const cropSchema = z.object({
  enabled: z.boolean().optional(),
  x: z.number().min(0).max(100000).optional(),
  y: z.number().min(0).max(100000).optional(),
  width: z.number().min(1).max(50000).optional(),
  height: z.number().min(1).max(50000).optional(),
  aspectRatio: z.string().max(50).optional(),
  preset: z
    .enum(['custom', 'square', '16:9', '4:3', '3:2', '2:1'])
    .optional(),
});

const rotateSchema = z.object({
  enabled: z.boolean().optional(),
  angle: z.number().min(-360).max(360).optional(),
  expand: z.boolean().optional(),
  fillColor: z.string().max(20).optional(),
  flip: z.boolean().optional(),
  flop: z.boolean().optional(),
});

const filterSchema = z.object({
  enabled: z.boolean().optional(),
  type: z
    .enum([
      'grayscale',
      'sepia',
      'invert',
      'blur',
      'sharpen',
      'emboss',
      'edge',
      'contrast',
      'brightness',
      'vintage',
      'cool',
      'warm',
      'dramatic',
      'noir',
    ])
    .optional(),
  intensity: z.number().min(0).max(100).optional(),
});

const watermarkSchema = z.object({
  enabled: z.boolean().optional(),
  type: z.enum(['text', 'image']).optional(),
  text: z.string().max(500).optional(),
  imageUrl: z
    .string()
    .max(2000)
    .refine(
      (url) => {
        // 第一道防线：仅允许 http(s) URL 格式
        try {
          const parsed = new URL(url);
          return parsed.protocol === 'http:' || parsed.protocol === 'https:';
        } catch {
          return false;
        }
      },
      { message: 'watermark.imageUrl must be a valid http(s) URL' }
    )
    .optional(),
  fontSize: z.number().min(1).max(500).optional(),
  color: z.string().max(20).optional(),
  opacity: z.number().min(0.01).max(1).optional(), // BUG-3：拒绝 0（透明水印无意义）
  position: z
    .enum([
      'top-left',
      'top-center',
      'top-right',
      'center-left',
      'center',
      'center-right',
      'bottom-left',
      'bottom-center',
      'bottom-right',
      'tile',
    ])
    .optional(),
  rotation: z.number().min(-360).max(360).optional(),
  margin: z.number().min(0).max(500).optional(),
  fontFamily: z.string().max(100).optional(),
  shadow: z.boolean().optional(),
  tileSpacing: z.number().min(0).max(2000).optional(),
});

const effectsSchema = z.object({
  enabled: z.boolean().optional(),
  brightness: z.number().min(0).max(10).optional(),
  contrast: z.number().min(0).max(10).optional(),
  saturation: z.number().min(0).max(10).optional(),
  sharpness: z.number().min(0).max(10).optional(),
  hue: z.number().min(-360).max(360).optional(),
  gamma: z.number().min(0.1).max(5).optional(),
  noise: z.number().min(0).max(100).optional(),
  vignette: z.number().min(0).max(100).optional(),
});

const borderSchema = z.object({
  enabled: z.boolean().optional(),
  width: z.number().min(0).max(500).optional(),
  color: z.string().max(20).optional(),
  radius: z.number().min(0).max(500).optional(),
  style: z.enum(['solid', 'double', 'rounded']).optional(),
});

const compressionSchema = z.object({
  enabled: z.boolean().optional(),
  mode: z.enum(['quality', 'size']).optional(),
  targetSize: z.number().min(1).max(100000).optional(), // 单位 KB
  quality: z.number().min(1).max(100).optional(),
  preserveMetadata: z.boolean().optional(),
});

/** ProcessConfig 完整校验 schema（顶层字段均可选，缺失由深合并兜底） */
export const processConfigSchema = z.object({
  rename: renameSchema.optional(),
  convert: convertSchema.optional(),
  resize: resizeSchema.optional(),
  crop: cropSchema.optional(),
  rotate: rotateSchema.optional(),
  filter: filterSchema.optional(),
  watermark: watermarkSchema.optional(),
  effects: effectsSchema.optional(),
  border: borderSchema.optional(),
  compression: compressionSchema.optional(),
  preserveMetadata: z.boolean().optional(),
});

export type ProcessConfigInput = z.infer<typeof processConfigSchema>;

/**
 * 将（已通过 safeParse 的）部分配置与默认配置做深合并，
 * 确保返回的 ProcessConfig 所有嵌套字段完整。
 */
export function deepMergeProcessConfig(
  partial: ProcessConfigInput | Record<string, unknown>
): ProcessConfig {
  const src = (partial || {}) as Record<string, unknown>;

  return {
    rename: { ...defaultRenameConfig, ...((src.rename as object) || {}) },
    convert: { ...defaultConvertConfig, ...((src.convert as object) || {}) },
    resize: { ...defaultResizeConfig, ...((src.resize as object) || {}) },
    crop: { ...defaultCropConfig, ...((src.crop as object) || {}) },
    rotate: { ...defaultRotateConfig, ...((src.rotate as object) || {}) },
    filter: { ...defaultFilterConfig, ...((src.filter as object) || {}) },
    watermark: {
      ...defaultWatermarkConfig,
      ...((src.watermark as object) || {}),
    },
    effects: { ...defaultEffectsConfig, ...((src.effects as object) || {}) },
    border: { ...defaultBorderConfig, ...((src.border as object) || {}) },
    compression: {
      ...defaultCompressionConfig,
      ...((src.compression as object) || {}),
    },
    preserveMetadata:
      typeof src.preserveMetadata === 'boolean'
        ? src.preserveMetadata
        : defaultProcessConfig.preserveMetadata,
  };
}
