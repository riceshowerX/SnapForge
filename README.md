<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="public/logo.png">
  <source media="(prefers-color-scheme: dark)" srcset="public/logo.png">
  <img src="public/logo.png" width="120" height="120" alt="SnapForge" style="border-radius: 24px;">
</picture>

# SnapForge

### 专业图像处理平台

**一个功能强大的现代化图像处理平台，支持批量处理、格式转换、滤镜特效、水印添加、智能去重等完整图像处理工作流**

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

[English](README_EN.md) · [快速开始](#快速开始) · [功能特性](#功能特性) · [技术架构](#技术架构)

---

## 核心优势

| 特性 | 说明 |
|------|------|
| 🚀 **高性能** | 并发处理引擎，支持 1-10 张图片同时处理 |
| 🔒 **安全可靠** | Magic Number 文件验证、速率限制、路径遍历防护 |
| 📦 **批量处理** | 支持数百张图片批量处理，自动队列管理 |
| 🎨 **丰富滤镜** | 15+ 内置滤镜，支持自定义色彩调整 |
| 🧠 **智能去重** | 感知哈希算法，快速识别相似/重复图片 |
| 🌐 **双语支持** | 中文/英文界面一键切换 |

---

## 功能特性

### 图像处理核心

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

### 高级功能

- **批量处理** - 一次性处理数百张图片，支持并发控制和错误中断选项
- **处理方案** - 预设方案一键应用，支持自定义方案保存/导入/导出
- **重复检测** - 感知哈希算法，支持相似度阈值配置
- **统计分析** - 可视化仪表盘，追踪处理趋势、效率、成功率
- **图片对比** - 滑块/叠加/并排三种对比模式，支持缩放和全屏
- **EXIF 信息** - 完整展示拍摄参数、元数据

### 用户体验

- **多种上传** - 支持拖拽上传、粘贴上传、点击上传
- **实时预览** - 处理效果即时可见
- **快捷键支持** - Ctrl+V 粘贴、Ctrl+A 全选、Delete 删除
- **批量下载** - 一键打包 ZIP 下载
- **主题切换** - 深色/浅色模式跟随系统
- **响应式设计** - 适配桌面、平板和移动设备

---

## 快速开始

### 环境要求

| 环境 | 要求 |
|------|------|
| **Node.js** | >= 18.0 |
| **pnpm** | >= 9.0 |

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 打开浏览器访问 http://localhost:5000
```

### 生产部署

```bash
# 构建生产版本
pnpm build

# 启动生产服务器
pnpm start
```

---

## 技术架构

### 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| **框架** | Next.js (App Router) | 16.1.1 |
| **UI 库** | React | 19.2.3 |
| **语言** | TypeScript | 5.0 |
| **样式** | Tailwind CSS + shadcn/ui | 4.0 |
| **状态管理** | Zustand (持久化) | - |
| **图像处理** | Sharp (libvips) | - |

### 项目结构

```
SnapForge/
├── src/
│   ├── app/
│   │   ├── api/                  # API 路由
│   │   ├── layout.tsx             # 根布局
│   │   └── page.tsx               # 首页
│   ├── components/
│   │   ├── ui/                    # shadcn/ui 基础组件
│   │   ├── ImageUploader.tsx       # 图片上传
│   │   ├── ProcessConfigPanel.tsx # 处理配置
│   │   ├── ProcessingPanel.tsx     # 处理面板
│   │   ├── ImageCompare.tsx       # 图片对比
│   │   ├── DuplicateDetector.tsx   # 重复检测
│   │   └── StatsDashboard.tsx     # 统计仪表盘
│   ├── lib/
│   │   ├── image-processor.ts     # 图像处理核心
│   │   ├── i18n.ts                # 国际化
│   │   └── utils.ts               # 工具函数
│   ├── store/                     # 状态管理
│   └── types/                     # TypeScript 类型
├── public/                        # 静态资源
├── package.json
├── tailwind.config.ts
└── README.md
```

---

## 安全特性

- **Magic Number 验证** - 文件头字节验证真实文件类型
- **文件大小限制** - 单文件最大 50MB
- **安全文件名** - 移除路径遍历字符
- **速率限制** - 防止滥用

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

---

<p align="center">
  由 <a href="https://github.com/riceshowerX">riceshowerX</a> ❤️ 构建
</p>
</div>
