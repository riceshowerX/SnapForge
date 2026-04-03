<div align="center">

# <img src="public/logo.png" width="80" height="80" alt="SnapForge Logo"> SnapForge

### 专业图像处理平台

**一个功能强大的现代化图像处理平台，支持批量处理、格式转换、滤镜特效、水印添加、智能去重等完整图像处理工作流**

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

[在线演示](https://snapforge.dev.coze.site) · [English](README_EN.md) · [快速开始](#快速开始) · [功能特性](#功能特性) · [技术文档](#技术文档)

---

## 🎯 核心优势

| 特性 | 说明 |
|------|------|
| 🚀 **高性能** | 并发处理引擎，支持 1-10 张图片同时处理 |
| 🔒 **安全可靠** | Magic Number 文件验证、速率限制、路径遍历防护 |
| 📦 **批量处理** | 支持数百张图片批量处理，自动队列管理 |
| 🎨 **丰富滤镜** | 15+ 内置滤镜，支持自定义色彩调整 |
| 🧠 **智能去重** | 感知哈希算法，快速识别相似/重复图片 |
| 💾 **数据持久化** | 本地存储任务历史，处理方案云端同步 |

</div>

---

## ✨ 功能特性

### 🖼️ 图像处理核心

| 功能 | 描述 | 支持格式 |
|------|------|----------|
| **格式转换** | 主流格式互转，支持质量控制 | JPEG, PNG, WebP, AVIF, TIFF, GIF, BMP |
| **尺寸调整** | 智能缩放，多种适应模式 | 适应/填充/拉伸/裁剪 |
| **智能裁剪** | 自定义裁剪区域，预设比例 | 1:1, 16:9, 4:3, 3:2, 2:1, 自定义 |
| **旋转翻转** | 任意角度旋转，水平/垂直翻转 | - |
| **滤镜效果** | 15+ 专业滤镜一键应用 | 灰度、复古、锐化、模糊、浮雕等 |
| **色彩调整** | 精细调节亮度/对比度/饱和度 | 范围 0-10 |
| **水印添加** | 文字/图片水印，多种定位模式 | 9宫格 + 平铺 |
| **边框装饰** | 自定义边框宽度、颜色、圆角 | - |

### 🚀 高级功能

- **批量处理** - 一次性处理数百张图片，支持并发控制和错误中断选项
- **处理方案** - 5 种预设方案一键应用，支持自定义方案保存/导入/导出
- **重复检测** - 感知哈希算法，支持相似度阈值配置 (0.5-1.0)
- **统计分析** - 可视化仪表盘，追踪处理趋势、效率、成功率和功能使用排行
- **图片对比** - 滑块/叠加/并排三种对比模式，支持缩放和全屏查看
- **EXIF 信息** - 完整展示拍摄参数、焦距、光圈、ISO 等元数据

### 💻 用户体验

- **多种上传** - 支持拖拽上传、粘贴上传、点击上传
- **实时预览** - 处理效果即时可见，无需等待
- **快捷键支持** - Ctrl+V 粘贴、Ctrl+A 全选、Delete 删除、Ctrl+Enter 处理
- **批量下载** - 一键打包 ZIP 下载所有处理结果
- **主题切换** - 深色/浅色模式自动跟随系统
- **响应式设计** - 完美适配桌面、平板和移动设备

---

## 📸 界面预览

<details>
<summary>点击展开查看截图</summary>

### 主界面
![主界面](./screenshots/main.png)

### 处理配置面板
![配置面板](./screenshots/config.png)

### 图片对比
![图片对比](./screenshots/compare.png)

### 统计仪表盘
![统计仪表盘](./screenshots/stats.png)

</details>

---

## 🚀 快速开始

### 环境要求

| 环境 | 要求 |
|------|------|
| **Node.js** | >= 18.0 |
| **pnpm** | >= 9.0 |
| **操作系统** | Linux, macOS, Windows |

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# 2. 安装依赖
pnpm install

# 3. 启动开发服务器
pnpm dev

# 4. 打开浏览器访问
open http://localhost:5000
```

### 生产部署

```bash
# 1. 构建生产版本
pnpm build

# 2. 启动生产服务器
pnpm start

# 3. 服务器将运行在 http://localhost:5000
```

### 环境变量（可选）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务监听端口 | `5000` |

---

## 🏗️ 技术架构

### 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| **框架** | Next.js (App Router) | 16.1.1 |
| **UI 库** | React | 19.2.3 |
| **语言** | TypeScript | 5.0 |
| **样式** | Tailwind CSS + shadcn/ui | 4.0 |
| **状态管理** | Zustand (持久化) | - |
| **图像处理** | Sharp (libvips) | - |
| **图表** | Recharts | - |
| **打包下载** | JSZip | - |
| **唯一ID** | UUID | - |

### 项目结构

```
SnapForge/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── api/                     # API 路由
│   │   │   ├── upload/route.ts      # 文件上传接口
│   │   │   ├── process/route.ts     # 图像处理接口
│   │   │   └── duplicates/route.ts  # 重复检测接口
│   │   ├── layout.tsx               # 根布局
│   │   ├── page.tsx                 # 首页
│   │   └── globals.css              # 全局样式
│   │
│   ├── components/                   # React 组件
│   │   ├── ui/                      # shadcn/ui 基础组件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ... (更多组件)
│   │   │
│   │   ├── ImageUploader.tsx        # 图片上传组件
│   │   ├── ProcessConfigPanel.tsx   # 处理配置面板
│   │   ├── ProcessingPanel.tsx       # 处理面板（含并发控制）
│   │   ├── ImageCompare.tsx          # 图片对比组件
│   │   ├── ExifPanel.tsx            # EXIF 信息面板
│   │   ├── SchemeManager.tsx         # 方案管理组件
│   │   ├── StatsDashboard.tsx        # 统计仪表盘
│   │   ├── DuplicateDetector.tsx    # 重复检测组件
│   │   ├── ThemeToggle.tsx          # 主题切换
│   │   └── ProcessingHistory.tsx    # 处理历史
│   │
│   ├── lib/                         # 工具库
│   │   ├── image-processor.ts       # 图像处理核心逻辑
│   │   ├── utils.ts                 # 通用工具函数
│   │   ├── api-response.ts          # 统一 API 响应格式
│   │   └── rate-limit.ts            # 请求速率限制
│   │
│   ├── store/                       # 状态管理
│   │   └── index.ts                 # Zustand Store (持久化)
│   │
│   └── types/                        # TypeScript 类型定义
│       └── index.ts                  # 全局类型、接口定义
│
├── public/                           # 静态资源
│   └── logo.png                      # 项目图标
│
├── scripts/                          # 构建脚本
│   ├── build.sh
│   ├── dev.sh
│   └── start.sh
│
├── package.json                      # 项目配置
├── tsconfig.json                     # TypeScript 配置
├── .coze                            # Coze 部署配置
└── README.md                         # 项目文档
```

### 核心处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        图像处理管道                              │
├─────────────────────────────────────────────────────────────────┤
│  1. 验证 ──→ 2. 裁剪 ──→ 3. 旋转 ──→ 4. 缩放 ──→ 5. 特效       │
│  6. 滤镜 ──→ 7. 边框 ──→ 8. 水印 ──→ 9. 格式转换 ──→ 10. 输出  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 API 文档

### 统一响应格式

所有 API 响应采用统一的 JSON 格式：

```typescript
// 成功响应
{
  "success": true,
  "data": { ... },
  "timestamp": 1709900000000
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  },
  "timestamp": 1709900000000
}
```

### 错误码说明

| 错误码 | 说明 |
|--------|------|
| `UNKNOWN_ERROR` | 未知错误 |
| `INVALID_REQUEST` | 无效请求 |
| `FILE_TOO_LARGE` | 文件过大 |
| `INVALID_FILE_TYPE` | 无效文件类型 |
| `FILE_SIGNATURE_MISMATCH` | 文件内容与声明类型不符 |
| `INVALID_CONFIG` | 无效配置 |
| `PROCESSING_FAILED` | 处理失败 |
| `RATE_LIMIT_EXCEEDED` | 请求过于频繁 |

---

### POST /api/upload

上传图片并获取预览信息和元数据。

**请求**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 图片文件，最大 50MB |

**速率限制**: 30 次/分钟

**响应示例**:

```json
{
  "success": true,
  "data": {
    "name": "photo.jpg",
    "size": 2048000,
    "type": "image/jpeg",
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "hasAlpha": false,
    "preview": "data:image/jpeg;base64,..."
  },
  "timestamp": 1709900000000
}
```

---

### POST /api/process

处理单张图片。

**请求**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 图片文件，最大 50MB |
| `config` | string | ✅ | JSON 格式的处理配置 |
| `counter` | number | ❌ | 编号，用于批量命名 |

**速率限制**: 20 次/分钟

**响应**: 处理后的图片二进制数据

**响应头**:

```
Content-Type: image/[format]
Content-Disposition: attachment; filename="processed_1.jpg"
X-Image-Width: 1920
X-Image-Height: 1080
X-Image-Size: 1024000
```

---

### POST /api/duplicates

检测重复或相似的图片。

**请求**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | File[] | ✅ | 图片文件数组，最多 100 个 |
| `threshold` | number | ❌ | 相似度阈值 (0.5-1.0)，默认 0.9 |

**速率限制**: 10 次/分钟

**响应示例**:

```json
{
  "success": true,
  "data": {
    "groups": [
      {
        "id": "uuid-group-1",
        "images": [
          { "id": "uuid-1", "name": "photo1.jpg", "size": 2048, "type": "image/jpeg" },
          { "id": "uuid-2", "name": "photo2.jpg", "size": 2048, "type": "image/jpeg" }
        ],
        "similarity": 0.95,
        "hash": "perceptual_hash_value"
      }
    ],
    "totalScanned": 10,
    "duplicatesFound": 2
  },
  "timestamp": 1709900000000
}
```

---

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + V` | 从剪贴板粘贴图片 |
| `Ctrl + A` | 全选/取消全选图片 |
| `Delete` | 删除选中的图片 |
| `Ctrl + Enter` | 开始处理 |
| `Esc` | 关闭预览/弹窗 |

---

## 🔒 安全特性

### 文件安全

| 特性 | 说明 |
|------|------|
| **Magic Number 验证** | 通过文件头字节验证真实文件类型，防止伪装攻击 |
| **文件大小限制** | 单文件最大 50MB，总请求体最大 100MB |
| **安全文件名** | 移除路径遍历字符、Unicode 控制字符，限制长度 255 |
| **Unicode 规范化** | 防止 NFC/NFD 规范化攻击 |

### 请求安全

| 特性 | 说明 |
|------|------|
| **速率限制** | 基于 IP 的请求限流，不同接口独立限制 |
| **参数校验** | 所有配置参数严格范围校验 |
| **错误隔离** | 不暴露内部错误细节到客户端 |

### 数据安全

| 特性 | 说明 |
|------|------|
| **本地存储** | 数据仅存储在浏览器本地 localStorage |
| **数据精简** | 历史记录自动精简，移除大型二进制数据 |
| **容量管理** | 自动清理旧数据防止存储溢出 |

---

## ⚡ 性能优化

### 前端优化

| 优化项 | 实现方式 |
|--------|----------|
| **大图预览** | >2MB 图片自动生成 800x800 缩略图 |
| **并发处理** | 可配置 1-10 张图片同时处理 |
| **内存管理** | 使用 ref 跟踪 Blob URL，组件卸载时自动释放 |
| **状态优化** | 使用 zustand getState() 避免不必要的重渲染 |
| **批量获取** | 并行获取图片 blob，最多 10 个并发 |

### 后端优化

| 优化项 | 实现方式 |
|--------|----------|
| **流式处理** | 使用 Sharp 流式 API |
| **延迟加载** | 按需导入重型模块 |
| **缓存策略** | 禁用浏览器缓存确保数据最新 |

---

## 🔧 配置参考

### 处理配置结构

```typescript
interface ProcessConfig {
  convert: {
    enabled: boolean;
    format: 'jpeg' | 'png' | 'webp' | 'avif';
    quality: number;      // 1-100
    progressive: boolean;
    optimize: boolean;
  };
  resize: {
    enabled: boolean;
    width: number;        // 1-20000
    height: number;       // 1-20000
    mode: 'contain' | 'cover' | 'stretch' | 'fill';
    onlyShrink: boolean;
  };
  crop: {
    enabled: boolean;
    x: number;
    y: number;
    width: number;        // 1-50000
    height: number;       // 1-50000
    aspectRatio: string;
    preset: 'custom' | 'square' | '16:9' | '4:3' | '3:2' | '2:1';
  };
  rotate: {
    enabled: boolean;
    angle: number;
    expand: boolean;
    fillColor: string;
    flip: boolean;
    flop: boolean;
  };
  filter: {
    enabled: boolean;
    type: FilterType;
    intensity: number;    // 0-10
  };
  effects: {
    enabled: boolean;
    brightness: number;   // 0-10
    contrast: number;     // 0-10
    saturation: number;   // 0-10
  };
  watermark: {
    enabled: boolean;
    text: string;
    position: WatermarkPosition;
    opacity: number;
    fontSize: number;
    color: string;
  };
  border: {
    enabled: boolean;
    width: number;        // 0-100
    color: string;
    radius: number;
  };
  compression: {
    enabled: boolean;
    level: number;        // 1-100
  };
  preserveMetadata: boolean;
}
```

### 预设处理方案

| 方案名称 | 适用场景 | 主要配置 |
|----------|----------|----------|
| **Web 优化** | 网页图片 | WebP 格式，质量 85%，宽度 1920 |
| **缩略图** | 图册预览 | JPEG 格式，质量 75%，400x400 |
| **社交媒体** | 社交平台 | JPEG 格式，质量 90%，1080x1080 |
| **水印保护** | 版权保护 | 添加文字水印 |
| **打印输出** | 印刷品质 | PNG 格式，质量 100%，300 DPI |

---

## ❓ 常见问题

### Q: 上传图片失败？

**可能原因**:
1. 文件大小超过 50MB
2. 文件格式不支持
3. 网络连接中断
4. 请求过于频繁（触发速率限制）

**解决方案**:
- 压缩图片大小后重试
- 使用支持的格式（JPEG, PNG, WebP, GIF, BMP, TIFF）
- 等待 1 分钟后重试

### Q: 处理速度慢？

**可能原因**:
1. 图片文件过大
2. 启用了多项处理操作
3. 并发数量设置过低

**解决方案**:
- 使用处理方案预设为图片减肥
- 减少同时启用的处理选项
- 在设置中调高并发数量（默认 3）

### Q: 重复检测不准确？

**可能原因**:
1. 相似度阈值设置过高
2. 图片经过压缩或格式转换

**解决方案**:
- 降低相似度阈值（默认 0.9，可降至 0.7-0.8）
- 对于截图或二次压缩的图片，可使用更低的阈值

### Q: 深色模式不生效？

**解决方案**:
- 确认浏览器支持 prefers-color-scheme
- 手动点击右上角主题切换按钮

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发规范

```bash
# 1. 安装依赖
pnpm install

# 2. 创建功能分支
git checkout -b feature/my-feature

# 3. 编写代码（自动 ESLint + TypeScript 检查）
pnpm lint
pnpm ts-check

# 4. 提交代码（遵循 Conventional Commits）
git commit -m "feat: add new processing filter"

# 5. 推送并创建 PR
git push origin feature/my-feature
```

### 提交信息规范

```
feat:     新功能
fix:      Bug 修复
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 代码重构
perf:     性能优化
test:     测试相关
chore:    构建/工具相关
```

---

## 📝 更新日志

### [v1.1.0] - 2024-04

#### 新增功能
- ✨ 并发处理引擎，支持 1-10 张图片同时处理
- ✨ 统一的 API 响应格式和错误码规范
- ✨ 请求速率限制，防止滥用
- ✨ 增强的文件名安全处理（Unicode 规范化）

#### 优化改进
- 🚀 批量图片获取优化（并行 + 缓存）
- 🚀 使用 zustand getState() 优化渲染性能
- 🐛 修复 SchemeManager 水合不匹配问题
- 🐛 修复 ImageCompare 拖拽状态过期问题

#### 安全增强
- 🔒 添加请求速率限制（按接口独立限制）
- 🔒 增强路径遍历防护（Unicode 控制字符过滤）

### [v1.0.0] - 2024-01

- ✨ 初始版本发布
- 🖼️ 完整的图像处理功能（转换、裁剪、滤镜、水印等）
- 🎨 专业级 UI 设计
- 📊 统计分析仪表盘
- 🔧 处理方案管理
- 🔍 重复图片检测

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

感谢以下开源项目：

- [Next.js](https://nextjs.org/) - React 框架
- [Sharp](https://sharp.pixelmatter.com/) - 高性能图像处理
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先 CSS 框架
- [shadcn/ui](https://ui.shadcn.com/) - 美观的 UI 组件
- [Zustand](https://zustand-demo.pmnd.rs/) - 轻量状态管理

---

<div align="center">

**Made with ❤️ by [riceshowerX](https://github.com/riceshowerX)**

**如果你觉得这个项目有帮助，请给个 ⭐ 支持一下！**

[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

</div>
