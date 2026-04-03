'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Sparkles,
  Star,
  MoreVertical,
  Download,
  Upload,
  Trash2,
  FolderOpen,
  Check,
  Webhook,
  Image as ImageIcon,
  Palette,
  FileText,
  Heart,
  Plus
} from 'lucide-react';
import { ProcessingScheme, ProcessConfig, presetSchemes } from '@/types';
import { v4 as uuidv4 } from 'uuid';

interface SchemeManagerProps {
  currentConfig: ProcessConfig;
  onApplyScheme: (config: ProcessConfig) => void;
}

// 方案图标映射
const schemeIcons: Record<string, React.ReactNode> = {
  'web-optimized': <Webhook className="w-4 h-4" />,
  'thumbnail': <ImageIcon className="w-4 h-4" />,
  'social-media': <Heart className="w-4 h-4" />,
  'watermark-protect': <FileText className="w-4 h-4" />,
  'print-ready': <Palette className="w-4 h-4" />,
};

// localStorage 键名
const STORAGE_KEY = 'snapforge-schemes';

// 加载自定义方案的辅助函数
function loadCustomSchemes(): ProcessingScheme[] {
  if (typeof window === 'undefined') return [];
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved) as ProcessingScheme[];
    }
  } catch (e) {
    console.warn('Failed to load custom schemes:', e);
  }
  return [];
}

export function SchemeManager({ currentConfig, onApplyScheme }: SchemeManagerProps) {
  // 使用延迟初始化加载本地存储数据，避免水合不匹配
  const [schemes, setSchemes] = useState<ProcessingScheme[]>(() => [
    ...presetSchemes,
    ...loadCustomSchemes(),
  ]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newSchemeName, setNewSchemeName] = useState('');
  const [newSchemeDesc, setNewSchemeDesc] = useState('');

  // 保存自定义方案到 localStorage
  const saveCustomSchemes = useCallback((customSchemes: ProcessingScheme[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(customSchemes));
    } catch (e) {
      console.warn('Failed to save custom schemes:', e);
    }
  }, []);

  // 创建新方案
  const handleCreateScheme = () => {
    if (!newSchemeName.trim()) return;

    const newScheme: ProcessingScheme = {
      id: uuidv4(),
      name: newSchemeName.trim(),
      description: newSchemeDesc.trim() || '自定义处理方案',
      category: 'advanced',
      config: { ...currentConfig },
      createdAt: Date.now(),
      updatedAt: Date.now(),
      usageCount: 0,
    };

    const updatedSchemes = [...schemes, newScheme];
    setSchemes(updatedSchemes);
    saveCustomSchemes(updatedSchemes.filter(s => !presetSchemes.find(p => p.id === s.id)));
    
    setNewSchemeName('');
    setNewSchemeDesc('');
    setIsCreateDialogOpen(false);
  };

  // 应用方案
  const handleApplyScheme = (scheme: ProcessingScheme) => {
    onApplyScheme(scheme.config);
    // 更新使用次数
    const updatedSchemes = schemes.map(s => 
      s.id === scheme.id 
        ? { ...s, usageCount: (s.usageCount || 0) + 1 }
        : s
    );
    setSchemes(updatedSchemes);
  };

  // 删除方案
  const handleDeleteScheme = (id: string) => {
    const updatedSchemes = schemes.filter(s => s.id !== id);
    setSchemes(updatedSchemes);
    saveCustomSchemes(updatedSchemes.filter(s => !presetSchemes.find(p => p.id === s.id)));
  };

  // 导出方案
  const handleExportScheme = (scheme: ProcessingScheme) => {
    const data = JSON.stringify(scheme, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${scheme.name}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // 导入方案
  const handleImportScheme = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const scheme = JSON.parse(text) as ProcessingScheme;
      scheme.id = uuidv4();
      scheme.createdAt = Date.now();
      scheme.updatedAt = Date.now();
      
      const updatedSchemes = [...schemes, scheme];
      setSchemes(updatedSchemes);
      saveCustomSchemes(updatedSchemes.filter(s => !presetSchemes.find(p => p.id === s.id)));
    } catch (error) {
      console.error('Failed to import scheme:', error);
    }
    
    e.target.value = '';
  };

  // 切换收藏
  const toggleFavorite = (id: string) => {
    const updatedSchemes = schemes.map(s => 
      s.id === id ? { ...s, isFavorite: !s.isFavorite } : s
    );
    setSchemes(updatedSchemes);
    saveCustomSchemes(updatedSchemes.filter(s => !presetSchemes.find(p => p.id === s.id)));
  };

  // 统计启用的功能数
  const getEnabledFeatures = (config: ProcessConfig): string[] => {
    const features: string[] = [];
    if (config.convert.enabled) features.push('格式转换');
    if (config.resize.enabled) features.push('尺寸调整');
    if (config.crop.enabled) features.push('裁剪');
    if (config.rotate.enabled) features.push('旋转');
    if (config.filter.enabled) features.push('滤镜');
    if (config.watermark.enabled) features.push('水印');
    if (config.effects.enabled) features.push('特效');
    if (config.border.enabled) features.push('边框');
    if (config.compression.enabled) features.push('压缩');
    return features;
  };

  const presetSchemesList = schemes.filter(s => s.category === 'preset');
  const customSchemesList = schemes.filter(s => s.category !== 'preset');

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base">处理方案</CardTitle>
            <CardDescription className="text-xs mt-1">
              快速应用预设或自定义配置
            </CardDescription>
          </div>
          <div className="flex items-center gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <label className="cursor-pointer">
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImportScheme}
                    className="hidden"
                  />
                  <Button variant="ghost" size="icon" className="h-7 w-7" asChild>
                    <span>
                      <Upload className="w-3.5 h-3.5" />
                    </span>
                  </Button>
                </label>
              </TooltipTrigger>
              <TooltipContent>导入方案</TooltipContent>
            </Tooltip>

            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7">
                  <Plus className="w-3.5 h-3.5" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>保存当前配置</DialogTitle>
                  <DialogDescription>
                    将当前的处理配置保存为方案，方便下次使用
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">方案名称</label>
                    <Input
                      value={newSchemeName}
                      onChange={(e) => setNewSchemeName(e.target.value)}
                      placeholder="例如：电商产品图"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">描述（可选）</label>
                    <Textarea
                      value={newSchemeDesc}
                      onChange={(e) => setNewSchemeDesc(e.target.value)}
                      placeholder="描述此方案的用途..."
                      rows={3}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    取消
                  </Button>
                  <Button onClick={handleCreateScheme} disabled={!newSchemeName.trim()}>
                    保存
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <ScrollArea className="h-[350px] pr-2">
          <div className="space-y-4">
            {/* 预设方案 */}
            <div className="space-y-2">
              <h4 className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5" />
                推荐方案
              </h4>
              {presetSchemesList.map((scheme) => (
                <SchemeCard
                  key={scheme.id}
                  scheme={scheme}
                  icon={schemeIcons[scheme.id]}
                  onApply={() => handleApplyScheme(scheme)}
                  onExport={() => handleExportScheme(scheme)}
                  onToggleFavorite={() => toggleFavorite(scheme.id)}
                  features={getEnabledFeatures(scheme.config)}
                />
              ))}
            </div>

            {/* 自定义方案 */}
            {customSchemesList.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                  <FolderOpen className="w-3.5 h-3.5" />
                  我的方案
                </h4>
                {customSchemesList.map((scheme) => (
                  <SchemeCard
                    key={scheme.id}
                    scheme={scheme}
                    onApply={() => handleApplyScheme(scheme)}
                    onDelete={() => handleDeleteScheme(scheme.id)}
                    onExport={() => handleExportScheme(scheme)}
                    onToggleFavorite={() => toggleFavorite(scheme.id)}
                    features={getEnabledFeatures(scheme.config)}
                    isCustom
                  />
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

// 方案卡片组件
function SchemeCard({
  scheme,
  icon,
  onApply,
  onDelete,
  onExport,
  onToggleFavorite,
  features,
  isCustom = false,
}: {
  scheme: ProcessingScheme;
  icon?: React.ReactNode;
  onApply: () => void;
  onDelete?: () => void;
  onExport: () => void;
  onToggleFavorite: () => void;
  features: string[];
  isCustom?: boolean;
}) {
  const [applied, setApplied] = useState(false);

  const handleApply = () => {
    onApply();
    setApplied(true);
    setTimeout(() => setApplied(false), 1500);
  };

  return (
    <div className="p-3 rounded-lg border bg-muted/20 hover:bg-muted/30 transition-colors group">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {icon && <span className="text-primary">{icon}</span>}
            <span className="font-medium text-sm truncate">{scheme.name}</span>
            {scheme.isFavorite && (
              <Star className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" />
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
            {scheme.description}
          </p>
          {features.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {features.slice(0, 3).map((f, i) => (
                <Badge key={i} variant="secondary" className="text-[10px] h-4 px-1">
                  {f}
                </Badge>
              ))}
              {features.length > 3 && (
                <Badge variant="secondary" className="text-[10px] h-4 px-1">
                  +{features.length - 3}
                </Badge>
              )}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={onToggleFavorite}
          >
            <Star className={`w-3.5 h-3.5 ${scheme.isFavorite ? 'text-yellow-500 fill-yellow-500' : ''}`} />
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100">
                <MoreVertical className="w-3.5 h-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-32">
              <DropdownMenuItem onClick={handleApply}>
                <Check className="w-4 h-4 mr-2" />
                应用
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onExport}>
                <Download className="w-4 h-4 mr-2" />
                导出
              </DropdownMenuItem>
              {isCustom && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={onDelete} className="text-destructive">
                    <Trash2 className="w-4 h-4 mr-2" />
                    删除
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            size="sm"
            className="h-7 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={handleApply}
          >
            {applied ? (
              <>
                <Check className="w-3.5 h-3.5 mr-1" />
                已应用
              </>
            ) : (
              '应用'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
