'use client';

import { useCallback, useState } from 'react';
import { Search, Loader2, CheckCircle, Trash2, ImageOff, Layers } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Checkbox } from '@/components/ui/checkbox';
import { useAppStore } from '@/store';
import Image from 'next/image';

// 扩展的重复图片信息，包含原始 imageId
interface DuplicateImageInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  similarity?: number;
  imageId?: string; // 原始图片 ID，用于精确匹配
}

interface DuplicateGroupInfo {
  id: string;
  images: DuplicateImageInfo[];
  similarity: number;
  hash?: string;
}

export function DuplicateDetector() {
  const { images, removeImages } = useAppStore();
  const [isDetecting, setIsDetecting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<{
    groups: DuplicateGroupInfo[];
    totalScanned: number;
    duplicatesFound: number;
  } | null>(null);
  const [selectedDuplicates, setSelectedDuplicates] = useState<Set<string>>(new Set());

  const detectDuplicates = useCallback(async () => {
    if (images.length < 2) return;

    setIsDetecting(true);
    setProgress(0);
    setResults(null);

    try {
      const formData = new FormData();
      
      // 过滤出有效的图片（有 preview data URL）
      const validImages = images.filter(img => img.preview);
      
      if (validImages.length < 2) {
        setIsDetecting(false);
        setResults({
          groups: [],
          totalScanned: images.length,
          duplicatesFound: 0,
        });
        return;
      }
      
      // 转换 data URL 为 Blob 并添加到 formData
      const imageIdMap = new Map<string, typeof images[0]>();
      
      for (let i = 0; i < validImages.length; i++) {
        const image = validImages[i];
        imageIdMap.set(image.id, image);
        
        try {
          // preview 是 data URL (base64)，直接转换
          const base64Data = image.preview!.split(',')[1];
          const binaryString = atob(base64Data);
          const bytes = new Uint8Array(binaryString.length);
          for (let j = 0; j < binaryString.length; j++) {
            bytes[j] = binaryString.charCodeAt(j);
          }
          const blob = new Blob([bytes], { type: image.type });
          formData.append('files', blob, image.id);
        } catch (err) {
          console.error(`Failed to process image ${image.name}:`, err);
        }
        
        setProgress(((i + 1) / validImages.length) * 40);
      }
      
      formData.append('threshold', '0.9');

      setProgress(60);
      const response = await fetch('/api/duplicates', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Detection failed');

      const data = await response.json();
      
      // 解析返回的数据，恢复 imageId 映射
      if (data.groups) {
        data.groups = data.groups.map((group: DuplicateGroupInfo) => ({
          ...group,
          images: group.images.map((img: DuplicateImageInfo) => {
            // 尝试通过名称（实际上是 imageId）匹配
            const matchedImage = imageIdMap.get(img.name);
            return {
              ...img,
              imageId: matchedImage ? matchedImage.id : undefined,
              // 保留原始图片预览
              preview: matchedImage?.preview || undefined,
            };
          }),
        }));
      }
      
      setProgress(100);
      setResults(data);
    } catch (error) {
      console.error('Duplicate detection error:', error);
    } finally {
      setIsDetecting(false);
    }
  }, [images]);

  const toggleDuplicate = (imageId: string) => {
    setSelectedDuplicates(prev => {
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
    results.groups.forEach(group => {
      // 保留第一张，选择其余的
      group.images.slice(1).forEach(img => {
        // 优先使用 imageId 匹配，其次使用名称匹配
        if (img.imageId) {
          allIds.add(img.imageId);
        } else {
          // 兼容旧逻辑
          const matchedImage = images.find(i => i.name === img.name);
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
        duplicatesFound: Math.max(0, results.duplicatesFound - selectedDuplicates.size),
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
              <h3 className="font-medium mb-1">重复检测</h3>
              <p className="text-sm text-muted-foreground">
                上传至少 2 张图片后可进行重复检测
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* 检测控制 */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Search className="w-4 h-4" />
              重复图片检测
            </CardTitle>
            {results && (
              <Badge variant="secondary">
                发现 {results.groups.length} 组重复
              </Badge>
            )}
          </div>
        </CardHeader>
        
        <CardContent>
          {isDetecting ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm">正在扫描图片...</span>
              </div>
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground text-right">{progress.toFixed(0)}%</p>
            </div>
          ) : (
            <Button
              onClick={detectDuplicates}
              className="w-full"
            >
              <Search className="w-4 h-4 mr-2" />
              开始检测 ({images.length} 张)
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
              <span className="text-sm">已选择 {selectedDuplicates.size} 张重复图片</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedDuplicates(new Set())}
                >
                  取消选择
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={deleteSelected}
                >
                  <Trash2 className="w-3.5 h-3.5 mr-1" />
                  删除选中
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
                    <h3 className="font-medium">未发现重复图片</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      已扫描 {results.totalScanned} 张图片
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  共 {results.groups.length} 组，{results.duplicatesFound} 张重复图片
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={selectAllDuplicates}
                >
                  全选重复项
                </Button>
              </div>

              {results.groups.map((group, index) => (
                <Card key={group.id} className="overflow-hidden">
                  <div className="bg-muted/50 px-3 py-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">组 {index + 1}</Badge>
                      <span className="text-xs text-muted-foreground">
                        相似度 {(group.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {group.images.length} 张相似
                    </span>
                  </div>
                  
                  <CardContent className="p-3">
                    <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2">
                      {group.images.map((img, imgIndex) => {
                        // 优先使用 imageId 匹配，其次使用名称匹配
                        const imageId = img.imageId || images.find(i => i.name === img.name)?.id || img.id;
                        const matchedImage = images.find(i => i.id === imageId) || images.find(i => i.name === img.name);
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
                                    <Badge className="h-4 px-1 text-[9px] bg-green-500">保留</Badge>
                                  ) : !isKept && (
                                    <Checkbox
                                      checked={isSelected}
                                      className="h-4 w-4 bg-background/80"
                                      onClick={(e) => e.stopPropagation()}
                                    />
                                  )}
                                </div>

                                {/* 文件名 */}
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1">
                                  <p className="text-[9px] text-white truncate">{img.name}</p>
                                </div>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="text-xs">
                              {isKept ? '点击其他图片选择删除' : isSelected ? '点击取消选择' : '点击选择删除'}
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
