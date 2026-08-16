'use client';

import { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { ImageUploader } from '@/components/ImageUploader';
import { ProcessConfigPanel } from '@/components/ProcessConfigPanel';
import { ProcessingPanel } from '@/components/ProcessingPanel';
import { DuplicateDetector } from '@/components/DuplicateDetector';
import { ImagePreview } from '@/components/ImagePreview';
import { ProcessingHistory } from '@/components/ProcessingHistory';
import { ThemeToggle } from '@/components/ThemeToggle';
import { ExifPanel } from '@/components/ExifPanel';
import { SchemeManager } from '@/components/SchemeManager';
import { StatsDashboard } from '@/components/StatsDashboard';
import { useAppStore } from '@/store';
import type { ProcessConfigKey } from '@/types';
import { t } from '@/lib/i18n';
import {
  Image as ImageIcon,
  Zap,
  Github,
  Sparkles,
  Upload,
  Wand2,
  History,
  Settings2,
  PanelRightClose,
  PanelRightOpen,
  Keyboard,
  Copy,
  FileImage,
  Layers,
  BarChart2,
  Info,
  X,
  ChevronRight,
  BookOpen,
  Lightbulb,
  Globe,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function Home() {
  const { images, selectedImageIds, config, updateConfig, language, setLanguage } =
    useAppStore();
  const [activeTab, setActiveTab] = useState('upload');
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [rightPanelTab, setRightPanelTab] = useState<
    'config' | 'preview' | 'schemes' | 'history' | 'stats'
  >('config');
  // 默认隐藏 Welcome Banner，客户端加载后根据 localStorage 决定是否显示
  const [showWelcome, setShowWelcome] = useState(false);

  // 获取翻译的便捷函数
  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // 客户端挂载后从 localStorage 读取欢迎弹窗状态
  // 注意：这里在 effect 中设置 state 是 Next.js 推荐的 hydration 修复模式
  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('snapforge-welcome-seen');
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setShowWelcome(!hasSeenWelcome);
  }, []);

  // Q-05：语言切换时动态更新 <html lang>（SEO / 无障碍）
  useEffect(() => {
    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
  }, [language]);

  const selectedCount = selectedImageIds.length;
  const totalCount = images.length;

  const dismissWelcome = () => {
    setShowWelcome(false);
    localStorage.setItem('snapforge-welcome-seen', 'true');
  };

  // 快捷键提示
  const shortcuts = [
    { key: 'Ctrl + V', action: tr('paste') },
    { key: 'Ctrl + A', action: tr('selectAllKey') },
    { key: 'Delete', action: tr('delete') },
    { key: 'Ctrl + Enter', action: tr('processAction') },
    { key: 'Esc', action: tr('close') },
  ];

  // F-15：selectedImage 取第一个选中图（与 ImagePreview 口径一致）
  const selectedImage =
    images.find((img) => selectedImageIds.includes(img.id)) || null;

  return (
    <TooltipProvider delayDuration={300}>
      <div className="min-h-screen bg-background">
        {/* Welcome Banner */}
        {showWelcome && (
          <div className="bg-gradient-to-r from-violet-500/10 via-purple-500/10 to-fuchsia-500/10 border-b">
            <div className="px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">{tr('welcomeTitle')}</p>
                  <p className="text-xs text-muted-foreground">
                    {tr('welcomeDesc')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  asChild
                >
                  <a
                    href="https://github.com/riceshowerX/SnapForge"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <BookOpen className="w-3.5 h-3.5 mr-1" />
                    {tr('viewDocs')}
                  </a>
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={dismissWelcome}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-14 items-center px-4 lg:px-6">
            {/* Logo */}
            <div className="flex items-center gap-3 mr-6">
              <div className="relative">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-md">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold tracking-tight">
                  SnapForge
                </h1>
                <p className="text-[11px] text-muted-foreground -mt-0.5">
                  Professional Image Toolkit
                </p>
              </div>
            </div>

            {/* Main Navigation */}
            <nav className="flex items-center gap-1 flex-1">
              <Tabs
                value={activeTab}
                onValueChange={setActiveTab}
                className="w-auto"
              >
                <TabsList className="h-8 bg-transparent p-0 gap-1">
                  <TabsTrigger
                    value="upload"
                    className="h-8 px-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none rounded-md text-sm"
                  >
                    <Upload className="w-4 h-4 mr-1.5" />
                    {tr('upload')}
                  </TabsTrigger>
                  <TabsTrigger
                    value="process"
                    className="h-8 px-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none rounded-md text-sm"
                  >
                    <Wand2 className="w-4 h-4 mr-1.5" />
                    {tr('process')}
                    {selectedCount > 0 && (
                      <Badge
                        variant="secondary"
                        className="ml-1 h-4 px-1.5 text-[10px]"
                      >
                        {selectedCount}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger
                    value="duplicates"
                    className="h-8 px-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none rounded-md text-sm"
                  >
                    <Copy className="w-4 h-4 mr-1.5" />
                    {tr('duplicateDetection')}
                  </TabsTrigger>
                  <TabsTrigger
                    value="stats"
                    className="h-8 px-3 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none rounded-md text-sm"
                  >
                    <BarChart2 className="w-4 h-4 mr-1.5" />
                    {tr('statistics')}
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-1">
              {totalCount > 0 && (
                <Badge
                  variant="outline"
                  className="hidden md:flex h-7 px-2.5 text-xs font-normal"
                >
                  <FileImage className="w-3 h-3 mr-1" />
                  {tr('images', { count: totalCount })}
                </Badge>
              )}

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setShowRightPanel(!showRightPanel)}
                  >
                    {showRightPanel ? (
                      <PanelRightClose className="h-4 w-4" />
                    ) : (
                      <PanelRightOpen className="h-4 w-4" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  {showRightPanel ? tr('hidePanel') : tr('showPanel')}
                </TooltipContent>
              </Tooltip>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Keyboard className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
                    {tr('keyboardShortcuts')}
                  </div>
                  {shortcuts.map((s, i) => (
                    <DropdownMenuItem
                      key={i}
                      className="flex justify-between text-xs"
                    >
                      <span className="text-muted-foreground">{s.action}</span>
                      <kbd className="ml-2 px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono">
                        {s.key}
                      </kbd>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              <ThemeToggle />

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Globe className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={() => setLanguage('zh')}
                    className={language === 'zh' ? 'bg-accent' : ''}
                  >
                    <span className="mr-2">🇨🇳</span>
                    中文
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setLanguage('en')}
                    className={language === 'en' ? 'bg-accent' : ''}
                  >
                    <span className="mr-2">🇺🇸</span>
                    English
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    asChild
                  >
                    <a
                      href="https://github.com/riceshowerX/SnapForge"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Github className="h-4 w-4" />
                    </a>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>GitHub</TooltipContent>
              </Tooltip>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex h-[calc(100vh-3.5rem)]">
          {/* Left Panel - Main Content */}
          <main className="flex-1 overflow-hidden">
            <div className="h-full overflow-auto p-4 lg:p-6">
              {/* Stats Bar */}
              <div className="flex items-center gap-4 mb-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <Layers className="w-4 h-4" />
                  <span>
                    {tr('uploaded')} {totalCount}
                  </span>
                </div>
                {selectedCount > 0 && (
                  <>
                    <span className="text-border">•</span>
                    <div className="flex items-center gap-1.5 text-primary">
                      <FileImage className="w-4 h-4" />
                      <span>
                        {tr('selected')} {selectedCount}
                      </span>
                    </div>
                  </>
                )}
                {!showRightPanel && (
                  <>
                    <span className="text-border">•</span>
                    <Button
                      variant="link"
                      size="sm"
                      className="h-auto p-0 text-xs"
                      onClick={() => setShowRightPanel(true)}
                    >
                      {tr('showConfigPanel')}
                      <ChevronRight className="w-3 h-3 ml-0.5" />
                    </Button>
                  </>
                )}
              </div>

              {/* Tab Content */}
              {activeTab === 'upload' && <ImageUploader />}
              {activeTab === 'process' && <ProcessingPanel />}
              {activeTab === 'duplicates' && <DuplicateDetector />}
              {activeTab === 'stats' && <StatsDashboard />}
            </div>
          </main>

          {/* Right Panel */}
          {showRightPanel && (
            <aside className="w-80 border-l bg-muted/10 flex flex-col">
              {/* Panel Tabs */}
              <div className="flex items-center border-b px-1 overflow-x-auto">
                <Button
                  variant="ghost"
                  size="sm"
                  className={`h-9 rounded-none border-b-2 shrink-0 ${rightPanelTab === 'config' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setRightPanelTab('config')}
                >
                  <Settings2 className="w-4 h-4 mr-1" />
                  {tr('config')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`h-9 rounded-none border-b-2 shrink-0 ${rightPanelTab === 'preview' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setRightPanelTab('preview')}
                >
                  <ImageIcon className="w-4 h-4 mr-1" />
                  {tr('preview')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`h-9 rounded-none border-b-2 shrink-0 ${rightPanelTab === 'schemes' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setRightPanelTab('schemes')}
                >
                  <Zap className="w-4 h-4 mr-1" />
                  {tr('schemes')}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`h-9 rounded-none border-b-2 shrink-0 ${rightPanelTab === 'history' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setRightPanelTab('history')}
                >
                  <History className="w-4 h-4 mr-1" />
                  {tr('history')}
                </Button>
              </div>

              {/* Panel Content */}
              <ScrollArea className="flex-1">
                <div className="p-3">
                  {rightPanelTab === 'config' && <ProcessConfigPanel />}
                  {rightPanelTab === 'preview' && (
                    <div className="space-y-3">
                      <ImagePreview />
                      {/* F-15：EXIF 面板出现条件与 ImagePreview 一致（有选中图即显示） */}
                      {/* key 保证切换图片时 ExifPanel 重新挂载，避免脏状态 */}
                      {selectedImage && (
                        <ExifPanel key={selectedImage.id} image={selectedImage} />
                      )}
                    </div>
                  )}
                  {rightPanelTab === 'schemes' && (
                    <SchemeManager
                      currentConfig={config}
                      onApplyScheme={(newConfig) => {
                        // 逐个更新配置
                        Object.keys(newConfig).forEach((key) => {
                          updateConfig(
                            key as ProcessConfigKey,
                            newConfig[key as ProcessConfigKey]
                          );
                        });
                      }}
                    />
                  )}
                  {rightPanelTab === 'history' && <ProcessingHistory />}
                </div>
              </ScrollArea>
            </aside>
          )}
        </div>

        {/* Help Tips FAB */}
        <div className="fixed bottom-4 left-4 z-40">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="h-10 w-10 rounded-full shadow-lg bg-background"
              >
                <Lightbulb className="w-5 h-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent side="top" align="start" className="w-72">
              <div className="p-3">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  {tr('tips')}
                </h4>
                <ul className="space-y-1.5 text-xs text-muted-foreground">
                  <li>• {tr('tipDragDrop')}</li>
                  <li>• {tr('tipSchemes')}</li>
                  <li>• {tr('tipAutoSave')}</li>
                  <li>• {tr('tipZip')}</li>
                </ul>
                <DropdownMenuSeparator className="my-2" />
                <div className="text-xs text-muted-foreground">
                  <p>{tr('haveIssues')}</p>
                  <a
                    href="https://github.com/riceshowerX/SnapForge/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    {tr('submitFeedback')}
                  </a>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </TooltipProvider>
  );
}
