'use client';

import { useAppStore } from '@/store';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
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
  FileText
} from 'lucide-react';
import type { ImageFormat, ResizeMode, FilterType, WatermarkPosition } from '@/types';
import { useState, useCallback } from 'react';

// 可折叠配置组
function ConfigSection({ 
  title, 
  icon,
  enabled, 
  onToggle, 
  children,
  tooltip,
  defaultExpanded = true
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
              <TooltipContent side="right" className="max-w-[200px]">{tooltip}</TooltipContent>
            </Tooltip>
          )}
        </div>
        {onToggle !== undefined && (
          <div onClick={(e) => e.stopPropagation()}>
            <Switch
              checked={enabled}
              onCheckedChange={onToggle}
            />
          </div>
        )}
      </div>
      {expanded && (
        <div className="px-3 pb-3 pt-0 space-y-3 border-t">
          {children}
        </div>
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
  suffix 
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
  suffix = '%'
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
            {value}{suffix}
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
  const { config, updateConfig, resetConfig } = useAppStore();

  // 快速设置
  const applyQuickPreset = useCallback((preset: 'web' | 'print' | 'thumbnail') => {
    switch (preset) {
      case 'web':
        updateConfig('convert', { enabled: true, format: 'webp', quality: 80, progressive: true, optimize: true });
        updateConfig('resize', { ...config.resize, enabled: true, width: 1920, height: 1080, mode: 'contain', onlyShrink: true, aspectRatio: 'auto' });
        break;
      case 'print':
        updateConfig('convert', { enabled: true, format: 'tiff', quality: 100, progressive: false, optimize: false });
        updateConfig('preserveMetadata', true);
        break;
      case 'thumbnail':
        updateConfig('resize', { ...config.resize, enabled: true, width: 200, height: 200, mode: 'cover', onlyShrink: true, aspectRatio: '1:1' });
        updateConfig('convert', { enabled: true, format: 'jpeg', quality: 75, progressive: false, optimize: true });
        break;
    }
  }, [config.resize, updateConfig]);

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
          Web优化
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs flex-1"
          onClick={() => applyQuickPreset('thumbnail')}
        >
          <Maximize className="w-3 h-3 mr-1" />
          缩略图
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
            title="格式转换"
            icon={<FileText className="w-4 h-4" />}
            enabled={config.convert.enabled}
            onToggle={(checked) => updateConfig('convert', { ...config.convert, enabled: checked })}
            tooltip="将图片转换为指定格式，支持质量控制"
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">输出格式</Label>
              <Select
                value={config.convert.format}
                onValueChange={(value) => 
                  updateConfig('convert', { ...config.convert, format: value as ImageFormat })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="jpeg">JPEG - 通用格式</SelectItem>
                  <SelectItem value="png">PNG - 无损压缩</SelectItem>
                  <SelectItem value="webp">WebP - 现代格式</SelectItem>
                  <SelectItem value="avif">AVIF - 高压缩比</SelectItem>
                  <SelectItem value="tiff">TIFF - 印刷质量</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label="质量"
              value={config.convert.quality}
              onChange={(v) => updateConfig('convert', { ...config.convert, quality: v })}
              min={1}
              max={100}
            />

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">渐进式加载</Label>
              <Switch
                checked={config.convert.progressive}
                onCheckedChange={(checked) => 
                  updateConfig('convert', { ...config.convert, progressive: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">优化压缩</Label>
              <Switch
                checked={config.convert.optimize}
                onCheckedChange={(checked) => 
                  updateConfig('convert', { ...config.convert, optimize: checked })
                }
              />
            </div>
          </ConfigSection>

          {/* 尺寸调整 */}
          <ConfigSection
            title="尺寸调整"
            icon={<Maximize className="w-4 h-4" />}
            enabled={config.resize.enabled}
            onToggle={(checked) => updateConfig('resize', { ...config.resize, enabled: checked })}
            tooltip="调整图片尺寸，支持多种缩放模式"
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">缩放模式</Label>
              <Select
                value={config.resize.mode}
                onValueChange={(value) => 
                  updateConfig('resize', { ...config.resize, mode: value as ResizeMode })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="contain">适应 - 保持比例</SelectItem>
                  <SelectItem value="cover">填充 - 裁剪适应</SelectItem>
                  <SelectItem value="stretch">拉伸 - 忽略比例</SelectItem>
                  <SelectItem value="fill">内部 - 完全包含</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label="宽度"
                value={config.resize.width}
                onChange={(v) => updateConfig('resize', { ...config.resize, width: v })}
                suffix="px"
              />
              <NumberInput
                label="高度"
                value={config.resize.height}
                onChange={(v) => updateConfig('resize', { ...config.resize, height: v })}
                suffix="px"
              />
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">仅缩小不放大</Label>
              <Switch
                checked={config.resize.onlyShrink}
                onCheckedChange={(checked) => 
                  updateConfig('resize', { ...config.resize, onlyShrink: checked })
                }
              />
            </div>
          </ConfigSection>

          {/* 裁剪 */}
          <ConfigSection
            title="裁剪"
            icon={<Crop className="w-4 h-4" />}
            enabled={config.crop.enabled}
            onToggle={(checked) => updateConfig('crop', { ...config.crop, enabled: checked })}
            tooltip="裁剪图片指定区域"
            defaultExpanded={false}
          >
            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label="X 起点"
                value={config.crop.x}
                onChange={(v) => updateConfig('crop', { ...config.crop, x: v })}
              />
              <NumberInput
                label="Y 起点"
                value={config.crop.y}
                onChange={(v) => updateConfig('crop', { ...config.crop, y: v })}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <NumberInput
                label="宽度"
                value={config.crop.width}
                onChange={(v) => updateConfig('crop', { ...config.crop, width: v })}
              />
              <NumberInput
                label="高度"
                value={config.crop.height}
                onChange={(v) => updateConfig('crop', { ...config.crop, height: v })}
              />
            </div>
          </ConfigSection>

          {/* 旋转 */}
          <ConfigSection
            title="旋转与翻转"
            icon={<RotateCw className="w-4 h-4" />}
            enabled={config.rotate.enabled}
            onToggle={(checked) => updateConfig('rotate', { ...config.rotate, enabled: checked })}
            tooltip="旋转或翻转图片"
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">旋转角度</Label>
              <Select
                value={config.rotate.angle.toString()}
                onValueChange={(value) => 
                  updateConfig('rotate', { ...config.rotate, angle: parseInt(value) })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">不旋转</SelectItem>
                  <SelectItem value="90">顺时针 90°</SelectItem>
                  <SelectItem value="180">180°</SelectItem>
                  <SelectItem value="270">顺时针 270°</SelectItem>
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
                <Label className="text-xs">垂直翻转</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={config.rotate.flop}
                  onCheckedChange={(checked) => 
                    updateConfig('rotate', { ...config.rotate, flop: checked })
                  }
                />
                <Label className="text-xs">水平翻转</Label>
              </div>
            </div>
          </ConfigSection>

          {/* 滤镜 */}
          <ConfigSection
            title="滤镜效果"
            icon={<Palette className="w-4 h-4" />}
            enabled={config.filter.enabled}
            onToggle={(checked) => updateConfig('filter', { ...config.filter, enabled: checked })}
            tooltip="应用预设滤镜效果"
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">滤镜类型</Label>
              <Select
                value={config.filter.type}
                onValueChange={(value) => 
                  updateConfig('filter', { ...config.filter, type: value as FilterType })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="grayscale">灰度</SelectItem>
                  <SelectItem value="sepia">复古棕褐</SelectItem>
                  <SelectItem value="invert">反色</SelectItem>
                  <SelectItem value="blur">模糊</SelectItem>
                  <SelectItem value="sharpen">锐化</SelectItem>
                  <SelectItem value="emboss">浮雕</SelectItem>
                  <SelectItem value="edge">边缘检测</SelectItem>
                  <SelectItem value="vintage">复古</SelectItem>
                  <SelectItem value="noir">黑白电影</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label="强度"
              value={config.filter.intensity * 100}
              onChange={(v) => updateConfig('filter', { ...config.filter, intensity: v / 100 })}
              min={0}
              max={100}
            />
          </ConfigSection>

          {/* 特效调整 */}
          <ConfigSection
            title="色彩调整"
            icon={<Sparkles className="w-4 h-4" />}
            enabled={config.effects.enabled}
            onToggle={(checked) => updateConfig('effects', { ...config.effects, enabled: checked })}
            tooltip="精细调整亮度、对比度等参数"
            defaultExpanded={false}
          >
            <SliderInput
              label="亮度"
              value={config.effects.brightness * 100}
              onChange={(v) => updateConfig('effects', { ...config.effects, brightness: v / 100 })}
              min={0}
              max={200}
              suffix="%"
            />
            <SliderInput
              label="对比度"
              value={config.effects.contrast * 100}
              onChange={(v) => updateConfig('effects', { ...config.effects, contrast: v / 100 })}
              min={0}
              max={200}
              suffix="%"
            />
            <SliderInput
              label="饱和度"
              value={config.effects.saturation * 100}
              onChange={(v) => updateConfig('effects', { ...config.effects, saturation: v / 100 })}
              min={0}
              max={200}
              suffix="%"
            />
            <SliderInput
              label="锐度"
              value={config.effects.sharpness * 100}
              onChange={(v) => updateConfig('effects', { ...config.effects, sharpness: v / 100 })}
              min={0}
              max={200}
              suffix="%"
            />
          </ConfigSection>

          {/* 水印 */}
          <ConfigSection
            title="水印"
            icon={<Type className="w-4 h-4" />}
            enabled={config.watermark.enabled}
            onToggle={(checked) => updateConfig('watermark', { ...config.watermark, enabled: checked })}
            tooltip="添加文本或图片水印"
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">水印类型</Label>
              <Select
                value={config.watermark.type}
                onValueChange={(value) => 
                  updateConfig('watermark', { ...config.watermark, type: value as 'text' | 'image' })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">文本水印</SelectItem>
                  <SelectItem value="image">图片水印</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {config.watermark.type === 'text' && (
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">水印文字</Label>
                <Input
                  value={config.watermark.text || ''}
                  onChange={(e) => 
                    updateConfig('watermark', { ...config.watermark, text: e.target.value })
                  }
                  placeholder="输入水印文字"
                  className="h-8"
                />
              </div>
            )}

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">位置</Label>
              <Select
                value={config.watermark.position}
                onValueChange={(value) => 
                  updateConfig('watermark', { ...config.watermark, position: value as WatermarkPosition })
                }
              >
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="top-left">左上角</SelectItem>
                  <SelectItem value="top-center">顶部居中</SelectItem>
                  <SelectItem value="top-right">右上角</SelectItem>
                  <SelectItem value="center-left">左侧居中</SelectItem>
                  <SelectItem value="center">正中心</SelectItem>
                  <SelectItem value="center-right">右侧居中</SelectItem>
                  <SelectItem value="bottom-left">左下角</SelectItem>
                  <SelectItem value="bottom-center">底部居中</SelectItem>
                  <SelectItem value="bottom-right">右下角</SelectItem>
                  <SelectItem value="tile">平铺</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <SliderInput
              label="透明度"
              value={config.watermark.opacity * 100}
              onChange={(v) => updateConfig('watermark', { ...config.watermark, opacity: v / 100 })}
              min={0}
              max={100}
            />

            <NumberInput
              label="字体大小"
              value={config.watermark.fontSize}
              onChange={(v) => updateConfig('watermark', { ...config.watermark, fontSize: v })}
              suffix="px"
            />
          </ConfigSection>

          {/* 边框 */}
          <ConfigSection
            title="边框"
            icon={<Frame className="w-4 h-4" />}
            enabled={config.border.enabled}
            onToggle={(checked) => updateConfig('border', { ...config.border, enabled: checked })}
            tooltip="为图片添加边框"
            defaultExpanded={false}
          >
            <NumberInput
              label="边框宽度"
              value={config.border.width}
              onChange={(v) => updateConfig('border', { ...config.border, width: v })}
              suffix="px"
            />

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">边框颜色</Label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={config.border.color}
                  onChange={(e) => 
                    updateConfig('border', { ...config.border, color: e.target.value })
                  }
                  className="w-8 h-8 rounded border cursor-pointer"
                />
                <Input
                  value={config.border.color}
                  onChange={(e) => 
                    updateConfig('border', { ...config.border, color: e.target.value })
                  }
                  className="h-8 flex-1 font-mono text-xs"
                />
              </div>
            </div>
          </ConfigSection>

          {/* 重命名 */}
          <ConfigSection
            title="智能重命名"
            icon={<FileText className="w-4 h-4" />}
            enabled={config.rename.enabled}
            onToggle={(checked) => updateConfig('rename', { ...config.rename, enabled: checked })}
            tooltip="批量重命名输出文件"
            defaultExpanded={false}
          >
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">文件名前缀</Label>
              <Input
                value={config.rename.prefix}
                onChange={(e) => 
                  updateConfig('rename', { ...config.rename, prefix: e.target.value })
                }
                placeholder="image"
                className="h-8"
              />
            </div>

            <NumberInput
              label="起始编号"
              value={config.rename.startNumber}
              onChange={(v) => updateConfig('rename', { ...config.rename, startNumber: v })}
            />
          </ConfigSection>

          {/* 元数据 */}
          <div className="flex items-center justify-between p-3 border rounded-lg bg-card">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-muted-foreground" />
              <Label className="text-sm">保留元数据</Label>
            </div>
            <Switch
              checked={config.preserveMetadata}
              onCheckedChange={(checked) => updateConfig('preserveMetadata', checked)}
            />
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
