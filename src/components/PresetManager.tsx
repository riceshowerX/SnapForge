'use client';

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { 
  Save, 
  Trash2, 
  Download, 
  Check, 
  FolderOpen
} from 'lucide-react';
import { ProcessConfig, defaultProcessConfig } from '@/types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface Preset {
  id: string;
  name: string;
  config: ProcessConfig;
  createdAt: number;
}

// 本地存储 key
const PRESETS_KEY = 'snapforge-presets';

function loadPresets(): Preset[] {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem(PRESETS_KEY);
  return stored ? JSON.parse(stored) : [];
}

function savePresets(presets: Preset[]) {
  localStorage.setItem(PRESETS_KEY, JSON.stringify(presets));
}

export function PresetManager() {
  const { config, updateConfig } = useAppStore();
  const [presets, setPresets] = useState<Preset[]>(loadPresets);
  const [newPresetName, setNewPresetName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  const handleSavePreset = () => {
    if (!newPresetName.trim()) return;
    
    const newPreset: Preset = {
      id: Date.now().toString(),
      name: newPresetName.trim(),
      config: JSON.parse(JSON.stringify(config)),
      createdAt: Date.now(),
    };

    const newPresets = [...presets, newPreset];
    setPresets(newPresets);
    savePresets(newPresets);
    setNewPresetName('');
    setShowSaveDialog(false);
  };

  const handleLoadPreset = (preset: Preset) => {
    // 更新所有配置
    Object.keys(preset.config).forEach((key) => {
      updateConfig(key as keyof ProcessConfig, preset.config[key as keyof ProcessConfig]);
    });
  };

  const handleDeletePreset = (id: string) => {
    const newPresets = presets.filter(p => p.id !== id);
    setPresets(newPresets);
    savePresets(newPresets);
  };

  const handleExportPresets = () => {
    const data = JSON.stringify(presets, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `snapforge-presets-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportPresets = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const imported = JSON.parse(event.target?.result as string);
        if (Array.isArray(imported)) {
          const newPresets = [...presets, ...imported];
          setPresets(newPresets);
          savePresets(newPresets);
        }
      } catch (error) {
        console.error('Failed to import presets:', error);
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <div className="p-3 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm">配置预设</h3>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={handleExportPresets}
            title="导出预设"
          >
            <Download className="w-3.5 h-3.5" />
          </Button>
          <label className="cursor-pointer">
            <input
              type="file"
              accept=".json"
              onChange={handleImportPresets}
              className="hidden"
            />
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              asChild
            >
              <span title="导入预设">
                <FolderOpen className="w-3.5 h-3.5" />
              </span>
            </Button>
          </label>
        </div>
      </div>

      {/* 保存当前配置 */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="w-full h-8">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            保存当前配置
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle className="text-sm">保存配置预设</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Input
              placeholder="输入预设名称"
              value={newPresetName}
              onChange={(e) => setNewPresetName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSavePreset()}
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setShowSaveDialog(false)}>
                取消
              </Button>
              <Button size="sm" onClick={handleSavePreset}>
                保存
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 预设列表 */}
      <div className="space-y-2">
        {presets.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground text-xs">
            <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>暂无保存的预设</p>
            <p className="mt-1">配置好参数后点击保存</p>
          </div>
        ) : (
          presets.map((preset) => (
            <Card key={preset.id} className="p-2.5 group">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{preset.name}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {new Date(preset.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0"
                    onClick={() => handleLoadPreset(preset)}
                    title="应用预设"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0 text-destructive hover:text-destructive"
                    onClick={() => handleDeletePreset(preset.id)}
                    title="删除预设"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* 快速预设 */}
      <div className="pt-2 border-t">
        <p className="text-xs text-muted-foreground mb-2">快速预设</p>
        <div className="flex flex-wrap gap-1">
          {[
            { name: 'WebP优化', config: { convert: { enabled: true, format: 'webp', quality: 80 }, resize: { enabled: true, width: 1920, height: 1080, mode: 'contain' as const } } },
            { name: '缩略图', config: { resize: { enabled: true, width: 200, height: 200, mode: 'cover' as const } } },
            { name: '灰度滤镜', config: { filter: { enabled: true, type: 'grayscale' as const } } },
          ].map((quick, i) => (
            <Button
              key={i}
              variant="outline"
              size="sm"
              className="h-6 px-2 text-[11px]"
              onClick={() => {
                // 应用快速预设
                Object.entries(quick.config).forEach(([key, value]) => {
                  const defaultValue = defaultProcessConfig[key as keyof ProcessConfig];
                  if (typeof defaultValue === 'object' && defaultValue !== null && typeof value === 'object' && value !== null) {
                    updateConfig(key as keyof ProcessConfig, { 
                      ...defaultValue,
                      ...value 
                    } as ProcessConfig[keyof ProcessConfig]);
                  }
                });
              }}
            >
              {quick.name}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
