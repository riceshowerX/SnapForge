'use client';

import { useAppStore } from '@/store';
import { ImageOff, FileImage, Maximize, HardDrive, Info } from 'lucide-react';
import Image from 'next/image';
import { format } from 'date-fns';

export function ImagePreview() {
  const { images, selectedImageIds } = useAppStore();

  // 获取第一个选中的图片
  const selectedImage = images.find(img => selectedImageIds.includes(img.id));

  if (!selectedImage) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
        <ImageOff className="w-12 h-12 mb-3 opacity-50" />
        <p className="text-sm">选择图片查看预览</p>
        <p className="text-xs mt-1">点击图片或使用 Ctrl+A 全选</p>
      </div>
    );
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const infoItems = [
    { icon: FileImage, label: '文件名', value: selectedImage.name },
    { icon: Maximize, label: '尺寸', value: selectedImage.width && selectedImage.height 
      ? `${selectedImage.width} × ${selectedImage.height}` : '未知' },
    { icon: HardDrive, label: '大小', value: formatSize(selectedImage.size) },
  ];

  return (
    <div className="p-3 space-y-4">
      {/* 预览图 */}
      <div className="relative aspect-square rounded-lg overflow-hidden bg-muted">
        {selectedImage.preview ? (
          <Image
            src={selectedImage.preview}
            alt={selectedImage.name}
            fill
            className="object-contain"
            unoptimized
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <ImageOff className="w-8 h-8 text-muted-foreground" />
          </div>
        )}
      </div>

      {/* 文件信息 */}
      <div className="space-y-2">
        <h4 className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5" />
          文件信息
        </h4>
        <div className="space-y-1.5">
          {infoItems.map((item, i) => (
            <div key={i} className="flex items-start gap-2 text-xs">
              <item.icon className="w-3.5 h-3.5 text-muted-foreground mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <span className="text-muted-foreground">{item.label}:</span>{' '}
                <span className="break-all">{item.value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 快速操作 */}
      <div className="pt-2 border-t">
        <p className="text-xs text-muted-foreground mb-2">已选择 {selectedImageIds.length} 张图片</p>
        {selectedImageIds.length > 1 && (
          <div className="flex flex-wrap gap-1">
            {images
              .filter(img => selectedImageIds.includes(img.id))
              .slice(0, 6)
              .map((img, i) => (
                <div key={img.id} className="relative w-10 h-10 rounded overflow-hidden border">
                  {img.preview ? (
                    <Image
                      src={img.preview}
                      alt={img.name}
                      fill
                      className="object-cover"
                      unoptimized
                    />
                  ) : (
                    <div className="w-full h-full bg-muted flex items-center justify-center">
                      <FileImage className="w-4 h-4 text-muted-foreground" />
                    </div>
                  )}
                  {i === 5 && selectedImageIds.length > 6 && (
                    <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                      <span className="text-white text-xs font-medium">+{selectedImageIds.length - 6}</span>
                    </div>
                  )}
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
