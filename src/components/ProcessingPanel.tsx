'use client';

import { useCallback, useState, useEffect, useRef } from 'react';
import { Loader2, CheckCircle, XCircle, Download, Play, RotateCcw, FileImage, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAppStore } from '@/store';
import JSZip from 'jszip';
import Image from 'next/image';

export function ProcessingPanel() {
  const { 
    images, 
    config, 
    selectedImageIds, 
    currentTask, 
    isProcessing,
    startProcessing,
    updateProcessResult,
    completeProcessing,
    taskHistory
  } = useAppStore();

  const [results, setResults] = useState<Map<string, { blob?: Blob; filename?: string; preview?: string }>>(new Map());
  const [currentProcessingIndex, setCurrentProcessingIndex] = useState<number>(-1);
  const [error, setError] = useState<string | null>(null);
  
  // 用于跟踪需要清理的 URL
  const objectUrlsRef = useRef<Set<string>>(new Set());

  // 清理 object URLs
  useEffect(() => {
    return () => {
      objectUrlsRef.current.forEach(url => {
        URL.revokeObjectURL(url);
      });
      objectUrlsRef.current.clear();
    };
  }, []);

  // 快捷键：Ctrl+Enter 开始处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 如果焦点在输入框中，不处理快捷键
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const selectedImages = images.filter(img => selectedImageIds.includes(img.id));
        if (selectedImages.length > 0 && !isProcessing) {
          processImages();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [images, selectedImageIds, isProcessing]);

  const processImages = useCallback(async () => {
    const selectedImages = images.filter(img => selectedImageIds.includes(img.id));
    if (selectedImages.length === 0) return;

    setError(null);
    startProcessing();
    setResults(new Map());
    setCurrentProcessingIndex(0);

    for (let i = 0; i < selectedImages.length; i++) {
      const image = selectedImages[i];
      setCurrentProcessingIndex(i);
      
      try {
        // 从 base64 获取 blob
        const response = await fetch(image.url);
        if (!response.ok) {
          throw new Error(`Failed to fetch image: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        
        const formData = new FormData();
        formData.append('file', blob, image.name);
        formData.append('config', JSON.stringify(config));
        formData.append('counter', String(i + 1));

        const result = await fetch('/api/process', {
          method: 'POST',
          body: formData,
        });

        if (!result.ok) {
          const errorData = await result.json().catch(() => ({}));
          throw new Error(errorData.error || `Processing failed: ${result.statusText}`);
        }

        const processedBlob = await result.blob();
        const filename = result.headers.get('Content-Disposition')?.split('filename=')[1]?.replace(/"/g, '') || `processed_${i + 1}.jpg`;
        const preview = URL.createObjectURL(processedBlob);
        
        // 跟踪 URL 以便清理
        objectUrlsRef.current.add(preview);

        setResults(prev => {
          const newMap = new Map(prev);
          newMap.set(image.id, { blob: processedBlob, filename, preview });
          return newMap;
        });

        updateProcessResult({
          id: image.id,
          originalName: image.name,
          status: 'success',
          processedUrl: preview,
          processingTime: Date.now(),
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        console.error(`Failed to process ${image.name}:`, err);
        
        updateProcessResult({
          id: image.id,
          originalName: image.name,
          status: 'error',
          error: errorMessage,
        });
      }
    }

    setCurrentProcessingIndex(-1);
    completeProcessing();
  }, [images, config, selectedImageIds, startProcessing, updateProcessResult, completeProcessing]);

  const downloadAll = useCallback(async () => {
    if (results.size === 0) return;
    
    const zip = new JSZip();
    
    results.forEach((value, key) => {
      if (value.blob && value.filename) {
        zip.file(value.filename, value.blob);
      }
    });

    const content = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(content);
    const a = document.createElement('a');
    a.href = url;
    a.download = `snapforge_${Date.now()}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [results]);

  const downloadSingle = useCallback((imageId: string) => {
    const result = results.get(imageId);
    if (!result?.blob || !result?.filename) return;

    const url = URL.createObjectURL(result.blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = result.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [results]);

  const resetProcessing = useCallback(() => {
    // 清理旧的 object URLs
    results.forEach((value) => {
      if (value.preview) {
        URL.revokeObjectURL(value.preview);
        objectUrlsRef.current.delete(value.preview);
      }
    });
    setResults(new Map());
    setError(null);
  }, [results]);

  const selectedImages = images.filter(img => selectedImageIds.includes(img.id));
  const canProcess = selectedImages.length > 0 && !isProcessing;

  const successCount = results.size;
  const activeConfigCount = Object.entries(config).filter(([key, value]) => 
    typeof value === 'object' && value !== null && 'enabled' in value && (value as { enabled: boolean }).enabled
  ).length;

  // 空状态
  if (!currentTask && results.size === 0) {
    return (
      <div className="space-y-4">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="p-3">
            <div className="text-2xl font-bold">{images.length}</div>
            <div className="text-xs text-muted-foreground">已上传</div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold text-primary">{selectedImageIds.length}</div>
            <div className="text-xs text-muted-foreground">已选择</div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold">{activeConfigCount}</div>
            <div className="text-xs text-muted-foreground">已启用配置</div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold">{taskHistory.length}</div>
            <div className="text-xs text-muted-foreground">历史记录</div>
          </Card>
        </div>

        {/* 错误提示 */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 开始处理卡片 */}
        <Card>
          <CardContent className="py-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-medium mb-1">准备就绪</h3>
                <p className="text-sm text-muted-foreground">
                  {selectedImages.length > 0 
                    ? `已选择 ${selectedImages.length} 张图片，${activeConfigCount} 项配置已启用`
                    : '请先上传并选择要处理的图片'
                  }
                </p>
              </div>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    onClick={processImages} 
                    disabled={!canProcess}
                    size="lg"
                    className="px-8"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    开始处理
                    {selectedImages.length > 0 && ` (${selectedImages.length}张)`}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  {selectedImages.length > 0 
                    ? '点击开始处理选中图片 (Ctrl+Enter)' 
                    : '请先选择要处理的图片'}
                </TooltipContent>
              </Tooltip>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // 处理中或已完成
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  处理中...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  处理完成
                </>
              )}
            </CardTitle>
            <CardDescription className="text-xs mt-1">
              {isProcessing 
                ? `正在处理第 ${currentProcessingIndex + 1} / ${selectedImages.length} 张`
                : `成功 ${successCount} 张，共 ${selectedImages.length} 张`
              }
            </CardDescription>
          </div>
          
          {!isProcessing && successCount > 0 && (
            <Button onClick={downloadAll} size="sm">
              <Download className="w-4 h-4 mr-1.5" />
              下载全部
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 进度条 */}
        {isProcessing && (
          <div className="space-y-2">
            <Progress value={((currentProcessingIndex + 1) / selectedImages.length) * 100} />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>处理进度</span>
              <span>{currentProcessingIndex + 1} / {selectedImages.length}</span>
            </div>
          </div>
        )}

        {/* 结果列表 */}
        <div className="space-y-1.5 max-h-[400px] overflow-auto">
          {selectedImages.map((image, index) => {
            const result = currentTask?.results.find(r => r.id === image.id);
            const hasResult = results.has(image.id);
            const resultData = results.get(image.id);

            return (
              <div
                key={image.id}
                className={`
                  flex items-center gap-3 p-2.5 rounded-lg transition-colors
                  ${isProcessing && currentProcessingIndex === index ? 'bg-primary/5 ring-1 ring-primary/20' : 'bg-muted/30'}
                `}
              >
                {/* 预览图 */}
                <div className="relative w-10 h-10 rounded overflow-hidden border shrink-0">
                  {hasResult && resultData?.preview ? (
                    <Image
                      src={resultData.preview}
                      alt="processed"
                      fill
                      className="object-cover"
                      unoptimized
                    />
                  ) : image.preview ? (
                    <Image
                      src={image.preview}
                      alt={image.name}
                      fill
                      className="object-cover opacity-50"
                      unoptimized
                    />
                  ) : (
                    <div className="w-full h-full bg-muted flex items-center justify-center">
                      <FileImage className="w-4 h-4 text-muted-foreground" />
                    </div>
                  )}
                  {isProcessing && currentProcessingIndex === index && (
                    <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                      <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    </div>
                  )}
                </div>

                {/* 文件信息 */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{resultData?.filename || image.name}</p>
                  {result?.error && (
                    <p className="text-xs text-destructive truncate">{result.error}</p>
                  )}
                </div>

                {/* 状态图标 */}
                <div className="shrink-0">
                  {result?.status === 'processing' ? (
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  ) : result?.status === 'success' ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : result?.status === 'error' ? (
                    <XCircle className="w-4 h-4 text-destructive" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-muted-foreground/30" />
                  )}
                </div>

                {/* 下载按钮 */}
                {hasResult && !isProcessing && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0 shrink-0"
                    onClick={() => downloadSingle(image.id)}
                  >
                    <Download className="w-3.5 h-3.5" />
                  </Button>
                )}
              </div>
            );
          })}
        </div>

        {/* 底部操作 */}
        {!isProcessing && (
          <div className="flex justify-between items-center pt-2 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={resetProcessing}
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              重新处理
            </Button>
            <Button
              size="sm"
              onClick={processImages}
            >
              <Play className="w-3.5 h-3.5 mr-1.5" />
              再次处理
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
