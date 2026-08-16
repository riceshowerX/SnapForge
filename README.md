<div align="center">

<img src="public/logo.png" width="120" height="120" alt="SnapForge" style="border-radius: 24px; box-shadow: 0 6px 28px rgba(0,0,0,.10);" />

# SnapForge

**把图片处理做到极致 —— 批量处理 · 格式转换 · 滤镜特效 · 水印 · 智能去重**

一款完全本地运行的现代化图像处理工作台。无需注册、无需上传云端，所有图片都在你自己的机器上通过 **Sharp 引擎**高速处理，隐私数据永不离机。

[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=flat-square&logo=github&label=Stars)](https://github.com/riceshowerX/SnapForge/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/riceshowerX/SnapForge?style=flat-square&label=Last%20Commit)](https://github.com/riceshowerX/SnapForge/commits/main)
[![License](https://img.shields.io/github/license/riceshowerX/SnapForge?style=flat-square)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-000000.svg?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB.svg?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC.svg?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)

[English](README_EN.md) · [核心亮点](#-核心亮点) · [功能特性](#-功能特性) · [快速开始](#-快速开始) · [API 参考](#-api-参考) · [技术栈](#-技术栈) · [安全设计](#-安全设计) · [贡献指南](#-贡献指南)

</div>

---

## 🎯 核心亮点

| | |
|---|---|
| 🏠 **本地优先** | 所有处理在本机完成（Sharp 引擎），图片不上传任何服务器，隐私 100% 可控 |
| ⚡ **批量高效** | 一次处理数百张图片，1–10 路并发可调，实时进度反馈 |
| 🛡️ **安全加固** | SSRF 防护、Magic Number 校验、防解压炸弹、限流防滥用，生产级安全实践 |
| 🚀 **开箱即用** | 零配置启动，中文 / English 双语，深色 / 浅色主题，响应式适配全设备 |

---

## ✨ 功能特性

### 🖼️ 图像处理核心

| 功能 | 说明 | 支持格式 |
|------|------|----------|
| **格式转换** | 主流格式互转，支持质量与压缩控制 | JPEG, PNG, WebP, AVIF, TIFF, GIF, BMP |
| **尺寸调整** | 智能缩放：适应 / 填充 / 拉伸 / 裁剪四种模式 | - |
| **智能裁剪** | 自定义裁剪区域，内置 1:1、16:9、4:3、3:2 等预设比例 | - |
| **旋转翻转** | 任意角度旋转，垂直 / 水平翻转（真实生效） | - |
| **滤镜特效** | 15+ 专业滤镜：灰度、复古、锐化、模糊、浮雕等 | - |
| **色彩调整** | 亮度 / 对比度 / 饱和度精细调节 | - |
| **水印添加** | 文字 / 图片水印，9 宫格定位 + 平铺模式（支持旋转与间距） | - |
| **边框装饰** | 自定义边框宽度、颜色、圆角 | - |
| **元数据保留** | 处理时保留 EXIF / ICC 元数据（可开关） | - |
| **目标压缩** | 按目标大小（KB）二分逼近压缩，Web 图片优化利器 | JPEG, WebP |

### 🧠 智能能力

- **批量处理** — 数百张图片一次搞定，并发控制（1–10 路）+ 出错中断选项
- **处理方案** — 预设方案一键应用（Web 优化 / 水印保护等），支持自定义方案保存 / 导入 / 导出（导入带运行时校验）
- **智能去重** — 感知哈希算法识别相似 / 重复图片，相似度阈值可配置，返回真实相似度
- **统计仪表盘** — 处理趋势、成功率、平均耗时、节省空间等真实统计
- **EXIF 信息** — 前端 exifr 解析，完整展示相机 / 镜头 / ISO / 曝光等拍摄参数
- **处理历史** — 本地保存最近 20 条处理记录，可回看与重用配置

### 🎨 体验细节

- **多种上传** — 拖拽、粘贴（Ctrl+V）、点击上传，4 路并发加速
- **实时预览** — 缩略图 + 原始数据分离存储（IndexedDB），处理效果即时可见
- **快捷键** — `Ctrl+V` 粘贴、`Ctrl+A` 全选、`Delete` 删除、`Ctrl+Enter` 开始处理
- **批量下载** — 一键打包 ZIP，重命名模板支持 `{counter}` 防覆盖
- **双语界面** — 中文 / English 一键切换，覆盖全部界面文案与预设方案
- **主题切换** — 深色 / 浅色模式跟随系统偏好
- **响应式设计** — 桌面、平板、移动端全适配

---

## 🚀 快速开始

### 环境要求

| 环境 | 要求 |
|------|------|
| **Node.js** | >= 18.0（推荐 20+） |
| **pnpm** | >= 9.0（项目强制 `only-allow pnpm`） |

### 安装与启动

```bash
# 1. 克隆仓库
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# 2. 安装依赖
pnpm install

# 3. 启动开发服务器（默认端口 5000）
pnpm dev

# 4. 打开浏览器
#    http://localhost:5000
```

### 生产部署

```bash
pnpm build   # 构建生产版本
pnpm start   # 启动生产服务器（默认端口 5000）
```

### 代码质量检查

```bash
pnpm lint       # ESLint 检查
pnpm ts-check   # TypeScript 类型检查
```

---

## 🔌 API 参考

| 接口 | 方法 | 说明 | 限流 |
|------|------|------|------|
| `/api/upload` | POST | 上传图片（multipart/form-data，字段名 `file`） | 30 次/分钟 |
| `/api/process` | POST | 按配置处理图片（`file` + `config` JSON） | 20 次/分钟 |
| `/api/duplicates` | POST | 批量图片重复 / 相似检测（`files` 多文件） | 10 次/分钟 |

所有接口返回统一响应格式：

```json
{
  "success": true,
  "data": {},
  "timestamp": 1755330000000
}
```

错误时返回 `error.code` / `error.message`（如 `INVALID_FILE_TYPE`、`RATE_LIMIT_EXCEEDED`）。

---

## 🛠️ 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Next.js (App Router) | 16.1.1 |
| UI 库 | React | 19.2.3 |
| 语言 | TypeScript | 5.x |
| 样式 | Tailwind CSS + shadcn/ui | 4.x |
| 状态管理 | Zustand (持久化) | 5.0 |
| 图像处理 | Sharp (libvips) | 0.34 |
| 前端压缩 | JSZip | 3.10 |
| EXIF 解析 | exifr | 7.1 |
| 表单 / 校验 | react-hook-form + zod | 4.3 |
| 图表 | Recharts | 2.15 |

---

## 📁 项目结构

```
SnapForge/
├── src/
│   ├── app/
│   │   ├── api/                  # API 路由（upload / process / duplicates）
│   │   ├── layout.tsx            # 根布局（i18n 动态语言）
│   │   ├── page.tsx              # 首页（单页工作台）
│   │   └── error.tsx             # 错误边界
│   ├── components/
│   │   ├── ui/                   # shadcn/ui 基础组件
│   │   ├── ImageUploader.tsx     # 上传（拖拽 / 粘贴 / 并发）
│   │   ├── ProcessingPanel.tsx   # 批量处理面板
│   │   ├── DuplicateDetector.tsx # 智能去重
│   │   ├── ExifPanel.tsx         # EXIF 信息
│   │   ├── SchemeManager.tsx     # 方案管理（导入校验）
│   │   ├── StatsDashboard.tsx    # 统计仪表盘
│   │   └── ProcessingHistory.tsx # 处理历史
│   ├── lib/
│   │   ├── image-processor.ts    # 图像处理核心（Sharp 流水线）
│   │   ├── file-validation.ts    # 文件类型 / 大小 / 文件名统一校验
│   │   ├── config-schema.ts      # zod 配置 Schema + 深合并
│   │   ├── blob-store.ts         # IndexedDB 原始 Blob 存储
│   │   ├── request-guard.ts      # API 请求防护（Content-Length）
│   │   ├── rate-limit.ts         # 速率限制（真实 IP + 容量上限）
│   │   ├── api-response.ts       # 统一 API 响应格式
│   │   └── i18n.ts               # 国际化词表（中 / 英）
│   ├── store/                    # Zustand 状态管理（持久化）
│   └── types/                    # TypeScript 类型定义
├── public/                       # 静态资源
├── scripts/                      # dev / build / start 脚本
├── AGENTS.md                     # 项目开发规范
├── SECURITY.md                   # 安全策略
└── package.json
```

---

## ⚙️ 配置说明

| 配置项 | 说明 |
|--------|------|
| 开发 / 生产端口 | 5000（`scripts/dev.sh`、`scripts/start.sh`） |
| 单文件大小上限 | 50 MB（`src/lib/file-validation.ts` 中 `MAX_FILE_SIZE`） |
| 支持上传格式 | JPEG / PNG / WebP / GIF（拒绝 SVG / PDF 等矢量格式，缩小攻击面） |
| 大图策略 | >2MB 图片原始数据存入 IndexedDB，预览使用 800×800 缩略图 |
| 限流 | `/api/upload` 30 次/分 · `/api/process` 20 次/分 · `/api/duplicates` 10 次/分 |
| 语言 | 界面右上角切换中文 / English，偏好持久化到 localStorage |
| 历史记录 | 最多保存 20 条，`stripLargeData()` 精简后存储 |

---

## 🔒 安全设计

- **SSRF 防护** — 水印远程 URL 仅允许 http/https，DNS 解析后拦截全部私有 / 保留网段（含 IPv6），fetch 超时 + 重定向复核
- **Magic Number 验证** — 文件头字节验证真实类型，不信任客户端 MIME
- **解码防线** — 所有 sharp 入口显式 `limitInputPixels` + `failOn: 'error'`，防解压炸弹
- **请求防护** — Content-Length 强校验（缺失 / 超限直接 413）
- **限流加固** — 基于真实连接 IP（不信任可伪造的转发头），存储容量上限
- **文件名清洗** — 路径遍历、Windows 保留设备名、控制字符、Unicode 规范化全处理
- **配置校验** — zod 运行时 Schema，非法参数返回友好 400 而非 500

---

## 🤝 贡献指南

欢迎提交 Issue 与 Pull Request！参与方式：

1. **Fork** 本仓库并创建特性分支：`git checkout -b feature/your-feature`
2. **开发**：遵循 `AGENTS.md` 中的编码规范（React Hooks、i18n、命名、安全约定）
3. **验证**：提交前确保 `pnpm lint` 与 `pnpm ts-check` 全部通过
4. **提交**：遵循 Conventional Commits 风格（`feat:` / `fix:` / `refactor:` 等）
5. **发起 PR**：清晰描述改动内容与验证结果

> 💡 新手友好：`src/lib/` 下的纯函数（`file-validation.ts`、`config-schema.ts`）是很好的首个贡献切入点。

### 路线图

- [ ] 更多滤镜与 AI 增强（超分、去噪）
- [ ] 批处理任务队列持久化与断点续传
- [ ] 命令行（CLI）版本
- [ ] PWA 离线支持

---

## 📄 许可证

[MIT License](LICENSE) — Copyright © 2026 [riceshowerX](https://github.com/riceshowerX)

---

<p align="center">
  <sub>由 <a href="https://github.com/riceshowerX">riceshowerX</a> ❤️ 构建 · 本地优先 · 隐私至上</sub>
</p>
