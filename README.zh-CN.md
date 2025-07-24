<div align="center">

  <!-- Logo -->
  <a href="https://snapforge.streamlit.app/" target="_blank">
    <img src="https://github.com/riceshowerX/picx-images-hosting/raw/master/%E7%BD%91%E7%AB%99/android-chrome-192x192-1.6wqw9el8i6.webp" alt="SnapForge Logo" width="90" height="90">
  </a>

  <h1>SnapForge</h1>

  <p><strong>一个强大、美观且开源的图片处理平台，专为极致效率而生。</strong></p>
  
  <p>SnapForge 提供了一个基于 Streamlit 的现代化Web界面，利用<strong>多核并行处理</strong>技术，让复杂的批量图片处理任务变得前所未有的简单和快速。无论是格式转换、<strong>高级模板重命名</strong>，还是AI抠图，一切尽在掌握。</p>

  <!-- Badges -->
  <p>
    <a href="https://snapforge.streamlit.app/" target="_blank"><img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App"></a>
    <a href="https://github.com/riceshowerX/SnapForge/blob/main/LICENSE"><img src="https://img.shields.io/github/license/riceshowerX/SnapForge?style=for-the-badge&color=007EC6" alt="License"></a>
    <a href="https://github.com/riceshowerX/SnapForge/stargazers"><img src="https://img.shields.io/github/stars/riceshowerX/SnapForge?style=for-the-badge&color=FE7D37" alt="Stars"></a>
    <a href="https://github.com/riceshowerX/SnapForge/issues"><img src="https://img.shields.io/github/issues/riceshowerX/SnapForge?style=for-the-badge&color=brightgreen" alt="Issues"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python Version">
  </p>

</div>

---

### 📖 目录 (Table of Contents)

- [✨ 在线体验 (Live Demo)](#-在线体验-live-demo)
- [🛡️ 隐私声明与使用建议](#️-隐私声明与使用建议)
- [🌟 核心功能](#-核心功能)
- [📸 软件界面预览](#-软件界面预览)
- [🔧 本地安装与运行](#-本地安装与运行)
- [🧠 技术栈与鸣谢](#-技术栈与鸣谢)
- [🛣️ 开发路线图](#️-开发路线图)
- [🤝 如何贡献](#-如何贡献)
- [📄 许可证](#-许可证)
- [⚠️ 免责声明](#️-免责声明)

---

### ✨ 在线体验 (Live Demo)

无需任何安装，立即在浏览器中体验SnapForge的全部功能！

<div align="center" style="margin: 30px;">
  <a href="https://snapforge.streamlit.app/" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #406aff; color: white; text-align: center; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); transition: all 0.2s ease;">
    🚀 点击这里，立即体验 🚀
  </a>
</div>

---

### 🛡️ 隐私声明与使用建议

我们强烈建议您将 **在线体验版** 用于功能评估和处理非敏感图片。

为了 **100%保障您的数据隐私和安全**，并获得 **最佳处理性能**（充分利用您本地机器的所有CPU核心），我们推荐您在处理任何私人、重要或商业图片时，**在您自己的计算机上进行本地部署**。

本地部署意味着所有图片文件始终保留在您的电脑上，绝不会上传到任何服务器，让您完全掌控自己的数据。

---

### 🌟 核心功能

| 功能模块 | 详细说明 |
| :--- | :--- |
| **🚀 高性能批量处理** | 利用多核并行处理，大幅提升**格式转换**、**尺寸调整**、**压缩**、**水印添加**、**旋转**和**滤镜**等操作的速度。 |
| **✍️ 高级命名模板** | 使用 `{prefix}`, `{counter}`, `{original_name}`, `{width}`, `{height}` 等动态占位符，实现专业级的文件命名自定义。 |
| **💡 交互式去重** | 革命性的去重工具！**智能预选**最佳图片，让您**交互式审查**并一键**打包下载**需要保留或多余的副本，安全高效。|
| **🛠️ 智能AI工具** | 提供 **AI一键去背景** (基于`rembg`)、**OCR文字识别** (`pytesseract`)、以及**智能分类** (按尺寸/主色调) 等高级功能。 |
| **📊 全方位信息查看** | 一键查看图片的详细信息，包括**尺寸**、**大小**、**EXIF元数据**、**主色调**、**调色板**以及**RGB颜色直方图**。 |
| **🌐 现代化UI** | 基于 Streamlit 构建，界面美观、响应迅速，支持**中/英**一键切换，并提供清晰的**处理日志**和进度反馈。 |

---

### 📸 软件界面预览

![SnapForge Interface Preview](https://github.com/user-attachments/assets/56c1b4c5-8be9-4490-9d86-a09bb48776b7)

---

### 🔧 本地安装与运行

**1. 克隆项目仓库**
```bash
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge
```

**2. 创建并激活虚拟环境 (推荐)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. 安装依赖**
```bash
pip install -r requirements.txt
```

<details>
<summary><strong>👉 重要：安装 Tesseract OCR 引擎 (OCR功能必需)</strong></summary>

`pytesseract` 库需要系统级的 **Tesseract OCR 引擎** 支持，请根据您的操作系统安装：

-   **Windows**: 从 [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装。**务必在安装时勾选 "Add Tesseract to system PATH"**。
-   **macOS**: `brew install tesseract tesseract-lang`
-   **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-chi-sim`

</details>

**4. 运行应用**
```bash
streamlit run app.py
```
应用启动后，浏览器将自动打开 `http://localhost:8501`。
> **提示**: 首次使用“AI去背景”功能时，程序会自动下载所需的模型文件 (约176MB)，请耐心等待。

---

### 🧠 技术栈与鸣谢

- **核心框架**: [Streamlit](https://streamlit.io/) - 构建美观数据应用的快速方式。
- **AI去背景**: [rembg](https://github.com/danielgatis/rembg) - 强大且易用的图片背景移除库。
  - **核心模型**: [U²-Net](https://github.com/xuebinqin/U-2-Net) (仅限非商业研究用途)。模型文件将自动下载至用户目录 (`~/.u2net/u2net.onnx`)。
- **OCR**: [pytesseract](https://github.com/madmaze/pytesseract) - Google Tesseract OCR 引擎的Python封装。
- **图像处理**: [Pillow](https://python-pillow.org/) - Python图像处理库的瑞士军刀。

SnapForge 仅为学术和技术研究目的调用这些模型和库，项目本身不分发、不修改、也不存储模型文件。所有第三方库的版权归其原作者所有。

---

### 🛣️ 开发路线图

- [x] **UI/UX**: 现代化、多语言的Web界面 (中/英)
- [x] **核心处理**: 批量格式转换、重命名、压缩、尺寸调整
- [x] **高级处理**: 批量添加水印、旋转、滤镜
- [x] **命名系统**: 高级、可自定义的命名模板
- [x] **性能优化**: 基于多进程的并行处理引擎
- [x] **智能工具**: 交互式图片去重（智能预选+直接下载）
- [x] **智能工具**: AI一键去背景 (支持批量)
- [x] **智能工具**: OCR文字识别 & 智能分类
- [x] **信息查看**: EXIF、主色调、直方图展示
- [ ] **工作流**: 保存和加载处理预设，实现一键化操作。
- [ ] **可移植性**: 提供一键打包的桌面版（如使用 PyInstaller 或 Nuitka）。

---

### 🤝 如何贡献

我们热烈欢迎各种形式的贡献！无论是**提交新功能**、**修复Bug**、**优化代码**、**完善文档**，还是仅仅**提出一个好建议**，都对项目至关重要。

- **报告问题**: 请通过 [**Issues**](https://github.com/riceshowerX/SnapForge/issues) 详细描述您遇到的问题。
- **提交代码**: 请通过 [**Pull Requests**](https://github.com/riceshowerX/SnapForge/pulls) 提交您的代码变更。

> 这是一个由个人在业余时间维护的开源项目。您的理解、支持和贡献是它不断前进的动力！

---

### 📄 许可证

本项目的主体代码基于 [**MIT License**](https://github.com/riceshowerX/SnapForge/blob/main/LICENSE) 开源。

本项目依赖的第三方库（如 `streamlit`, `rembg` 等）各自拥有其独立的开源许可证。我们已尽力遵守并尊重所有相关许可证的要求。

---

### ⚠️ 免责声明

本项目按“原样”提供，不附带任何明示或暗示的保证。对于因使用本软件（或其任何部分）而导致的任何直接或间接的损害、数据丢失或业务中断，开发者和贡献者概不负责。所有风险均由用户自行承担。
