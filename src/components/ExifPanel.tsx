'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Camera,
  Aperture,
  Clock,
  MapPin,
  Maximize,
  FileImage,
  Info,
  ChevronDown,
  ChevronRight,
  Copy,
  Check
} from 'lucide-react';
import { ImageFile, ExifData, formatFileSize } from '@/types';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ExifPanelProps {
  image: ImageFile | null;
}

interface ExifItem {
  label: string;
  value: string;
  icon?: React.ReactNode;
  category: 'basic' | 'camera' | 'advanced';
}

function parseExifValue(key: string, value: unknown): string {
  if (value === undefined || value === null) return '-';
  
  switch (key) {
    case 'exposureTime':
      return typeof value === 'string' && value.includes('/') 
        ? value 
        : `${value}s`;
    case 'fNumber':
      return `f/${value}`;
    case 'focalLength':
      return `${value}mm`;
    case 'iso':
      return `ISO ${value}`;
    case 'xResolution':
    case 'yResolution':
      return `${value} DPI`;
    default:
      return String(value);
  }
}

function ExifSection({ 
  title, 
  items, 
  defaultOpen = true 
}: { 
  title: string; 
  items: ExifItem[];
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  if (items.length === 0) return null;
  
  return (
    <div className="space-y-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full text-left"
      >
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        )}
        <span className="text-sm font-medium">{title}</span>
        <Badge variant="secondary" className="h-4 px-1.5 text-[10px]">
          {items.length}
        </Badge>
      </button>
      
      {isOpen && (
        <div className="space-y-1 pl-6">
          {items.map((item, i) => (
            <ExifRow key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function ExifRow({ item }: { item: ExifItem }) {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(item.value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  
  return (
    <div className="flex items-center justify-between py-1.5 group">
      <div className="flex items-center gap-2 min-w-0">
        {item.icon && (
          <span className="text-muted-foreground shrink-0">{item.icon}</span>
        )}
        <span className="text-xs text-muted-foreground truncate">{item.label}</span>
      </div>
      <div className="flex items-center gap-1">
        <span className="text-xs font-medium truncate max-w-[150px]">{item.value}</span>
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="w-3 h-3 text-green-500" />
          ) : (
            <Copy className="w-3 h-3" />
          )}
        </Button>
      </div>
    </div>
  );
}

export function ExifPanel({ image }: ExifPanelProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [exifData, setExifData] = useState<ExifData | null>(null);

  useEffect(() => {
    if (!image) {
      setExifData(null);
      return;
    }

    const fetchExif = async () => {
      setIsLoading(true);
      try {
        // 实际项目中应从后端获取 EXIF 数据
        // 这里使用模拟数据
        setExifData(null);
      } catch (error) {
        console.error('Failed to fetch EXIF:', error);
        setExifData(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchExif();
  }, [image]);

  if (!image) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">选择图片查看详细信息</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 构建基本信息
  const basicItems: ExifItem[] = [
    {
      label: '文件名',
      value: image.name,
      icon: <FileImage className="w-3.5 h-3.5" />,
      category: 'basic',
    },
    {
      label: '文件大小',
      value: formatFileSize(image.size),
      icon: <FileImage className="w-3.5 h-3.5" />,
      category: 'basic',
    },
    ...(image.width && image.height ? [{
      label: '尺寸',
      value: `${image.width} × ${image.height}`,
      icon: <Maximize className="w-3.5 h-3.5" />,
      category: 'basic' as const,
    }] : []),
    {
      label: '类型',
      value: image.type || 'unknown',
      category: 'basic',
    },
  ];

  // 构建 EXIF 信息
  const cameraItems: ExifItem[] = exifData ? [
    ...(exifData.make ? [{
      label: '制造商',
      value: exifData.make,
      icon: <Camera className="w-3.5 h-3.5" />,
      category: 'camera' as const,
    }] : []),
    ...(exifData.model ? [{
      label: '型号',
      value: exifData.model,
      icon: <Camera className="w-3.5 h-3.5" />,
      category: 'camera' as const,
    }] : []),
    ...(exifData.fNumber ? [{
      label: '光圈',
      value: parseExifValue('fNumber', exifData.fNumber),
      icon: <Aperture className="w-3.5 h-3.5" />,
      category: 'camera' as const,
    }] : []),
    ...(exifData.exposureTime ? [{
      label: '快门',
      value: parseExifValue('exposureTime', exifData.exposureTime),
      category: 'camera' as const,
    }] : []),
    ...(exifData.iso ? [{
      label: 'ISO',
      value: parseExifValue('iso', exifData.iso),
      category: 'camera' as const,
    }] : []),
    ...(exifData.focalLength ? [{
      label: '焦距',
      value: parseExifValue('focalLength', exifData.focalLength),
      category: 'camera' as const,
    }] : []),
  ] : [];

  const advancedItems: ExifItem[] = exifData ? [
    ...(exifData.dateTime ? [{
      label: '拍摄时间',
      value: exifData.dateTime,
      icon: <Clock className="w-3.5 h-3.5" />,
      category: 'advanced' as const,
    }] : []),
    ...(exifData.gps?.latitude && exifData.gps?.longitude ? [{
      label: 'GPS',
      value: `${exifData.gps.latitude.toFixed(4)}, ${exifData.gps.longitude.toFixed(4)}`,
      icon: <MapPin className="w-3.5 h-3.5" />,
      category: 'advanced' as const,
    }] : []),
    ...(exifData.software ? [{
      label: '软件',
      value: exifData.software,
      category: 'advanced' as const,
    }] : []),
    ...(exifData.xResolution ? [{
      label: 'X 分辨率',
      value: parseExifValue('xResolution', exifData.xResolution),
      category: 'advanced' as const,
    }] : []),
    ...(exifData.colorSpace ? [{
      label: '色彩空间',
      value: exifData.colorSpace,
      category: 'advanced' as const,
    }] : []),
  ] : [];

  const hasExif = cameraItems.length > 0 || advancedItems.length > 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center justify-between">
          <span>图片信息</span>
          {hasExif && (
            <Badge variant="outline" className="text-xs font-normal">
              EXIF
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        {/* 预览图 */}
        <div className="relative aspect-video bg-muted/30 rounded-lg overflow-hidden mb-4">
          {image.preview ? (
            <Image
              src={image.preview}
              alt={image.name}
              fill
              className="object-contain"
              unoptimized
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <FileImage className="w-8 h-8 text-muted-foreground" />
            </div>
          )}
        </div>

        <ScrollArea className="h-[300px] pr-3">
          <div className="space-y-4">
            <ExifSection title="基本信息" items={basicItems} />
            
            {hasExif && (
              <>
                <Separator />
                <ExifSection title="拍摄信息" items={cameraItems} />
                <ExifSection title="高级信息" items={advancedItems} defaultOpen={false} />
              </>
            )}

            {!hasExif && (
              <div className="text-center py-4 text-muted-foreground text-xs">
                <Info className="w-4 h-4 mx-auto mb-1" />
                <p>此图片无 EXIF 元数据</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
