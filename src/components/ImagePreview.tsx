'use client';

import { useCallback } from 'react';
import { useAppStore } from '@/store';
import {
  ImageOff,
  FileImage,
  Maximize,
  HardDrive,
  Info,
} from 'lucide-react';
import { formatFileSize } from '@/types';
import { t } from '@/lib/i18n';
import Image from 'next/image';

export function ImagePreview() {
  const { images, selectedImageIds, language } = useAppStore();

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // 获取第一个选中的图片
  const selectedImage = images.find((img) =>
    selectedImageIds.includes(img.id)
  );

  if (!selectedImage) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
        <ImageOff className="w-12 h-12 mb-3 opacity-50" />
        <p className="text-sm">{tr('selectPreviewHint')}</p>
        <p className="text-xs mt-1">{tr('selectPreviewHint2')}</p>
      </div>
    );
  }

  const infoItems = [
    { icon: FileImage, label: tr('fileName'), value: selectedImage.name },
    {
      icon: Maximize,
      label: tr('dimensions'),
      value:
        selectedImage.width && selectedImage.height
          ? `${selectedImage.width} × ${selectedImage.height}`
          : tr('unknown'),
    },
    {
      icon: HardDrive,
      label: tr('fileSize'),
      value: formatFileSize(selectedImage.size),
    },
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
          {tr('fileInfo')}
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
        <p className="text-xs text-muted-foreground mb-2">
          {tr('selectedCount', {
            selected: selectedImageIds.length,
            total: images.length,
          })}
        </p>
        {selectedImageIds.length > 1 && (
          <div className="flex flex-wrap gap-1">
            {images
              .filter((img) => selectedImageIds.includes(img.id))
              .slice(0, 6)
              .map((img, i) => (
                <div
                  key={img.id}
                  className="relative w-10 h-10 rounded overflow-hidden border"
                >
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
                      <span className="text-white text-xs font-medium">
                        +{selectedImageIds.length - 6}
                      </span>
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
