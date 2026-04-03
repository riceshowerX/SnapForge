'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Image as ImageIcon,
  Clock,
  HardDrive,
  Activity,
  BarChart2,
  PieChart as PieChartIcon,
  RotateCcw
} from 'lucide-react';
import { useAppStore } from '@/store';
import { formatFileSize, formatDuration, ProcessingStats } from '@/types';
import type { BatchTask, ProcessResult, ImageFile } from '@/types';

// 图表颜色
const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

export function StatsDashboard() {
  const { taskHistory, images } = useAppStore();
  const [activeChart, setActiveChart] = useState<'bar' | 'pie' | 'area'>('bar');

  // 计算统计数据
  const stats = calculateStats(taskHistory, images);

  // 处理趋势数据（最近7天）
  const trendData = generateTrendData(taskHistory);

  // 功能使用分布
  const featureUsage = calculateFeatureUsage(taskHistory);

  return (
    <div className="space-y-4">
      {/* 关键指标卡片 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="已处理图片"
          value={stats.totalProcessed.toString()}
          subtitle={`共 ${stats.totalImages} 张上传`}
          icon={<ImageIcon className="w-4 h-4" />}
          trend={stats.totalProcessed > 0 ? 'up' : 'neutral'}
          trendValue={stats.totalProcessed > 0 ? `+${stats.totalProcessed}` : '暂无'}
        />
        <MetricCard
          title="节省空间"
          value={formatFileSize(stats.totalSizeSaved)}
          subtitle="通过压缩优化"
          icon={<HardDrive className="w-4 h-4" />}
          trend={stats.totalSizeSaved > 0 ? 'up' : 'neutral'}
          trendValue={stats.totalSizeSaved > 0 ? '优化有效' : '暂无'}
        />
        <MetricCard
          title="平均处理时间"
          value={formatDuration(stats.averageProcessingTime)}
          subtitle="单张图片"
          icon={<Clock className="w-4 h-4" />}
          trend={stats.averageProcessingTime < 1000 ? 'up' : 'neutral'}
          trendValue={stats.averageProcessingTime < 1000 ? '快速' : '正常'}
        />
        <MetricCard
          title="成功率"
          value={`${stats.successRate.toFixed(1)}%`}
          subtitle="处理成功比例"
          icon={<Activity className="w-4 h-4" />}
          trend={stats.successRate >= 95 ? 'up' : stats.successRate >= 80 ? 'neutral' : 'down'}
          trendValue={stats.successRate >= 95 ? '优秀' : stats.successRate >= 80 ? '良好' : '需关注'}
        />
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 处理趋势 */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">处理趋势</CardTitle>
              <div className="flex items-center gap-1">
                <Button
                  variant={activeChart === 'bar' ? 'secondary' : 'ghost'}
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setActiveChart('bar')}
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                </Button>
                <Button
                  variant={activeChart === 'area' ? 'secondary' : 'ghost'}
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setActiveChart('area')}
                >
                  <Activity className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
            <CardDescription className="text-xs">最近7天处理量</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="h-[200px]">
              {trendData.length > 0 ? (
                activeChart === 'bar' ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                      <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                      <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="count"
                        stroke="#8b5cf6"
                        fill="url(#colorGradient)"
                        strokeWidth={2}
                      />
                      <defs>
                        <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                    </AreaChart>
                  </ResponsiveContainer>
                )
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
                  暂无处理数据
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 功能使用分布 */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <PieChartIcon className="w-4 h-4" />
              功能使用分布
            </CardTitle>
            <CardDescription className="text-xs">各功能使用次数统计</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="h-[200px] flex items-center justify-center">
              {featureUsage.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={featureUsage}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {featureUsage.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-muted-foreground text-sm">
                  暂无功能使用数据
                </div>
              )}
            </div>
            {featureUsage.length > 0 && (
              <div className="flex flex-wrap gap-2 justify-center mt-2">
                {featureUsage.slice(0, 6).map((item, index) => (
                  <div key={item.name} className="flex items-center gap-1.5">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="text-xs text-muted-foreground">{item.name}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 最近任务 */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">最近任务</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => useAppStore.getState().clearTaskHistory()}
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              清空历史
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[150px]">
            {taskHistory.length > 0 ? (
              <div className="space-y-2">
                {taskHistory.slice(0, 5).map((task) => {
                  const successCount = task.results.filter(r => r.status === 'success').length;
                  const totalCount = task.results.length;
                  const duration = task.endTime && task.startTime
                    ? task.endTime - task.startTime
                    : 0;

                  return (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-2 rounded-lg bg-muted/30"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center">
                          <ImageIcon className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm font-medium">
                            {totalCount} 张图片
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(task.startTime || 0).toLocaleString('zh-CN')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-xs">
                        <div className="text-right">
                          <p className="font-medium">{successCount}/{totalCount} 成功</p>
                          <p className="text-muted-foreground">{formatDuration(duration)}</p>
                        </div>
                        <Badge
                          variant={successCount === totalCount ? 'default' : 'secondary'}
                          className="h-5"
                        >
                          {successCount === totalCount ? '完成' : '部分成功'}
                        </Badge>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
                暂无处理历史
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

// 指标卡片
function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
}) {
  return (
    <Card>
      <CardContent className="pt-3 pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{title}</p>
            <p className="text-xl font-bold">{value}</p>
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              {icon}
            </div>
            {trend !== 'neutral' && (
              <div className={`flex items-center gap-0.5 text-xs ${
                trend === 'up' ? 'text-green-500' : 'text-red-500'
              }`}>
                {trend === 'up' ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {trendValue}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// 计算统计数据
function calculateStats(taskHistory: BatchTask[], images: ImageFile[]): ProcessingStats {
  let totalProcessed = 0;
  const totalSizeSaved = 0;
  let totalProcessingTime = 0;
  let successCount = 0;
  let totalAttempts = 0;

  taskHistory.forEach(task => {
    task.results.forEach((result: ProcessResult) => {
      totalAttempts++;
      if (result.status === 'success') {
        successCount++;
        if (result.processingTime) {
          totalProcessingTime += result.processingTime;
        }
      }
    });
    totalProcessed += task.results.length;
  });

  return {
    totalProcessed,
    totalImages: images.length,
    totalSizeSaved,
    averageProcessingTime: successCount > 0 ? totalProcessingTime / successCount : 0,
    successRate: totalAttempts > 0 ? (successCount / totalAttempts) * 100 : 0,
    mostUsedFeatures: [],
    processingHistory: [],
  };
}

// 生成趋势数据
function generateTrendData(taskHistory: BatchTask[]) {
  const days: { [key: string]: number } = {};
  
  // 初始化最近7天
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const key = date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    days[key] = 0;
  }

  // 统计每天处理量
  taskHistory.forEach(task => {
    if (task.startTime) {
      const date = new Date(task.startTime);
      const key = date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
      if (key in days) {
        days[key] += task.results.length;
      }
    }
  });

  return Object.entries(days).map(([date, count]) => ({ date, count }));
}

// 计算功能使用
function calculateFeatureUsage(taskHistory: BatchTask[]) {
  const features: { [key: string]: number } = {
    '格式转换': 0,
    '尺寸调整': 0,
    '裁剪': 0,
    '旋转': 0,
    '滤镜': 0,
    '水印': 0,
    '特效': 0,
    '边框': 0,
  };

  taskHistory.forEach(task => {
    if (task.config?.convert?.enabled) features['格式转换']++;
    if (task.config?.resize?.enabled) features['尺寸调整']++;
    if (task.config?.crop?.enabled) features['裁剪']++;
    if (task.config?.rotate?.enabled) features['旋转']++;
    if (task.config?.filter?.enabled) features['滤镜']++;
    if (task.config?.watermark?.enabled) features['水印']++;
    if (task.config?.effects?.enabled) features['特效']++;
    if (task.config?.border?.enabled) features['边框']++;
  });

  return Object.entries(features)
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}
