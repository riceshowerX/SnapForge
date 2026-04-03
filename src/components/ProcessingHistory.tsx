'use client';

import { useAppStore } from '@/store';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { History, Trash2, Download, Clock, CheckCircle, XCircle, Image as ImageIcon } from 'lucide-react';
import Image from 'next/image';

export function ProcessingHistory() {
  const { taskHistory } = useAppStore();

  const formatDuration = (start: number, end: number) => {
    const seconds = Math.floor((end - start) / 1000);
    if (seconds < 60) return `${seconds}秒`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}分${remainingSeconds}秒`;
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (taskHistory.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-muted-foreground p-4">
        <History className="w-10 h-10 mb-3 opacity-50" />
        <p className="text-sm">暂无处理历史</p>
        <p className="text-xs mt-1">处理图片后显示记录</p>
      </div>
    );
  }

  return (
    <div className="p-3 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm flex items-center gap-1.5">
          <History className="w-4 h-4" />
          处理历史
        </h3>
        <Badge variant="secondary" className="text-[10px]">
          {taskHistory.length} 条记录
        </Badge>
      </div>

      <div className="space-y-2 max-h-96 overflow-auto">
        {taskHistory.map((task) => {
          const successCount = task.results.filter(r => r.status === 'success').length;
          const errorCount = task.results.filter(r => r.status === 'error').length;
          const total = task.results.length;

          return (
            <Card key={task.id} className="p-2.5">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <ImageIcon className="w-3.5 h-3.5 text-muted-foreground" />
                  <span className="text-xs font-medium">{total} 张图片</span>
                </div>
                <div className="flex items-center gap-1">
                  {successCount > 0 && (
                    <Badge variant="outline" className="h-4 px-1.5 text-[10px] text-green-600 border-green-200">
                      <CheckCircle className="w-2.5 h-2.5 mr-0.5" />
                      {successCount}
                    </Badge>
                  )}
                  {errorCount > 0 && (
                    <Badge variant="outline" className="h-4 px-1.5 text-[10px] text-red-600 border-red-200">
                      <XCircle className="w-2.5 h-2.5 mr-0.5" />
                      {errorCount}
                    </Badge>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatTime(task.startTime!)}
                </div>
                {task.startTime && task.endTime && (
                  <span>耗时 {formatDuration(task.startTime, task.endTime)}</span>
                )}
              </div>

              {/* 缩略图预览 */}
              <div className="mt-2 flex flex-wrap gap-1">
                {task.files.slice(0, 5).map((file) => (
                  <div key={file.id} className="relative w-8 h-8 rounded overflow-hidden border">
                    {file.preview ? (
                      <Image
                        src={file.preview}
                        alt={file.name}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    ) : (
                      <div className="w-full h-full bg-muted" />
                    )}
                  </div>
                ))}
                {task.files.length > 5 && (
                  <div className="w-8 h-8 rounded bg-muted flex items-center justify-center text-[10px] text-muted-foreground border">
                    +{task.files.length - 5}
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
