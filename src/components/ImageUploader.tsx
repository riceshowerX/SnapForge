'use client';

import { useCallback, useState, useEffect, useRef } from 'react';
import {
  Upload,
  Check,
  Loader2,
  FileImage,
  Trash2,
  RotateCw,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from '@/components/ui/context-menu';
import { useAppStore } from '@/store';
import { ImageFile } from '@/types';
import { putBlob } from '@/lib/blob-store';
import { ALLOWED_TYPES } from '@/lib/file-validation';
import { t } from '@/lib/i18n';
import { v4 as uuidv4 } from 'uuid';
import Image from 'next/image';

// 上传并发数（与 /api/upload 限流 30 次/分钟对齐：4 路并发下 20 张图 5 批内完成）
const UPLOAD_CONCURRENCY = 4;

interface UploadResponseData {
  name: string;
  size: number;
  type: string;
  width: number;
  height: number;
  format: string;
  hasAlpha: boolean;
  preview: string;
  originalDataUrl?: string;
}

export function ImageUploader() {
  const {
    addImages,
    images,
    removeImages,
    toggleImageSelection,
    selectAllImages,
    deselectAllImages,
    selectedImageIds,
    language,
  } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // 使用 ref 避免闭包问题
  const handleFilesRef = useRef<((files: File[]) => Promise<void>) | null>(null);

  // 上传单张图片
  const uploadOne = useCallback(
    async (file: File): Promise<ImageFile | null> => {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const message =
            errorData.error?.message ||
            errorData.error ||
            tr('uploadFailed');
          throw new Error(message);
        }

        const json = await response.json();
        const data: UploadResponseData = json?.data ?? json;

        const image: ImageFile = {
          id: uuidv4(),
          name: file.name,
          size: file.size,
          type: file.type,
          url: data.preview,
          preview: data.preview,
          originalDataUrl: data.originalDataUrl || '',
          width: data.width,
          height: data.height,
          selected: true,
        };

        // F-01 / P-02：>2MB 的原始数据优先写入 IndexedDB，preview 仅用于展示
        if (data.originalDataUrl) {
          try {
            const blobResponse = await fetch(data.originalDataUrl);
            const blob = await blobResponse.blob();
            const ok = await putBlob(image.id, blob);
            if (ok) {
              image.blobKey = image.id;
              // 写入成功后可释放内存中的原始 base64
              image.originalDataUrl = '';
            }
          } catch (error) {
            console.warn('Failed to store original blob in IndexedDB:', error);
            // 降级：blobKey 留空，originalDataUrl 仍保留在内存
          }
        }

        return image;
      } catch (error) {
        const message = error instanceof Error ? error.message : tr('uploadFailed');
        console.error(`Failed to upload ${file.name}:`, error);
        setUploadError(message);
        return null;
      }
    },
    [tr]
  );

  // 处理文件上传（P-03：4 路并发，保留逐张进度）
  const handleFiles = useCallback(
    async (files: File[]) => {
      if (!files || files.length === 0) return;

      // 前端预检（F-13）：与后端白名单一致，减少无谓请求
      const validFiles = files.filter((f) =>
        ALLOWED_TYPES.includes(f.type as (typeof ALLOWED_TYPES)[number])
      );
      if (validFiles.length === 0) {
        setUploadError(tr('invalidFileType'));
        return;
      }

      setIsUploading(true);
      setUploadError(null);
      setUploadProgress(0);
      const newImages: ImageFile[] = [];
      let completed = 0;

      const batches: File[][] = [];
      for (let i = 0; i < validFiles.length; i += UPLOAD_CONCURRENCY) {
        batches.push(validFiles.slice(i, i + UPLOAD_CONCURRENCY));
      }

      for (const batch of batches) {
        const results = await Promise.all(batch.map((file) => uploadOne(file)));
        for (const result of results) {
          if (result) newImages.push(result);
        }
        completed += batch.length;
        setUploadProgress((completed / validFiles.length) * 100);
      }

      if (newImages.length > 0) {
        addImages(newImages);
      }
      if (newImages.length < validFiles.length) {
        setUploadError(tr('someUploadsFailed'));
      }

      setIsUploading(false);
      setUploadProgress(0);
    },
    [addImages, uploadOne, tr]
  );

  // 保持 ref 更新
  useEffect(() => {
    handleFilesRef.current = handleFiles;
  }, [handleFiles]);

  // 粘贴监听
  useEffect(() => {
    const handlePaste = async (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      const files: File[] = [];
      for (const item of items) {
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (file) files.push(file);
        }
      }

      if (files.length > 0 && handleFilesRef.current) {
        await handleFilesRef.current(files);
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  // 快捷键监听（P-04：用 getState 读取最新状态，依赖数组收敛为 []）
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

      const {
        images: currentImages,
        selectedImageIds: currentIds,
        deselectAllImages: deselectAll,
        selectAllImages: selectAll,
        removeImages: remove,
      } = useAppStore.getState();

      if ((e.ctrlKey || e.metaKey) && e.key === 'a' && currentImages.length > 0) {
        e.preventDefault();
        if (currentIds.length === currentImages.length) {
          deselectAll();
        } else {
          selectAll();
        }
      }
      if (e.key === 'Delete' && currentIds.length > 0) {
        e.preventDefault();
        remove(currentIds);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFiles(Array.from(e.dataTransfer.files));
    },
    [handleFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        handleFiles(Array.from(e.target.files));
      }
      e.target.value = '';
    },
    [handleFiles]
  );

  const handleRemoveSelected = useCallback(() => {
    removeImages(selectedImageIds);
  }, [removeImages, selectedImageIds]);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      {/* 上传错误提示（F-13） */}
      {uploadError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{uploadError}</AlertDescription>
        </Alert>
      )}

      {/* 上传区域 */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200
          ${isDragging
            ? 'border-primary bg-primary/5 scale-[1.01]'
            : 'border-border hover:border-primary/50 hover:bg-muted/30'
          }
        `}
      >
        <input
          type="file"
          multiple
          accept={ALLOWED_TYPES.join(',')}
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="flex flex-col items-center gap-3">
          <div
            className={`
            p-4 rounded-full transition-all duration-200
            ${isDragging ? 'bg-primary/15 scale-110' : 'bg-muted'}
          `}
          >
            <Upload
              className={`w-6 h-6 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`}
            />
          </div>

          <div>
            <p className="text-base font-medium">
              {isUploading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {tr('uploading')}
                </span>
              ) : (
                <>
                  {tr('dragDropHint')}
                  <span className="text-muted-foreground">
                    {' '}
                    {tr('orClickToUpload')}
                  </span>
                </>
              )}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {tr('supportedFormats')}
            </p>
          </div>

          {isUploading && uploadProgress > 0 && (
            <div className="w-full max-w-xs">
              <Progress value={uploadProgress} className="h-1.5" />
              <p className="text-xs text-muted-foreground mt-1">
                {uploadProgress.toFixed(0)}%
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 图片列表 */}
      {images.length > 0 && (
        <div className="space-y-3">
          {/* 操作栏 */}
          <div className="flex items-center justify-between py-2 px-1">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="select-all"
                  checked={
                    selectedImageIds.length === images.length &&
                    images.length > 0
                  }
                  onCheckedChange={(checked) => {
                    if (checked) selectAllImages();
                    else deselectAllImages();
                  }}
                />
                <label
                  htmlFor="select-all"
                  className="text-sm cursor-pointer select-none"
                >
                  {tr('selectAll')}
                </label>
              </div>

              <span className="text-sm text-muted-foreground">
                {tr('selectedCount', {
                  selected: selectedImageIds.length,
                  total: images.length,
                })}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {selectedImageIds.length > 0 && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={handleRemoveSelected}
                    >
                      <Trash2 className="w-3.5 h-3.5 mr-1" />
                      {tr('deleteSelected')}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {tr('deleteSelected')} (Delete)
                  </TooltipContent>
                </Tooltip>
              )}

              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => removeImages(images.map((i) => i.id))}
              >
                <RotateCw className="w-3.5 h-3.5 mr-1" />
                {tr('clearAll')}
              </Button>
            </div>
          </div>

          {/* 图片网格（F-08：渲染一律以 selectedImageIds 判定选中态） */}
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
            {images.map((image) => {
              const isSelected = selectedImageIds.includes(image.id);
              return (
                <ContextMenu key={image.id}>
                  <ContextMenuTrigger>
                    <div
                      className={`
                      relative group aspect-square rounded-lg overflow-hidden 
                      border-2 cursor-pointer transition-all duration-150
                      ${isSelected
                          ? 'border-primary ring-2 ring-primary/20'
                          : 'border-transparent hover:border-border'
                        }
                    `}
                      onClick={() => toggleImageSelection(image.id)}
                    >
                      {image.preview ? (
                        <Image
                          src={image.preview}
                          alt={image.name}
                          fill
                          className="object-cover"
                          unoptimized
                        />
                      ) : (
                        <div className="w-full h-full bg-muted flex items-center justify-center">
                          <FileImage className="w-6 h-6 text-muted-foreground" />
                        </div>
                      )}

                      {/* Hover Overlay */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />

                      {/* 选中标记 */}
                      <div
                        className={`
                      absolute top-1.5 left-1.5 w-5 h-5 rounded-full 
                      flex items-center justify-center transition-all
                      ${isSelected
                            ? 'bg-primary'
                            : 'bg-background/80 border border-border opacity-0 group-hover:opacity-100'
                          }
                    `}
                      >
                        {isSelected && (
                          <Check className="w-3 h-3 text-primary-foreground" />
                        )}
                      </div>

                      {/* 尺寸信息 */}
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <p className="text-[10px] text-white truncate">
                          {image.name}
                        </p>
                        <div className="flex items-center justify-between">
                          {image.width && image.height && (
                            <p className="text-[9px] text-white/70">
                              {image.width}×{image.height}
                            </p>
                          )}
                          <p className="text-[9px] text-white/70">
                            {formatSize(image.size)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </ContextMenuTrigger>
                  <ContextMenuContent>
                    <ContextMenuItem
                      onClick={() => toggleImageSelection(image.id)}
                    >
                      {isSelected ? tr('deselect') : tr('select')}
                    </ContextMenuItem>
                    <ContextMenuItem onClick={() => removeImages([image.id])}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      {tr('deleteSingle')}
                    </ContextMenuItem>
                    <ContextMenuSeparator />
                    <ContextMenuItem
                      onClick={() => {
                        deselectAllImages();
                        toggleImageSelection(image.id);
                      }}
                    >
                      {tr('selectOnly')}
                    </ContextMenuItem>
                  </ContextMenuContent>
                </ContextMenu>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
