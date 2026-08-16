# SnapForge 项目开发规范

## 1. 项目概览

**SnapForge** 是一个专业图像处理平台，支持批量处理、格式转换、滤镜特效、水印添加、智能去重等功能。

### 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Next.js 16 (App Router) |
| UI 库 | React 19 |
| 语言 | TypeScript 5 |
| 样式 | Tailwind CSS 4 + shadcn/ui |
| 状态管理 | Zustand (persist) |
| 图像处理 | Sharp (libvips) |
| 国际化 | 自定义 i18n (中文/英文) |
| 打包下载 | JSZip |

### 项目根目录

```
/workspace/projects/
```

---

## 2. 构建和测试命令

### 安装依赖

```bash
pnpm install
```

### 开发环境

```bash
pnpm dev
# 运行在 http://localhost:5000
```

### 生产构建

```bash
pnpm build
pnpm start
```

### 代码检查

```bash
pnpm lint      # ESLint 检查
pnpm ts-check  # TypeScript 类型检查
```

### 端口规范

- **开发端口**: 5000
- **生产端口**: 5000
- **HMR 端口**: 5000 (Next.js 内置)

---

## 3. 重要：图片数据存储说明

### image.url 和 image.preview 都是 data URL

**关键点**：上传后的图片存储在 `image.preview` 字段中，格式为 **data URL (base64)**，不是可 fetch 的 HTTP URL。

```typescript
// ❌ 错误：尝试 fetch data URL
const response = await fetch(image.url); // 会失败！

// ✅ 正确：直接解析 base64
const base64Data = image.preview.split(',')[1];
const binaryString = atob(base64Data);
const bytes = new Uint8Array(binaryString.length);
for (let i = 0; i < binaryString.length; i++) {
  bytes[i] = binaryString.charCodeAt(i);
}
const blob = new Blob([bytes], { type: image.type });
```

### 适用场景
- `ProcessingPanel` - 图片处理
- `DuplicateDetector` - 重复检测
- 任何需要将图片发送到后端 API 的场景

---

## 5. React 规范

- 使用函数组件 + Hooks
- 优先使用 `useCallback` 包装回调函数
- 避免在 `useEffect` 中直接调用 `setState`，使用延迟初始化
- 使用 `ref` 存储频繁变化的临时状态（如 dragging）
- 组件卸载时清理副作用（URLs、定时器、事件监听）

### 国际化 (i18n) 规范

项目支持中文（默认）和英文界面。

```typescript
// 1. 导入翻译函数
import { t } from '@/lib/i18n';

// 2. 从 store 获取当前语言
const { language } = useAppStore();

// 3. 使用翻译
const tr = useCallback((key: keyof Translations) => t(language, key), [language]);

// 4. 在组件中使用
<span>{tr('upload')}</span>

// 5. 简单文本可使用三元表达式
{language === 'zh' ? '中文' : 'English'}
```

语言切换存储在 `useAppStore` 的 `language` 字段中，会自动持久化到 localStorage。

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `ProcessingPanel.tsx` |
| Hooks | camelCase, use 前缀 | `useAppStore.ts` |
| 类型 | PascalCase | `ImageFile`, `ProcessConfig` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_FILE_SIZE` |
| 函数 | camelCase | `handleClick`, `processImages` |

### 导入顺序

```typescript
// 1. React 和框架
import { useState, useCallback } from 'react';

// 2. shadcn/ui 组件
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// 3. Lucide 图标
import { Sparkles, Download } from 'lucide-react';

// 4. 项目组件
import { ProcessingPanel } from '@/components/ProcessingPanel';

// 5. 项目工具/类型
import { useAppStore } from '@/store';
import type { ProcessConfig } from '@/types';

// 6. 第三方库
import JSZip from 'jszip';
```

---

## 6. 组件规范

### 文件结构

```
src/components/
├── ui/                      # shadcn/ui 基础组件
│   ├── button.tsx
│   ├── card.tsx
│   └── dialog.tsx
├── ImageUploader.tsx       # 图片上传
├── ProcessingPanel.tsx      # 处理面板
├── ProcessConfigPanel.tsx  # 配置面板
├── ImageCompare.tsx         # 图片对比
├── ExifPanel.tsx           # EXIF 信息
├── SchemeManager.tsx       # 方案管理
├── StatsDashboard.tsx      # 统计仪表盘
├── DuplicateDetector.tsx   # 重复检测
├── ThemeToggle.tsx         # 主题切换
└── ProcessingHistory.tsx   # 处理历史
```

### 组件模板

```tsx
'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/store';

interface MyComponentProps {
  title: string;
  onComplete?: () => void;
}

export function MyComponent({ title, onComplete }: MyComponentProps) {
  const { data, updateData } = useAppStore();
  
  const handleAction = useCallback(() => {
    // 业务逻辑
    onComplete?.();
  }, [onComplete]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {/* 内容 */}
      </CardContent>
    </Card>
  );
}
```

---

## 7. API 设计规范

### 统一响应格式

```typescript
// src/lib/api-response.ts

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: number;
}
```

### 错误码规范

```typescript
// 通用错误 (1xxx)
UNKNOWN_ERROR: 'UNKNOWN_ERROR'
INVALID_REQUEST: 'INVALID_REQUEST'
MISSING_FIELD: 'MISSING_FIELD'

// 文件相关错误 (2xxx)
FILE_TOO_LARGE: 'FILE_TOO_LARGE'
INVALID_FILE_TYPE: 'INVALID_FILE_TYPE'
FILE_SIGNATURE_MISMATCH: 'FILE_SIGNATURE_MISMATCH'

// 配置相关错误 (3xxx)
INVALID_CONFIG: 'INVALID_CONFIG'
CONFIG_TOO_LARGE: 'CONFIG_TOO_LARGE'
CONFIG_PARAMS_OUT_OF_RANGE: 'CONFIG_PARAMS_OUT_OF_RANGE'

// 限流错误 (6xxx)
RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED'
```

### API 路由结构

```
src/app/api/
├── upload/route.ts      # POST - 上传图片
├── process/route.ts     # POST - 处理图片
└── duplicates/route.ts  # POST - 重复检测
```

### 速率限制

| 接口 | 限制 |
|------|------|
| `/api/upload` | 30 次/分钟 |
| `/api/process` | 20 次/分钟 |
| `/api/duplicates` | 10 次/分钟 |

---

## 6. 状态管理规范

### Zustand Store 结构

```typescript
// src/store/index.ts

interface AppState {
  // 状态
  images: ImageFile[];
  config: ProcessConfig;
  currentTask: BatchTask | null;
  taskHistory: BatchTask[];
  selectedImageIds: string[];
  isProcessing: boolean;
  
  // 方法
  addImages: (files: ImageFile[]) => void;
  removeImages: (ids: string[]) => void;
  updateConfig: <K extends keyof ProcessConfig>(key: K, value: ProcessConfig[K]) => void;
  // ...
}
```

### 持久化配置

- 使用 `zustand/middleware` 的 `persist` 中间件
- 自定义 `storage` 处理 localStorage 错误
- 任务历史通过 `stripLargeData()` 精简后存储
- 历史记录数量限制为 20 条

---

## 7. 安全规范

### 文件上传安全

1. **Magic Number 验证**: 通过文件头字节验证真实文件类型
2. **文件大小限制**: 单文件最大 50MB
3. **安全文件名**: 移除路径遍历字符和 Unicode 控制字符
4. **Unicode 规范化**: 防止 NFC/NFD 规范化攻击

### 文件名处理

```typescript
function sanitizeFilename(filename: string): string {
  let safe = filename.replace(/[\/\\]/g, '_');
  safe = safe.replace(/\.\./g, '');
  safe = safe.replace(/[<>:"|?*\x00-\x1f\x7f]/g, '_');
  safe = safe.normalize('NFC');
  safe = safe.trim().replace(/\s+/g, '_');
  return safe.slice(0, 255);
}
```

### 请求验证

- 所有配置参数严格范围校验
- 数值参数设置安全上下限
- 不暴露内部错误细节到客户端

---

## 8. 性能优化

### 前端优化

| 优化项 | 实现方式 |
|--------|----------|
| 大图预览 | >2MB 生成 800x800 缩略图 |
| 并发处理 | 可配置 1-10 张同时处理 |
| 内存管理 | ref 跟踪 Blob URL，卸载时释放 |
| 状态更新 | 使用 zustand getState() 避免重渲染 |
| 批量获取 | 并行 fetch，最多 10 个并发 |

### 关键代码模式

```tsx
// 1. 使用 ref 跟踪临时状态
const isDraggingRef = useRef(false);

// 2. 使用 getState() 获取最新状态
const processImages = useCallback(async () => {
  const { images, config } = useAppStore.getState();
  // ...
}, []);

// 3. 清理副作用
useEffect(() => {
  const urls = objectUrlsRef.current;
  return () => {
    urls.forEach(url => URL.revokeObjectURL(url));
  };
}, []);
```

---

## 9. 测试说明

### 手动测试清单

- [ ] 图片上传功能（拖拽、粘贴、点击）
- [ ] 格式转换（JPEG, PNG, WebP）
- [ ] 尺寸调整和裁剪
- [ ] 滤镜效果应用
- [ ] 水印添加
- [ ] 批量处理和并发控制
- [ ] 重复图片检测
- [ ] 统计仪表盘显示
- [ ] 方案保存/导入/导出
- [ ] 主题切换
- [ ] 快捷键功能
- [ ] 深色模式

### API 测试

```bash
# 上传测试
curl -X POST -F "file=@test.jpg" http://localhost:5000/api/upload

# 处理测试
curl -X POST -F "file=@test.jpg" -F "config={}" http://localhost:5000/api/process

# 重复检测测试
curl -X POST -F "files=@img1.jpg" -F "files=@img2.jpg" http://localhost:5000/api/duplicates
```

---

## 10. 常见问题修复

### Hydration 不匹配

**问题**: 服务端和客户端渲染结果不一致

**解决**: 使用延迟初始化或 `useEffect` 加载客户端数据

```tsx
// ❌ 错误
const [data, setData] = useState(() => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('key');
  }
  return null;
});

// ✅ 正确
const [data, setData] = useState(initialValue);

useEffect(() => {
  setData(localStorage.getItem('key'));
}, []);
```

### Stale 闭包问题

**问题**: 回调函数中读取到过期的状态值

**解决**: 使用 ref 存储频繁变化的状态

```tsx
// ❌ 错误
const handleMove = useCallback((e) => {
  if (isDragging) { // 可能是过期的值
    // ...
  }
}, [isDragging]);

// ✅ 正确
const isDraggingRef = useRef(false);
const handleMove = useCallback((e) => {
  if (isDraggingRef.current) {
    // ...
  }
}, []);
```

### 内存泄漏

**问题**: Blob URLs 未释放

**解决**: 组件卸载时清理

```tsx
useEffect(() => {
  const urls = objectUrlsRef.current;
  return () => {
    urls.forEach(url => URL.revokeObjectURL(url));
    urls.clear();
  };
}, []);
```

---

## 11. 部署说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | `5000` |

### 构建输出

- 开发: `pnpm dev` (热更新)
- 生产: `pnpm build` + `pnpm start`

### 目录权限

- `/workspace/projects/public/` - 可写入（上传文件）
- `/tmp/` - 临时文件目录
