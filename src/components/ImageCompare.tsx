'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Move, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  ChevronLeft, 
  ChevronRight,
  GripVertical,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { formatFileSize } from '@/types';

interface ImageCompareProps {
  originalUrl: string;
  originalName: string;
  originalSize: number;
  originalWidth?: number;
  originalHeight?: number;
  processedUrl?: string;
  processedName?: string;
  processedSize?: number;
  processedWidth?: number;
  processedHeight?: number;
}

export function ImageCompare({
  originalUrl,
  originalName,
  originalSize,
  originalWidth,
  originalHeight,
  processedUrl,
  processedName,
  processedSize,
  processedWidth,
  processedHeight,
}: ImageCompareProps) {
  const [mode, setMode] = useState<'slider' | 'overlay' | 'side-by-side'>('slider');
  const [sliderPosition, setSliderPosition] = useState(50);
  const [zoom, setZoom] = useState(100);
  const [isDragging, setIsDragging] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const sizeDiff = processedSize && originalSize 
    ? ((processedSize - originalSize) / originalSize) * 100 
    : 0;

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    setSliderPosition(Math.min(100, Math.max(0, percentage)));
  }, [isDragging]);

  useEffect(() => {
    const handleGlobalMouseUp = () => setIsDragging(false);
    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
  }, []);

  if (!processedUrl) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <p>处理后才能查看对比效果</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={isFullscreen ? 'fixed inset-4 z-50' : ''}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">对比预览</CardTitle>
          <div className="flex items-center gap-2">
            <Tabs value={mode} onValueChange={(v) => setMode(v as typeof mode)}>
              <TabsList className="h-7">
                <TabsTrigger value="slider" className="h-6 px-2 text-xs">滑块</TabsTrigger>
                <TabsTrigger value="overlay" className="h-6 px-2 text-xs">叠加</TabsTrigger>
                <TabsTrigger value="side-by-side" className="h-6 px-2 text-xs">并排</TabsTrigger>
              </TabsList>
            </Tabs>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setIsFullscreen(!isFullscreen)}
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* 对比视图 */}
        <div 
          ref={containerRef}
          className="relative aspect-video bg-muted/30 rounded-lg overflow-hidden select-none"
          onMouseMove={handleMouseMove}
        >
          {mode === 'slider' && (
            <>
              {/* 原图 */}
              <div 
                className="absolute inset-0 overflow-hidden"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
              >
                <div 
                  className="w-full h-full flex items-center justify-center"
                  style={{ transform: `scale(${zoom / 100})` }}
                >
                  <Image
                    src={originalUrl}
                    alt="原图"
                    fill
                    className="object-contain"
                    unoptimized
                  />
                </div>
              </div>
              
              {/* 处理后 */}
              <div 
                className="absolute inset-0 overflow-hidden"
                style={{ clipPath: `inset(0 0 0 ${sliderPosition}%)` }}
              >
                <div 
                  className="w-full h-full flex items-center justify-center"
                  style={{ transform: `scale(${zoom / 100})` }}
                >
                  <Image
                    src={processedUrl}
                    alt="处理后"
                    fill
                    className="object-contain"
                    unoptimized
                  />
                </div>
              </div>
              
              {/* 滑块 */}
              <div 
                className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg cursor-ew-resize z-10"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
              >
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center">
                  <GripVertical className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>
              
              {/* 标签 */}
              <Badge variant="secondary" className="absolute top-2 left-2 text-xs">
                原图
              </Badge>
              <Badge variant="secondary" className="absolute top-2 right-2 text-xs">
                处理后
              </Badge>
            </>
          )}
          
          {mode === 'overlay' && (
            <div 
              className="w-full h-full flex items-center justify-center"
              style={{ transform: `scale(${zoom / 100})` }}
            >
              <Image
                src={processedUrl}
                alt="处理后"
                fill
                className="object-contain"
                unoptimized
              />
            </div>
          )}
          
          {mode === 'side-by-side' && (
            <div className="flex h-full">
              <div className="flex-1 relative border-r">
                <div 
                  className="w-full h-full flex items-center justify-center"
                  style={{ transform: `scale(${zoom / 100})` }}
                >
                  <Image
                    src={originalUrl}
                    alt="原图"
                    fill
                    className="object-contain p-2"
                    unoptimized
                  />
                </div>
                <Badge variant="secondary" className="absolute top-2 left-2 text-xs">
                  原图
                </Badge>
              </div>
              <div className="flex-1 relative">
                <div 
                  className="w-full h-full flex items-center justify-center"
                  style={{ transform: `scale(${zoom / 100})` }}
                >
                  <Image
                    src={processedUrl}
                    alt="处理后"
                    fill
                    className="object-contain p-2"
                    unoptimized
                  />
                </div>
                <Badge variant="secondary" className="absolute top-2 right-2 text-xs">
                  处理后
                </Badge>
              </div>
            </div>
          )}
        </div>

        {/* 控制栏 */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="h-7 w-7"
              onClick={() => setZoom(Math.max(25, zoom - 25))}
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </Button>
            <span className="text-xs w-12 text-center">{zoom}%</span>
            <Button
              variant="outline"
              size="icon"
              className="h-7 w-7"
              onClick={() => setZoom(Math.min(200, zoom + 25))}
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-7 w-7"
              onClick={() => { setZoom(100); setSliderPosition(50); }}
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </Button>
          </div>
          
          {mode === 'slider' && (
            <div className="flex items-center gap-2 flex-1">
              <span className="text-xs text-muted-foreground">位置</span>
              <Slider
                value={[sliderPosition]}
                onValueChange={([v]) => setSliderPosition(v)}
                min={0}
                max={100}
                className="w-32"
              />
            </div>
          )}
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="p-2 bg-muted/30 rounded-lg">
            <p className="text-muted-foreground">原文件大小</p>
            <p className="font-medium">{formatFileSize(originalSize)}</p>
            {originalWidth && originalHeight && (
              <p className="text-muted-foreground">{originalWidth} × {originalHeight}</p>
            )}
          </div>
          <div className="p-2 bg-muted/30 rounded-lg">
            <p className="text-muted-foreground">处理后大小</p>
            <p className="font-medium">{formatFileSize(processedSize || 0)}</p>
            {processedWidth && processedHeight && (
              <p className="text-muted-foreground">{processedWidth} × {processedHeight}</p>
            )}
          </div>
          <div className={`p-2 rounded-lg ${sizeDiff < 0 ? 'bg-green-500/10' : 'bg-orange-500/10'}`}>
            <p className="text-muted-foreground">变化</p>
            <p className={`font-medium ${sizeDiff < 0 ? 'text-green-600' : 'text-orange-600'}`}>
              {sizeDiff > 0 ? '+' : ''}{sizeDiff.toFixed(1)}%
            </p>
            <p className="text-muted-foreground">
              {sizeDiff < 0 ? '节省空间' : '体积增加'}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
