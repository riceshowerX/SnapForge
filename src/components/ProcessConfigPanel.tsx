'use client';

import { useAppStore } from '@/store';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  RotateCcw,
  Info,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Palette,
  Type,
  Frame,
  Crop,
  RotateCw,
  Maximize,
  Zap,
  FileText,
} from 'lucide-react';
import type {
  ImageFormat,
  ResizeMode,
  FilterType,
  WatermarkPosition,
} from '@/types';
import { useCallback, useState } from 'react';
import { t } from '@/lib/i18n';

// 可折叠配置组
function ConfigSection({
  title,
  icon,
  enabled,
  onToggle,
  children,
  tooltip,
  defaultExpanded = true,
}: {
  title: string;
  icon?: React.ReactNode;
  enabled?: boolean;
  onToggle?: (checked: boolean) => void;
  children: React.ReactNode;
  tooltip?: string;
  defaultExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className="border rounded-lg bg-card">
      <div
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          )}
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <span className="font-medium text-sm">{title}</span>
          {tooltip && (
            <Tooltip>
              <TooltipTrigger onClick={(e) => e.stopPropagation()}>
                <Info className="w-3.5 h-3.5 text-muted-foreground/60" />
              </TooltipTrigger>
              <TooltipContent side="right" className="max-w-[200px]">
                {tooltip}
              </TooltipContent>
            </Tooltip>
          )}
        </div>
        {onToggle !== undefined && (
          <div onClick={(e) => e.stopPropagation()}>
            <Switch checked={enabled} onCheckedChange={onToggle} />
          </div>
        )}
      </div>
      {expanded && (
        <div className="px-3 pb-3 pt-0 space-y-3 border-t">{children}</div>
      )}
    </div>
  );
}

// 数字输入组件
function NumberInput({
  label,
  value,
  onChange,
  min = 0,
  max,
  step = 1,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <div className="flex items-center gap-2">
        <Input
          type="number"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min}
          max={max}
          step={step}
          className="h-8 flex-1"
        />
        {suffix && <span className="text-xs text-muted-foreground">{suffix}</span>}
      </div>
    </div>
  );
}

// 滑块输入组件
function SliderInput({
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  showValue = true,
  suffix = '%',
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  showValue?: boolean;
  suffix?: string;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <Label className="text-xs text-muted-foreground">{label}</Label>
        {showValue && (
          <span className="text-xs font-medium">
            {value}
            {suffix}
          </span>
        )}
      </div>
      <Slider
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={([v]) => onChange(v)}
        className="py-2"
      />
    </div>
  );
}

export function ProcessConfigPanel() {
  const { config, updateConfig, resetConfig, language } = useAppStore();

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // 快速设置
  const applyQuickPreset = useCallback(
    (preset: 'web' | 'print' | 'thumbnail') => {
      switch (preset) {
        case 'web':
          updateConfig('convert', {
            enabled: true,
            format: 'webp',
            quality: 80,
            progressive: true,
            optimize: true,
          });
          updateConfig('resize', {
            ...config.resize,
            enabled: true,
            width: 1920,
            height: 1080,
            mode: 'contain',
            onlyShrink: true,
            aspectRatio: 'auto',
          });
          break;
        case 'print':
          updateConfig('convert', {
            enabled: true,
            format: 'tiff',
            quality: 100,
            progressive: false,
            optimize: false,
          });
          updateConfig('preserveMetadata', true);
          break;
        case 'thumbnail':
          updateConfig('resize', {
            ...config.resize,
            enabled: true,
            width: 200,
            height: 200,
            mode: 'cover',
            onlyShrink: true,
            aspectRatio: '1:1',
          });
          updateConfig('convert', {
            enabled: true,
            format: 'jpeg',
            quality: 75,
            progressive: false,
            optimize: true,
          });
          break;
      }
    },
    [config.resize, updateConfig]
  );

  return (
    <div className="space-y-3">
      {/* 快速预设 */}
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs flex-1"
          onClick={() => applyQuickPreset('web')}
        >
          <Zap className="w-3 h-3 mr-1" />
          {tr('quickWeb')}
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs flex-1"
          onClick={() => applyQuickPreset('thumbnail')}
        >
          <Maximize className="w-3 h-3 mr-1" />
          {tr('quickThumbnail')}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 px-0"
          onClick={resetConfig}
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="space-y-3 pr-2">
          {/* 格式转换 */}
          <ConfigSection
            title={tr('formatConversion')}
            icon={<FileText className="w-4 h-4" />}
            enabled={config.convert.enabled}
            onToggle={(checked) =>
              updateConfig('convert', { ...config.convert, enabled: checked })
            }
            tooltip={tr('formatConversion')}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('outputFormat')}
              </Label>
              <Select
                value={config.convert.format}
                onValueChange={(value) =>
                  updateConfig('convert', {
                    ...config.convert,
                    format: value as ImageFormat,
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="jpeg">{tr('optionJpeg')}</SelectItem>
                  <SelectItem value="png">{tr('optionPng')}</SelectItem>
                  <SelectItem value="webp">{tr('optionWebp')}</SelectItem>
                  <SelectItem value="avif">{tr('optionAvif')}</SelectItem>
                  <SelectItem value="tiff">{tr('optionTiff')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label={tr('quality')}
              value={config.convert.quality}
              onChange={(v) =>
                updateConfig('convert', { ...config.convert, quality: v })
              }
              min={1}
              max={100}
              suffix=""
            />

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">
                {tr('progressiveLoading')}
              </Label>
              <Switch
                checked={config.convert.progressive}
                onCheckedChange={(checked) =>
                  updateConfig('convert', {
                    ...config.convert,
                    progressive: checked,
                  })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">
                {tr('optimizeCompression')}
              </Label>
              <Switch
                checked={config.convert.optimize}
                onCheckedChange={(checked) =>
                  updateConfig('convert', {
                    ...config.convert,
                    optimize: checked,
                  })
                }
              />
            </div>
          </ConfigSection>

          {/* 尺寸调整 */}
          <ConfigSection
            title={tr('resize')}
            icon={<Maximize className="w-4 h-4" />}
            enabled={config.resize.enabled}
            onToggle={(checked) =>
              updateConfig('resize', { ...config.resize, enabled: checked })
            }
            tooltip={tr('resize')}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('fitMode')}
              </Label>
              <Select
                value={config.resize.mode}
                onValueChange={(value) =>
                  updateConfig('resize', {
                    ...config.resize,
                    mode: value as ResizeMode,
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="contain">{tr('optionContain')}</SelectItem>
                  <SelectItem value="cover">{tr('optionCover')}</SelectItem>
                  <SelectItem value="stretch">{tr('optionStretch')}</SelectItem>
                  <SelectItem value="fill">{tr('optionFill')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label={tr('cropWidth')}
                value={config.resize.width}
                onChange={(v) =>
                  updateConfig('resize', { ...config.resize, width: v })
                }
                suffix="px"
              />
              <NumberInput
                label={tr('cropHeight')}
                value={config.resize.height}
                onChange={(v) =>
                  updateConfig('resize', { ...config.resize, height: v })
                }
                suffix="px"
              />
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">
                {tr('onlyShrink')}
              </Label>
              <Switch
                checked={config.resize.onlyShrink}
                onCheckedChange={(checked) =>
                  updateConfig('resize', {
                    ...config.resize,
                    onlyShrink: checked,
                  })
                }
              />
            </div>
          </ConfigSection>

          {/* 裁剪 */}
          <ConfigSection
            title={tr('crop')}
            icon={<Crop className="w-4 h-4" />}
            enabled={config.crop.enabled}
            onToggle={(checked) =>
              updateConfig('crop', { ...config.crop, enabled: checked })
            }
            tooltip={tr('crop')}
            defaultExpanded={false}
          >
            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label={tr('cropX')}
                value={config.crop.x}
                onChange={(v) => updateConfig('crop', { ...config.crop, x: v })}
              />
              <NumberInput
                label={tr('cropY')}
                value={config.crop.y}
                onChange={(v) => updateConfig('crop', { ...config.crop, y: v })}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label={tr('cropWidth')}
                value={config.crop.width}
                onChange={(v) =>
                  updateConfig('crop', { ...config.crop, width: v })
                }
              />
              <NumberInput
                label={tr('cropHeight')}
                value={config.crop.height}
                onChange={(v) =>
                  updateConfig('crop', { ...config.crop, height: v })
                }
              />
            </div>
          </ConfigSection>

          {/* 旋转 */}
          <ConfigSection
            title={tr('rotateFlip')}
            icon={<RotateCw className="w-4 h-4" />}
            enabled={config.rotate.enabled}
            onToggle={(checked) =>
              updateConfig('rotate', { ...config.rotate, enabled: checked })
            }
            tooltip={tr('rotateFlip')}
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('rotationAngle')}
              </Label>
              <Select
                value={config.rotate.angle.toString()}
                onValueChange={(value) =>
                  updateConfig('rotate', {
                    ...config.rotate,
                    angle: parseInt(value, 10),
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">{tr('noRotation')}</SelectItem>
                  <SelectItem value="90">{tr('rotate90')}</SelectItem>
                  <SelectItem value="180">{tr('rotate180')}</SelectItem>
                  <SelectItem value="270">{tr('rotate270')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <Switch
                  checked={config.rotate.flip}
                  onCheckedChange={(checked) =>
                    updateConfig('rotate', { ...config.rotate, flip: checked })
                  }
                />
                <Label className="text-xs">{tr('flipVertical')}</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={config.rotate.flop}
                  onCheckedChange={(checked) =>
                    updateConfig('rotate', { ...config.rotate, flop: checked })
                  }
                />
                <Label className="text-xs">{tr('flipHorizontal')}</Label>
              </div>
            </div>
          </ConfigSection>

          {/* 滤镜 */}
          <ConfigSection
            title={tr('filters')}
            icon={<Palette className="w-4 h-4" />}
            enabled={config.filter.enabled}
            onToggle={(checked) =>
              updateConfig('filter', { ...config.filter, enabled: checked })
            }
            tooltip={tr('filters')}
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('filterType')}
              </Label>
              <Select
                value={config.filter.type}
                onValueChange={(value) =>
                  updateConfig('filter', {
                    ...config.filter,
                    type: value as FilterType,
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="grayscale">
                    {tr('filterGrayscale')}
                  </SelectItem>
                  <SelectItem value="sepia">{tr('filterSepia')}</SelectItem>
                  <SelectItem value="invert">{tr('filterInvert')}</SelectItem>
                  <SelectItem value="blur">{tr('filterBlur')}</SelectItem>
                  <SelectItem value="sharpen">{tr('filterSharpen')}</SelectItem>
                  <SelectItem value="emboss">{tr('filterEmboss')}</SelectItem>
                  <SelectItem value="edge">{tr('filterEdge')}</SelectItem>
                  <SelectItem value="vintage">{tr('filterVintage')}</SelectItem>
                  <SelectItem value="noir">{tr('filterNoir')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label={tr('intensity')}
              value={config.filter.intensity * 100}
              onChange={(v) =>
                updateConfig('filter', {
                  ...config.filter,
                  intensity: v / 100,
                })
              }
              min={0}
              max={100}
            />
          </ConfigSection>

          {/* 特效调整 */}
          <ConfigSection
            title={tr('colorAdjustment')}
            icon={<Sparkles className="w-4 h-4" />}
            enabled={config.effects.enabled}
            onToggle={(checked) =>
              updateConfig('effects', { ...config.effects, enabled: checked })
            }
            tooltip={tr('colorAdjustment')}
            defaultExpanded={false}
          >
            <SliderInput
              label={tr('brightness')}
              value={config.effects.brightness * 100}
              onChange={(v) =>
                updateConfig('effects', {
                  ...config.effects,
                  brightness: v / 100,
                })
              }
              min={0}
              max={200}
            />
            <SliderInput
              label={tr('contrast')}
              value={config.effects.contrast * 100}
              onChange={(v) =>
                updateConfig('effects', {
                  ...config.effects,
                  contrast: v / 100,
                })
              }
              min={0}
              max={200}
            />
            <SliderInput
              label={tr('saturation')}
              value={config.effects.saturation * 100}
              onChange={(v) =>
                updateConfig('effects', {
                  ...config.effects,
                  saturation: v / 100,
                })
              }
              min={0}
              max={200}
            />
            <SliderInput
              label={tr('sharpness')}
              value={config.effects.sharpness * 100}
              onChange={(v) =>
                updateConfig('effects', {
                  ...config.effects,
                  sharpness: v / 100,
                })
              }
              min={0}
              max={200}
            />
          </ConfigSection>

          {/* 水印 */}
          <ConfigSection
            title={tr('watermark')}
            icon={<Type className="w-4 h-4" />}
            enabled={config.watermark.enabled}
            onToggle={(checked) =>
              updateConfig('watermark', {
                ...config.watermark,
                enabled: checked,
              })
            }
            tooltip={tr('watermark')}
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('watermarkType')}
              </Label>
              <Select
                value={config.watermark.type}
                onValueChange={(value) =>
                  updateConfig('watermark', {
                    ...config.watermark,
                    type: value as 'text' | 'image',
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">{tr('textWatermark')}</SelectItem>
                  <SelectItem value="image">{tr('imageWatermark')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {config.watermark.type === 'text' && (
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  {tr('watermarkText')}
                </Label>
                <Input
                  value={config.watermark.text || ''}
                  onChange={(e) =>
                    updateConfig('watermark', {
                      ...config.watermark,
                      text: e.target.value,
                    })
                  }
                  placeholder={tr('watermarkTextPlaceholder')}
                  className="h-8"
                />
              </div>
            )}

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('position')}
              </Label>
              <Select
                value={config.watermark.position}
                onValueChange={(value) =>
                  updateConfig('watermark', {
                    ...config.watermark,
                    position: value as WatermarkPosition,
                  })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="top-left">{tr('posTopLeft')}</SelectItem>
                  <SelectItem value="top-center">
                    {tr('posTopCenter')}
                  </SelectItem>
                  <SelectItem value="top-right">{tr('posTopRight')}</SelectItem>
                  <SelectItem value="center-left">
                    {tr('posCenterLeft')}
                  </SelectItem>
                  <SelectItem value="center">{tr('posCenter')}</SelectItem>
                  <SelectItem value="center-right">
                    {tr('posCenterRight')}
                  </SelectItem>
                  <SelectItem value="bottom-left">
                    {tr('posBottomLeft')}
                  </SelectItem>
                  <SelectItem value="bottom-center">
                    {tr('posBottomCenter')}
                  </SelectItem>
                  <SelectItem value="bottom-right">
                    {tr('posBottomRight')}
                  </SelectItem>
                  <SelectItem value="tile">{tr('posTile')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label={tr('opacity')}
              value={config.watermark.opacity * 100}
              onChange={(v) =>
                updateConfig('watermark', {
                  ...config.watermark,
                  opacity: v / 100,
                })
              }
              min={1}
              max={100}
            />

            <NumberInput
              label={tr('fontSize')}
              value={config.watermark.fontSize}
              onChange={(v) =>
                updateConfig('watermark', {
                  ...config.watermark,
                  fontSize: v,
                })
              }
              suffix="px"
            />
          </ConfigSection>

          {/* 边框 */}
          <ConfigSection
            title={tr('border')}
            icon={<Frame className="w-4 h-4" />}
            enabled={config.border.enabled}
            onToggle={(checked) =>
              updateConfig('border', { ...config.border, enabled: checked })
            }
            tooltip={tr('border')}
            defaultExpanded={false}
          >
            <NumberInput
              label={tr('borderWidth')}
              value={config.border.width}
              onChange={(v) =>
                updateConfig('border', { ...config.border, width: v })
              }
              suffix="px"
            />

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('borderColor')}
              </Label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={config.border.color}
                  onChange={(e) =>
                    updateConfig('border', {
                      ...config.border,
                      color: e.target.value,
                    })
                  }
                  className="w-8 h-8 rounded border cursor-pointer"
                />
                <Input
                  value={config.border.color}
                  onChange={(e) =>
                    updateConfig('border', {
                      ...config.border,
                      color: e.target.value,
                    })
                  }
                  className="h-8 flex-1 font-mono text-xs"
                />
              </div>
            </div>
          </ConfigSection>

          {/* 重命名 */}
          <ConfigSection
            title={tr('rename')}
            icon={<FileText className="w-4 h-4" />}
            enabled={config.rename.enabled}
            onToggle={(checked) =>
              updateConfig('rename', { ...config.rename, enabled: checked })
            }
            tooltip={tr('rename')}
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                {tr('prefix')}
              </Label>
              <Input
                value={config.rename.prefix}
                onChange={(e) =>
                  updateConfig('rename', {
                    ...config.rename,
                    prefix: e.target.value,
                  })
                }
                placeholder="image"
                className="h-8"
              />
            </div>

            <NumberInput
              label={tr('startNumber')}
              value={config.rename.startNumber}
              onChange={(v) =>
                updateConfig('rename', { ...config.rename, startNumber: v })
              }
            />
          </ConfigSection>

          {/* 元数据 */}
          <div className="flex items-center justify-between p-3 border rounded-lg bg-card">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-muted-foreground" />
              <Label className="text-sm">{tr('preserveMetadata')}</Label>
            </div>
            <Switch
              checked={config.preserveMetadata}
              onCheckedChange={(checked) =>
                updateConfig('preserveMetadata', checked)
              }
            />
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
