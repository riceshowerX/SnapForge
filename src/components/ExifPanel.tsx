'use client';

import { useState, useEffect, useCallback } from 'react';
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
  Check,
} from 'lucide-react';
import { ImageFile, ExifData, formatFileSize } from '@/types';
import { getImageBlob } from '@/lib/blob-store';
import { useAppStore } from '@/store';
import { t } from '@/lib/i18n';
import exifr from 'exifr';

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

/** 将 exifr 解析结果映射为项目 ExifData 结构 */
function mapExifData(parsed: Record<string, unknown>): ExifData {
  const gpsLat = typeof parsed.GPSLatitude === 'number' ? parsed.GPSLatitude : undefined;
  const gpsLon =
    typeof parsed.GPSLongitude === 'number' ? parsed.GPSLongitude : undefined;

  return {
    make: typeof parsed.Make === 'string' ? parsed.Make : undefined,
    model: typeof parsed.Model === 'string' ? parsed.Model : undefined,
    software:
      typeof parsed.Software === 'string' ? parsed.Software : undefined,
    dateTime:
      typeof parsed.DateTimeOriginal === 'string'
        ? parsed.DateTimeOriginal
        : undefined,
    exposureTime:
      typeof parsed.ExposureTime === 'string' ||
      typeof parsed.ExposureTime === 'number'
        ? String(parsed.ExposureTime)
        : undefined,
    fNumber:
      typeof parsed.FNumber === 'number' ? parsed.FNumber : undefined,
    iso: typeof parsed.ISO === 'number' ? parsed.ISO : undefined,
    focalLength:
      typeof parsed.FocalLength === 'number' ? parsed.FocalLength : undefined,
    gps:
      gpsLat !== undefined && gpsLon !== undefined
        ? { latitude: gpsLat, longitude: gpsLon }
        : undefined,
    orientation:
      typeof parsed.Orientation === 'number' ? parsed.Orientation : undefined,
    xResolution:
      typeof parsed.XResolution === 'number' ? parsed.XResolution : undefined,
    yResolution:
      typeof parsed.YResolution === 'number' ? parsed.YResolution : undefined,
    colorSpace:
      typeof parsed.ColorSpace === 'number'
        ? parsed.ColorSpace === 1
          ? 'sRGB'
          : String(parsed.ColorSpace)
        : undefined,
  };
}

function ExifSection({
  title,
  items,
  defaultOpen = true,
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

  // Q-06：setTimeout 用 useEffect 清理，避免卸载后 setState
  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 1500);
    return () => clearTimeout(timer);
  }, [copied]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(item.value);
      setCopied(true);
    } catch {
      // 剪贴板不可用时静默失败
    }
  };

  return (
    <div className="flex items-center justify-between py-1.5 group">
      <div className="flex items-center gap-2 min-w-0">
        {item.icon && (
          <span className="text-muted-foreground shrink-0">{item.icon}</span>
        )}
        <span className="text-xs text-muted-foreground truncate">
          {item.label}
        </span>
      </div>
      <div className="flex items-center gap-1">
        <span className="text-xs font-medium truncate max-w-[150px]">
          {item.value}
        </span>
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
  const { language } = useAppStore();
  const [exifData, setExifData] = useState<ExifData | null>(null);

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  // F-04：前端 exifr 解析真实 EXIF 数据（Q-06：带取消标记，防 setState after unmount）
  // 注意：初始状态即为 null；切换图片时由父组件以 key={image.id} 重新挂载本组件，
  // 避免在 effect 体内同步 setState。
  useEffect(() => {
    let cancelled = false;

    if (!image) return;

    const run = async () => {
      try {
        const blob = await getImageBlob(image);
        if (!blob || cancelled) return;

        const parsed = await exifr.parse(blob, {
          pick: [
            'Make',
            'Model',
            'Software',
            'DateTimeOriginal',
            'ExposureTime',
            'FNumber',
            'ISO',
            'FocalLength',
            'GPSLatitude',
            'GPSLongitude',
            'Orientation',
            'XResolution',
            'YResolution',
            'ColorSpace',
          ],
        });

        if (cancelled) return;
        if (parsed && typeof parsed === 'object') {
          setExifData(mapExifData(parsed as Record<string, unknown>));
        } else {
          setExifData(null);
        }
      } catch (err) {
        console.warn('Failed to parse EXIF:', err);
        if (!cancelled) setExifData(null);
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [image]);

  if (!image) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">{tr('selectImageHint')}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 构建基本信息
  const basicItems: ExifItem[] = [
    {
      label: tr('fileName'),
      value: image.name,
      icon: <FileImage className="w-3.5 h-3.5" />,
      category: 'basic',
    },
    {
      label: tr('fileSize'),
      value: formatFileSize(image.size),
      icon: <FileImage className="w-3.5 h-3.5" />,
      category: 'basic',
    },
    ...(image.width && image.height
      ? [
          {
            label: tr('dimensions'),
            value: `${image.width} × ${image.height}`,
            icon: <Maximize className="w-3.5 h-3.5" />,
            category: 'basic' as const,
          },
        ]
      : []),
    {
      label: tr('type'),
      value: image.type || 'unknown',
      category: 'basic',
    },
  ];

  // 构建 EXIF 信息
  const cameraItems: ExifItem[] = exifData
    ? [
        ...(exifData.make
          ? [
              {
                label: tr('manufacturer'),
                value: exifData.make,
                icon: <Camera className="w-3.5 h-3.5" />,
                category: 'camera' as const,
              },
            ]
          : []),
        ...(exifData.model
          ? [
              {
                label: tr('model'),
                value: exifData.model,
                icon: <Camera className="w-3.5 h-3.5" />,
                category: 'camera' as const,
              },
            ]
          : []),
        ...(exifData.fNumber
          ? [
              {
                label: tr('aperture'),
                value: parseExifValue('fNumber', exifData.fNumber),
                icon: <Aperture className="w-3.5 h-3.5" />,
                category: 'camera' as const,
              },
            ]
          : []),
        ...(exifData.exposureTime
          ? [
              {
                label: tr('shutter'),
                value: parseExifValue('exposureTime', exifData.exposureTime),
                category: 'camera' as const,
              },
            ]
          : []),
        ...(exifData.iso
          ? [
              {
                label: tr('iso'),
                value: parseExifValue('iso', exifData.iso),
                category: 'camera' as const,
              },
            ]
          : []),
        ...(exifData.focalLength
          ? [
              {
                label: tr('focalLength'),
                value: parseExifValue('focalLength', exifData.focalLength),
                category: 'camera' as const,
              },
            ]
          : []),
      ]
    : [];

  const advancedItems: ExifItem[] = exifData
    ? [
        ...(exifData.dateTime
          ? [
              {
                label: tr('dateTaken'),
                value: exifData.dateTime,
                icon: <Clock className="w-3.5 h-3.5" />,
                category: 'advanced' as const,
              },
            ]
          : []),
        ...(exifData.gps?.latitude !== undefined &&
        exifData.gps?.longitude !== undefined
          ? [
              {
                label: tr('gps'),
                value: `${exifData.gps.latitude.toFixed(4)}, ${exifData.gps.longitude.toFixed(4)}`,
                icon: <MapPin className="w-3.5 h-3.5" />,
                category: 'advanced' as const,
              },
            ]
          : []),
        ...(exifData.software
          ? [
              {
                label: tr('software'),
                value: exifData.software,
                category: 'advanced' as const,
              },
            ]
          : []),
        ...(exifData.xResolution
          ? [
              {
                label: tr('xResolution'),
                value: parseExifValue('xResolution', exifData.xResolution),
                category: 'advanced' as const,
              },
            ]
          : []),
        ...(exifData.colorSpace
          ? [
              {
                label: tr('colorSpace'),
                value: exifData.colorSpace,
                category: 'advanced' as const,
              },
            ]
          : []),
      ]
    : [];

  const hasExif = cameraItems.length > 0 || advancedItems.length > 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center justify-between">
          <span>{tr('imageInfo')}</span>
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
            <ExifSection title={tr('basicInfo')} items={basicItems} />

            {hasExif && (
              <>
                <Separator />
                <ExifSection title={tr('cameraInfo')} items={cameraItems} />
                <ExifSection
                  title={tr('advancedInfo')}
                  items={advancedItems}
                  defaultOpen={false}
                />
              </>
            )}

            {!hasExif && (
              <div className="text-center py-4 text-muted-foreground text-xs">
                <Info className="w-4 h-4 mx-auto mb-1" />
                <p>{tr('noExif')}</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
