'use client';

import { useCallback, useState, useEffect, useRef } from 'react';
import { Upload, Check, Loader2, FileImage, Trash2, RotateCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from '@/components/ui/context-menu';
import { useAppStore } from '@/store';
import { ImageFile } from '@/types';
import { v4 as uuidv4 } from 'uuid';
import Image from 'next/image';

export function ImageUploader() {
  const { addImages, images, removeImages, toggleImageSelection, selectAllImages, deselectAllImages, selectedImageIds } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // 使用 ref 避免闭包问题
  const handleFilesRef = useRef<((files: File[]) => Promise<void>) | null>(null);

  // 处理文件上传
  const handleFiles = useCallback(async (files: File[]) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadProgress(0);
    const newImages: ImageFile[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) continue;

      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || 'Upload failed');
        }

        const data = await response.json();
        
        newImages.push({
          id: uuidv4(),
          name: file.name,
          size: file.size,
          type: file.type,
          url: data.preview,
          preview: data.preview,
          width: data.width,
          height: data.height,
          selected: true,
        });

        setUploadProgress(((i + 1) / files.length) * 100);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
      }
    }

    addImages(newImages);
    setIsUploading(false);
    setUploadProgress(0);
  }, [addImages]);

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

  // 快捷键监听
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 如果焦点在输入框中，不处理快捷键
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'a' && images.length > 0) {
        e.preventDefault();
        if (selectedImageIds.length === images.length) {
          deselectAllImages();
        } else {
          selectAllImages();
        }
      }
      if (e.key === 'Delete' && selectedImageIds.length > 0) {
        e.preventDefault();
        removeImages(selectedImageIds);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [images, selectedImageIds, selectAllImages, deselectAllImages, removeImages]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(Array.from(e.dataTransfer.files));
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
    e.target.value = '';
  }, [handleFiles]);

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
          accept="image/*"
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="flex flex-col items-center gap-3">
          <div className={`
            p-4 rounded-full transition-all duration-200
            ${isDragging ? 'bg-primary/15 scale-110' : 'bg-muted'}
          `}>
            <Upload className={`w-6 h-6 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
          </div>
          
          <div>
            <p className="text-base font-medium">
              {isUploading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  上传中...
                </span>
              ) : (
                '拖拽图片到此处，或点击选择文件'
              )}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              支持 JPEG, PNG, WebP, GIF, BMP, TIFF · 最大 50MB · Ctrl+V 粘贴
            </p>
          </div>

          {isUploading && uploadProgress > 0 && (
            <div className="w-full max-w-xs">
              <Progress value={uploadProgress} className="h-1.5" />
              <p className="text-xs text-muted-foreground mt-1">{uploadProgress.toFixed(0)}%</p>
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
                  checked={selectedImageIds.length === images.length && images.length > 0}
                  onCheckedChange={(checked) => {
                    if (checked) selectAllImages();
                    else deselectAllImages();
                  }}
                />
                <label htmlFor="select-all" className="text-sm cursor-pointer select-none">
                  全选
                </label>
              </div>
              
              <span className="text-sm text-muted-foreground">
                已选择 {selectedImageIds.length} / {images.length} 张
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
                      删除选中
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>删除选中的图片 (Delete)</TooltipContent>
                </Tooltip>
              )}
              
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => removeImages(images.map(i => i.id))}
              >
                <RotateCw className="w-3.5 h-3.5 mr-1" />
                清空
              </Button>
            </div>
          </div>

          {/* 图片网格 */}
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
            {images.map((image) => (
              <ContextMenu key={image.id}>
                <ContextMenuTrigger>
                  <div
                    className={`
                      relative group aspect-square rounded-lg overflow-hidden 
                      border-2 cursor-pointer transition-all duration-150
                      ${image.selected 
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
                    <div className={`
                      absolute top-1.5 left-1.5 w-5 h-5 rounded-full 
                      flex items-center justify-center transition-all
                      ${image.selected 
                        ? 'bg-primary' 
                        : 'bg-background/80 border border-border opacity-0 group-hover:opacity-100'
                      }
                    `}>
                      {image.selected && <Check className="w-3 h-3 text-primary-foreground" />}
                    </div>

                    {/* 尺寸信息 */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <p className="text-[10px] text-white truncate">{image.name}</p>
                      <div className="flex items-center justify-between">
                        {image.width && image.height && (
                          <p className="text-[9px] text-white/70">{image.width}×{image.height}</p>
                        )}
                        <p className="text-[9px] text-white/70">{formatSize(image.size)}</p>
                      </div>
                    </div>
                  </div>
                </ContextMenuTrigger>
                <ContextMenuContent>
                  <ContextMenuItem onClick={() => toggleImageSelection(image.id)}>
                    {image.selected ? '取消选择' : '选择'}
                  </ContextMenuItem>
                  <ContextMenuItem onClick={() => removeImages([image.id])}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    删除
                  </ContextMenuItem>
                  <ContextMenuSeparator />
                  <ContextMenuItem onClick={() => {
                    deselectAllImages();
                    toggleImageSelection(image.id);
                  }}>
                    仅选择此图片
                  </ContextMenuItem>
                </ContextMenuContent>
              </ContextMenu>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
