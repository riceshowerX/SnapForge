'use client';

import { useCallback, useState } from 'react';
import {
  Search,
  Loader2,
  CheckCircle,
  Trash2,
  ImageOff,
  Layers,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAppStore } from '@/store';
import { getImageBlob } from '@/lib/blob-store';
import { t } from '@/lib/i18n';
import Image from 'next/image';

// 扩展的重复图片信息，包含原始 imageId
interface DuplicateImageInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  similarity?: number;
  imageId?: string; // 原始图片 ID，用于精确匹配
  preview?: string;
}

interface DuplicateGroupInfo {
  id: string;
  images: DuplicateImageInfo[];
  similarity: number;
  hash?: string;
}

interface DuplicateResponse {
  groups: DuplicateGroupInfo[];
  totalScanned: number;
  duplicatesFound: number;
}

export function DuplicateDetector() {
  const { images, removeImages, language } = useAppStore();
  const [isDetecting, setIsDetecting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<DuplicateResponse | null>(null);
  const [selectedDuplicates, setSelectedDuplicates] = useState<Set<string>>(
    new Set()
  );
  const [error, setError] = useState<string | null>(null);

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  const detectDuplicates = useCallback(async () => {
    if (images.length < 2) return;

    setIsDetecting(true);
    setError(null);
    setProgress(0);
    setResults(null);
    setSelectedDuplicates(new Set());

    try {
      const formData = new FormData();

      // F-01：取原始数据（IndexedDB → originalDataUrl → preview）
      const validImages: typeof images = [];
      const imageIdMap = new Map<string, (typeof images)[number]>();

      for (const image of images) {
        const blob = await getImageBlob(image);
        if (!blob) continue;
        validImages.push(image);
        imageIdMap.set(image.id, image);
        formData.append('files', blob, image.id);
        formData.append('id', image.id);
        setProgress(
          Math.min(40, ((validImages.length) / Math.max(images.length, 1)) * 40)
        );
      }

      if (validImages.length < 2) {
        setIsDetecting(false);
        setResults({
          groups: [],
          totalScanned: validImages.length,
          duplicatesFound: 0,
        });
        return;
      }

      formData.append('threshold', '0.9');

      setProgress(60);
      const response = await fetch('/api/duplicates', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error?.message || errorData.error || 'Detection failed'
        );
      }

      const json = await response.json();
      const data: DuplicateResponse = json?.data ?? json;

      // F-10：优先用 imageId 精确匹配恢复前端图片数据
      if (data.groups) {
        data.groups = data.groups.map((group) => ({
          ...group,
          images: group.images.map((img) => {
            const matchedImage = img.imageId
              ? imageIdMap.get(img.imageId)
              : imageIdMap.get(img.name);
            return {
              ...img,
              imageId: matchedImage ? matchedImage.id : img.imageId,
              preview: matchedImage?.preview || undefined,
            };
          }),
        }));
      }

      setProgress(100);
      setResults(data);
    } catch (err) {
      console.error('Duplicate detection error:', err);
      setError(err instanceof Error ? err.message : 'Detection failed');
    } finally {
      setIsDetecting(false);
    }
  }, [images]);

  const toggleDuplicate = (imageId: string) => {
    setSelectedDuplicates((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(imageId)) {
        newSet.delete(imageId);
      } else {
        newSet.add(imageId);
      }
      return newSet;
    });
  };

  const selectAllDuplicates = () => {
    if (!results) return;
    const allIds = new Set<string>();
    results.groups.forEach((group) => {
      // 保留第一张，选择其余的
      group.images.slice(1).forEach((img) => {
        if (img.imageId) {
          allIds.add(img.imageId);
        } else {
          const matchedImage = images.find((i) => i.name === img.name);
          if (matchedImage) allIds.add(matchedImage.id);
        }
      });
    });
    setSelectedDuplicates(allIds);
  };

  const deleteSelected = () => {
    if (selectedDuplicates.size === 0) return;
    removeImages(Array.from(selectedDuplicates));
    setSelectedDuplicates(new Set());
    // 重新计算结果
    if (results) {
      setResults({
        ...results,
        duplicatesFound: Math.max(
          0,
          results.duplicatesFound - selectedDuplicates.size
        ),
      });
    }
  };

  // 空状态
  if (images.length < 2) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-muted flex items-center justify-center mx-auto">
              <Layers className="w-7 h-7 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-medium mb-1">{tr('duplicateDetection')}</h3>
              <p className="text-sm text-muted-foreground">
                {tr('uploadAtLeast2')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* 错误提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 检测控制 */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Search className="w-4 h-4" />
              {tr('duplicateDetection')}
            </CardTitle>
            {results && (
              <Badge variant="secondary">
                {tr('duplicatesBadge', { count: results.groups.length })}
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent>
          {isDetecting ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm">{tr('scanning')}</span>
              </div>
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground text-right">
                {progress.toFixed(0)}%
              </p>
            </div>
          ) : (
            <Button onClick={detectDuplicates} className="w-full">
              <Search className="w-4 h-4 mr-2" />
              {tr('startDetection')} ({images.length})
            </Button>
          )}
        </CardContent>
      </Card>

      {/* 检测结果 */}
      {results && (
        <>
          {/* 操作栏 */}
          {selectedDuplicates.size > 0 && (
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm">
                {tr('selectedDuplicates', { count: selectedDuplicates.size })}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedDuplicates(new Set())}
                >
                  {tr('deselectAll')}
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={deleteSelected}
                >
                  <Trash2 className="w-3.5 h-3.5 mr-1" />
                  {tr('deleteSelected')}
                </Button>
              </div>
            </div>
          )}

          {/* 结果列表 */}
          {results.groups.length === 0 ? (
            <Card>
              <CardContent className="py-8">
                <div className="text-center space-y-3">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
                  <div>
                    <h3 className="font-medium">
                      {tr('noDuplicatesFound')}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {tr('scannedCount', { count: results.totalScanned })}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  {tr('duplicateGroups', {
                    groups: results.groups.length,
                    count: results.duplicatesFound,
                  })}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={selectAllDuplicates}
                >
                  {tr('selectAllDuplicates')}
                </Button>
              </div>

              {results.groups.map((group, index) => (
                <Card key={group.id} className="overflow-hidden">
                  <div className="bg-muted/50 px-3 py-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">
                        {tr('groupLabel', { index: index + 1 })}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {tr('similarity')}{' '}
                        {(group.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {tr('imagesSimilar', { count: group.images.length })}
                    </span>
                  </div>

                  <CardContent className="p-3">
                    <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2">
                      {group.images.map((img, imgIndex) => {
                        // F-10：优先用 imageId 精确匹配，其次名称匹配
                        const imageId =
                          img.imageId ||
                          images.find((i) => i.name === img.name)?.id ||
                          img.id;
                        const matchedImage =
                          images.find((i) => i.id === imageId) ||
                          images.find((i) => i.name === img.name);
                        const isSelected = selectedDuplicates.has(imageId);
                        const isKept = imgIndex === 0;

                        return (
                          <Tooltip key={img.id}>
                            <TooltipTrigger asChild>
                              <div
                                className={`
                                  relative aspect-square rounded-lg overflow-hidden 
                                  border-2 cursor-pointer transition-all
                                  ${isKept
                                      ? 'border-green-500 ring-1 ring-green-500/30'
                                      : isSelected
                                        ? 'border-destructive ring-1 ring-destructive/30'
                                        : 'border-border hover:border-primary/50'
                                    }
                                `}
                                onClick={() => !isKept && toggleDuplicate(imageId)}
                              >
                                {matchedImage?.preview ? (
                                  <Image
                                    src={matchedImage.preview}
                                    alt={img.name}
                                    fill
                                    className="object-cover"
                                    unoptimized
                                  />
                                ) : (
                                  <div className="w-full h-full bg-muted flex items-center justify-center">
                                    <ImageOff className="w-4 h-4 text-muted-foreground" />
                                  </div>
                                )}

                                {/* 标签 */}
                                <div className="absolute top-1 left-1">
                                  {isKept ? (
                                    <Badge className="h-4 px-1 text-[9px] bg-green-500">
                                      {tr('keep')}
                                    </Badge>
                                  ) : (
                                    <Checkbox
                                      checked={isSelected}
                                      className="h-4 w-4 bg-background/80"
                                      onClick={(e) => e.stopPropagation()}
                                      onCheckedChange={() =>
                                        toggleDuplicate(imageId)
                                      }
                                    />
                                  )}
                                </div>

                                {/* 文件名 */}
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1">
                                  <p className="text-[9px] text-white truncate">
                                    {matchedImage?.name || img.name}
                                  </p>
                                </div>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="text-xs">
                              {isKept
                                ? tr('clickToDelete')
                                : isSelected
                                  ? tr('clickToDeselect')
                                  : tr('clickToSelect')}
                            </TooltipContent>
                          </Tooltip>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
