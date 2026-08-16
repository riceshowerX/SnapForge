'use client';

import { useCallback, useState, useEffect, useRef } from 'react';
import {
  Loader2,
  CheckCircle,
  XCircle,
  Download,
  Play,
  RotateCcw,
  FileImage,
  Sparkles,
  AlertCircle,
  Settings,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useAppStore } from '@/store';
import { getImageBlob } from '@/lib/blob-store';
import { t } from '@/lib/i18n';
import JSZip from 'jszip';
import Image from 'next/image';

// 并发处理配置
const DEFAULT_CONCURRENCY = 3;
const MAX_CONCURRENCY = 10;

interface ProcessedResult {
  blob: Blob;
  filename: string;
  preview: string;
  processingTime: number;
  processedSize: number;
}

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
    taskHistory,
    language,
  } = useAppStore();

  const [results, setResults] = useState<
    Map<string, ProcessedResult>
  >(new Map());
  const [currentProcessingIndex, setCurrentProcessingIndex] =
    useState<number>(-1);
  const [error, setError] = useState<string | null>(null);

  // 处理选项状态
  const [stopOnError, setStopOnError] = useState(false);
  const [concurrency, setConcurrency] = useState(DEFAULT_CONCURRENCY);
  const [showSettings, setShowSettings] = useState(false);

  // 用于跟踪需要清理的 URL
  const objectUrlsRef = useRef<Set<string>>(new Set());
  // 用于中断处理
  const abortRef = useRef(false);

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // 清理 object URLs
  useEffect(() => {
    const currentUrls = objectUrlsRef.current;
    return () => {
      const urls = Array.from(currentUrls);
      urls.forEach((url) => {
        URL.revokeObjectURL(url);
      });
      currentUrls.clear();
    };
  }, []);

  // 处理单张图片的函数（F-01：数据源为原始 Blob；F-09：采集统计字段）
  const processSingleImage = useCallback(
    async (
      image: typeof images[0],
      index: number,
      currentConfig: typeof config
    ): Promise<{
      success: boolean;
      result?: ProcessedResult;
      error?: string;
    }> => {
      const startTime = Date.now();
      try {
        // F-01 / P-02：优先取 IndexedDB 中的原始 Blob，其次 originalDataUrl，最后 preview
        const blob = await getImageBlob(image);
        if (!blob) {
          throw new Error('Failed to read image data');
        }

        const formData = new FormData();
        formData.append('file', blob, image.name);
        formData.append('config', JSON.stringify(currentConfig));
        formData.append('counter', String(index + 1));

        const result = await fetch('/api/process', {
          method: 'POST',
          body: formData,
        });

        if (!result.ok) {
          const errorData = await result.json().catch(() => ({}));
          throw new Error(
            errorData.error?.message ||
              errorData.error ||
              `Processing failed: ${result.statusText}`
          );
        }

        const processedBlob = await result.blob();

        // F-07：解码 Content-Disposition 中的文件名（优先 RFC 5987 filename*）
        const contentDisposition =
          result.headers.get('Content-Disposition') || '';
        const filenameStar = /filename\*=UTF-8''([^;]+)/i.exec(
          contentDisposition
        );
        const filenamePlain = /filename="?([^";]+)"?/.exec(contentDisposition);
        const rawFilename =
          (filenameStar ? filenameStar[1] : filenamePlain?.[1]) ||
          `processed_${index + 1}.jpg`;
        let filename: string;
        try {
          filename = decodeURIComponent(rawFilename);
        } catch {
          filename = rawFilename;
        }

        // F-09：processedSize 优先取响应头 X-Image-Size，缺失则用 blob.size
        const processedSizeHeader = Number(
          result.headers.get('X-Image-Size')
        );
        const processedSize = Number.isFinite(processedSizeHeader)
          ? processedSizeHeader
          : processedBlob.size;

        const preview = URL.createObjectURL(processedBlob);

        // 跟踪 URL 以便清理
        objectUrlsRef.current.add(preview);

        return {
          success: true,
          result: {
            blob: processedBlob,
            filename,
            preview,
            processingTime: Date.now() - startTime,
            processedSize,
          },
        };
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Unknown error';
        console.error(`Failed to process ${image.name}:`, err);
        return { success: false, error: errorMessage };
      }
    },
    []
  );

  // 并发处理图片
  const processImages = useCallback(async () => {
    // 使用 zustand getState 避免闭包 stale 值问题
    const {
      images: currentImages,
      config: currentConfig,
      selectedImageIds: currentSelectedIds,
    } = useAppStore.getState();
    const selectedImages = currentImages.filter((img) =>
      currentSelectedIds.includes(img.id)
    );

    if (selectedImages.length === 0) return;

    setError(null);
    abortRef.current = false;

    // P-01：revoke 旧批次的 object URL 并清空 ref，防止内存随批次线性增长
    objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    objectUrlsRef.current.clear();

    startProcessing();
    setResults(new Map());
    setCurrentProcessingIndex(0);

    const totalImages = selectedImages.length;
    let processedCount = 0;
    let aborted = false;

    // 分批并发处理
    for (let i = 0; i < totalImages; i += concurrency) {
      // 检查是否中断
      if (abortRef.current) {
        aborted = true;
        break;
      }

      const batch = selectedImages.slice(i, i + concurrency);
      const batchResults = await Promise.all(
        batch.map((image, localIndex) =>
          processSingleImage(image, i + localIndex, currentConfig)
        )
      );

      // 处理批次结果
      for (let j = 0; j < batchResults.length; j++) {
        const result = batchResults[j];
        const image = batch[j];

        processedCount++;
        setCurrentProcessingIndex(processedCount - 1);

        if (result.success && result.result) {
          const processedResult = result.result;
          setResults((prev) => {
            const newMap = new Map(prev);
            newMap.set(image.id, processedResult);
            return newMap;
          });

          // F-09：填充 originalSize / processedSize / processingTime
          updateProcessResult({
            id: image.id,
            originalName: image.name,
            status: 'success',
            processedUrl: processedResult.preview,
            originalSize: image.size,
            processedSize: processedResult.processedSize,
            processingTime: processedResult.processingTime,
          });
        } else {
          updateProcessResult({
            id: image.id,
            originalName: image.name,
            status: 'error',
            error: result.error,
          });

          // 如果设置为遇到错误停止
          if (stopOnError) {
            aborted = true;
            abortRef.current = true;
            // BUG-2：语言无关的 ASCII 分隔符（避免英文界面显示全角冒号）
            setError(`${tr('processingError')}: ${result.error}`);
            break;
          }
        }
      }
    }

    setCurrentProcessingIndex(-1);

    // F-14：中止时以 error 状态 + 实际进度入库，不写「100% 完成」
    completeProcessing(aborted ? 'error' : 'completed');
    if (aborted) {
      setError(tr('processingInterrupted'));
    }
  }, [
    concurrency,
    stopOnError,
    processSingleImage,
    startProcessing,
    updateProcessResult,
    completeProcessing,
    tr,
  ]);

  // 中断处理
  const abortProcessing = useCallback(() => {
    abortRef.current = true;
  }, []);

  // 快捷键：Ctrl+Enter 开始处理（用 getState 读取最新状态）
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 如果焦点在输入框中，不处理快捷键
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const {
          images: currentImages,
          selectedImageIds: currentIds,
          isProcessing: currentIsProcessing,
        } = useAppStore.getState();
        const selectedImages = currentImages.filter((img) =>
          currentIds.includes(img.id)
        );
        if (selectedImages.length > 0 && !currentIsProcessing) {
          processImages();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [processImages]);

  // F-16：ZIP 内同名文件查重，冲突追加 (2)/(3) 后缀
  const downloadAll = useCallback(async () => {
    if (results.size === 0) return;

    const zip = new JSZip();
    const usedNames = new Set<string>();

    const uniqueName = (name: string): string => {
      if (!usedNames.has(name)) {
        usedNames.add(name);
        return name;
      }
      const dot = name.lastIndexOf('.');
      const base = dot > 0 ? name.slice(0, dot) : name;
      const ext = dot > 0 ? name.slice(dot) : '';
      let i = 2;
      while (usedNames.has(`${base}(${i})${ext}`)) {
        i++;
      }
      const finalName = `${base}(${i})${ext}`;
      usedNames.add(finalName);
      return finalName;
    };

    results.forEach((value) => {
      if (value.blob && value.filename) {
        zip.file(uniqueName(value.filename), value.blob);
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

  const downloadSingle = useCallback(
    (imageId: string) => {
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
    },
    [results]
  );

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

  const selectedImages = images.filter((img) =>
    selectedImageIds.includes(img.id)
  );
  const canProcess = selectedImages.length > 0 && !isProcessing;

  // Q-06：errorCount 从 results/currentTask 显式统计，pending 不计为失败
  const taskResults = currentTask?.results ?? [];
  const successCount = taskResults.filter((r) => r.status === 'success').length;
  const errorCount = taskResults.filter((r) => r.status === 'error').length;

  const activeConfigCount = Object.entries(config).filter(
    ([, value]) =>
      typeof value === 'object' &&
      value !== null &&
      'enabled' in value &&
      (value as { enabled: boolean }).enabled
  ).length;

  // 空状态
  if (!currentTask && results.size === 0) {
    return (
      <div className="space-y-4">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="p-3">
            <div className="text-2xl font-bold">{images.length}</div>
            <div className="text-xs text-muted-foreground">
              {tr('uploaded')}
            </div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold text-primary">
              {selectedImageIds.length}
            </div>
            <div className="text-xs text-muted-foreground">{tr('selected')}</div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold">{activeConfigCount}</div>
            <div className="text-xs text-muted-foreground">
              {tr('enabledConfigs')}
            </div>
          </Card>
          <Card className="p-3">
            <div className="text-2xl font-bold">{taskHistory.length}</div>
            <div className="text-xs text-muted-foreground">
              {tr('historyRecords')}
            </div>
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
                <h3 className="text-lg font-medium mb-1">{tr('ready')}</h3>
                <p className="text-sm text-muted-foreground">
                  {selectedImages.length > 0
                    ? tr('selectedAndConfig', {
                        count: selectedImages.length,
                        configs: activeConfigCount,
                      })
                    : tr('noImagesToProcess')}
                </p>
              </div>
              <div className="flex items-center justify-center gap-2">
                {/* 设置按钮 */}
                <Dialog open={showSettings} onOpenChange={setShowSettings}>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="icon" className="h-10 w-10">
                      <Settings className="w-4 h-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>{tr('processingSettings')}</DialogTitle>
                      <DialogDescription>{tr('concurrencyHint')}</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-6 py-4">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="concurrency">{tr('concurrency')}</Label>
                          <span className="text-sm font-medium">
                            {concurrency}
                          </span>
                        </div>
                        <Slider
                          id="concurrency"
                          min={1}
                          max={MAX_CONCURRENCY}
                          step={1}
                          value={[concurrency]}
                          onValueChange={(v) => setConcurrency(v[0])}
                        />
                        <p className="text-xs text-muted-foreground">
                          {tr('concurrencyHint')}
                        </p>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="stop-on-error">
                            {tr('stopOnError')}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {tr('stopOnErrorHint')}
                          </p>
                        </div>
                        <Switch
                          id="stop-on-error"
                          checked={stopOnError}
                          onCheckedChange={setStopOnError}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button onClick={() => setShowSettings(false)}>
                        {tr('finish')}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      onClick={processImages}
                      disabled={!canProcess}
                      size="lg"
                      className="px-8"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {tr('startProcessing')}
                      {selectedImages.length > 0 && ` (${selectedImages.length})`}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {selectedImages.length > 0
                      ? tr('startProcessingHint')
                      : tr('noImagesToProcess')}
                  </TooltipContent>
                </Tooltip>
              </div>
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
                  {tr('processingInProgress')}
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  {tr('processingComplete')}
                </>
              )}
            </CardTitle>
            <CardDescription className="text-xs mt-1">
              {isProcessing
                ? tr('currentProcessing', {
                    current: currentProcessingIndex + 1,
                    total: selectedImages.length,
                    concurrency,
                  })
                : tr('successSummary', {
                    success: successCount,
                    failedText:
                      errorCount > 0
                        ? tr('failedSummary', { failed: errorCount })
                        : '',
                    total: selectedImages.length,
                  })}
            </CardDescription>
          </div>

          <div className="flex items-center gap-2">
            {!isProcessing && successCount > 0 && (
              <Button onClick={downloadAll} size="sm">
                <Download className="w-4 h-4 mr-1.5" />
                {tr('downloadAll')}
              </Button>
            )}
            {isProcessing && (
              <Button
                onClick={abortProcessing}
                variant="destructive"
                size="sm"
              >
                {tr('stop')}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 进度条 */}
        {isProcessing && (
          <div className="space-y-2">
            <Progress
              value={
                ((currentProcessingIndex + 1) / selectedImages.length) * 100
              }
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{tr('processingProgress')}</span>
              <span>
                {currentProcessingIndex + 1} / {selectedImages.length}
              </span>
            </div>
          </div>
        )}

        {/* 结果列表 */}
        <div className="space-y-1.5 max-h-[400px] overflow-auto">
          {selectedImages.map((image, index) => {
            const result = taskResults.find((r) => r.id === image.id);
            const hasResult = results.has(image.id);
            const resultData = results.get(image.id);

            return (
              <div
                key={image.id}
                className={`
                  flex items-center gap-3 p-2.5 rounded-lg transition-colors
                  ${isProcessing && currentProcessingIndex === index
                      ? 'bg-primary/5 ring-1 ring-primary/20'
                      : 'bg-muted/30'
                    }
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
                </div>

                {/* 信息 */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{image.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {hasResult && resultData?.filename
                      ? resultData.filename
                      : result?.status === 'error'
                        ? tr('processedFile')
                        : tr('waiting')}
                  </p>
                </div>

                {/* 状态 */}
                <div className="flex items-center gap-2 shrink-0">
                  {isProcessing && currentProcessingIndex === index ? (
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  ) : result?.status === 'success' || hasResult ? (
                    <Tooltip>
                      <TooltipTrigger>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      </TooltipTrigger>
                      <TooltipContent>{tr('success')}</TooltipContent>
                    </Tooltip>
                  ) : result?.status === 'error' ? (
                    <Tooltip>
                      <TooltipTrigger>
                        <XCircle className="w-4 h-4 text-destructive" />
                      </TooltipTrigger>
                      <TooltipContent>
                        {result.error || tr('processedFile')}
                      </TooltipContent>
                    </Tooltip>
                  ) : null}

                  {hasResult && (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => downloadSingle(image.id)}
                        >
                          <Download className="w-3.5 h-3.5" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>{tr('download')}</TooltipContent>
                    </Tooltip>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* 重置按钮 */}
        {!isProcessing && (
          <div className="flex justify-center pt-2">
            <Button variant="outline" size="sm" onClick={resetProcessing}>
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              {tr('reset')}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
