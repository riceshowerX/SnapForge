
<div align="center">

  <!-- Logo已替换为您指定的链接 -->
  <img src="https://github.com/riceshowerX/picx-images-hosting/raw/master/%E7%BD%91%E7%AB%99/android-chrome-192x192-1.6wqw9el8i6.webp" alt="SnapForge Logo" width="90" height="90">

  <h1>SnapForge</h1>

  <p>
    <strong>一个强大、美观且开源的图片处理平台，专为效率而生。</strong>
  </p>
  <p>
    SnapForge 提供了一个基于 Streamlit 的现代化Web界面，让复杂的批量图片处理任务变得前所未有的简单。无论是格式转换、智能重命名，还是AI抠图，一切尽在掌握。
  </p>

  <!-- 徽章 -->
  <p>
    <a href="https://github.com/riceshowerX/SnapForge/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/riceshowerX/SnapForge?style=for-the-badge&color=007EC6" alt="License">
    </a>
    <a href="https://github.com/riceshowerX/SnapForge/releases/latest">
      <img src="https://img.shields.io/github/v/release/riceshowerX/SnapForge?style=for-the-badge&color=7856D5" alt="Release">
    </a>
    <img src="https://img.shields.io/github/stars/riceshowerX/SnapForge?style=for-the-badge&color=FE7D37" alt="Stars">
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python Version">
  </p>
</div>

---

## 📸 软件界面预览

![SnapForge界面预览](https://github.com/user-attachments/assets/a475207e-2650-4212-b7aa-3e3d32d6974b)

---

## ✨ 核心功能

| 功能模块 | 详细说明 |
| :--- | :--- |
| **🖼️ 批量处理** | 支持对图片进行**格式转换** (JPEG, PNG, WEBP等)、**尺寸调整**、**压缩**、**重命名**、**水印添加**、**旋转**和**滤镜**等多种操作。 |
| **💡 智能工具** | 提供 **AI一键去背景** (基于`rembg`和U²-Net)、**OCR文字识别**、**相似图片查找**以及**智能分类** (按尺寸/主色调) 等高级功能。 |
| **📊 信息查看** | 一键查看图片的详细信息，包括**尺寸**、**文件大小**、**EXIF元数据**、**主色调**、**调色板**以及**RGB颜色直方图**。 |
| **🌐 现代化UI** | 基于 Streamlit 构建，界面美观、响应迅速，支持**中/英文**一键切换，并提供清晰的**处理日志**和进度反馈。 |
| **⚙️ 灵活配置** | 提供丰富的参数选项，如多种缩放模式（Fit, Fill, Pad, Crop）、自定义重命名规则、压缩质量调节等，满足专业需求。 |
| **跨平台** | 完全兼容 **Windows / macOS / Linux** 主流操作系统。 |

---

## 🚀 快速上手

在本地运行 SnapForge 非常简单，只需三个步骤：

**1. 克隆项目仓库**
```bash
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge
```

**2. 安装依赖项**
我们推荐在一个虚拟环境中安装，以保持环境纯净。
```bash
# 安装所有Python库
pip install -r requirements.txt
```
> **重要提示 (OCR功能)**: `pytesseract` 库需要系统级的 **Tesseract OCR 引擎** 支持。请根据您的操作系统进行安装，否则OCR功能将无法使用。
> - **Windows**: 从 [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装，**务必在安装时勾选 "Add Tesseract to system PATH"**。
> - **macOS**: `brew install tesseract tesseract-lang`
> - **Linux (Ubuntu/Debian)**: `sudo apt install tesseract-ocr tesseract-ocr-chi-sim`

**3. 运行应用**
```bash
streamlit run app.py
```
应用启动后，浏览器会自动打开 `http://localhost:8501`。首次使用“去背景”功能时，程序会自动下载所需的模型文件 (约176MB)，请耐心等待。

---

## 🧠 关于U²-Net模型 (去背景功能)

SnapForge的去背景功能由强大的 [rembg](https://github.com/danielgatis/rembg) 库驱动，其核心模型为 [U²-Net](https://github.com/xuebinqin/U-2-Net)。

- **模型下载路径**:
  - Windows: `C:\Users\你的用户名\.u2net\u2net.onnx`
  - Linux/Mac: `~/.u2net/u2net.onnx`
- **模型版权**: U²-Net模型归原作者所有，其许可证限制其仅用于非商业用途。SnapForge仅为学术和技术研究目的调用此模型，项目本身不分发、不修改、也不存储模型文件。

---

## 🛣️ 开发路线图

- [x] **UI/UX**: 现代化、多语言的Web界面 (中/英)
- [x] **核心处理**: 批量格式转换、重命名、压缩、尺寸调整
- [x] **高级处理**: 批量添加水印、旋转、滤镜
- [x] **智能工具**: AI一键去背景 (支持批量)
- [x] **智能工具**: 相似图片查找
- [x] **智能工具**: OCR文字识别 & 智能分类
- [x] **信息查看**: EXIF、主色调、直方图展示
- [ ] **输出配置**: 自定义输出目录结构与命名模板
- [ ] **性能优化**: 优化大批量文件的处理速度与内存占用
- [ ] **可移植性**: 提供一键打包的桌面版（如使用PyInstaller或Nuitka）

---

## 🤝 如何贡献

我们热烈欢迎各种形式的贡献！无论是**提交新功能**、**修复Bug**、**优化代码**、**完善文档**，还是仅仅**提出一个好建议**，都对项目至关重要。

- **报告问题**: 请通过 [Issues](https://github.com/riceshowerX/SnapForge/issues) 详细描述您遇到的问题。
- **提交代码**: 请通过 [Pull Requests](https://github.com/riceshowerX/SnapForge/pulls) 提交您的代码变更。

> 这是一个由个人在业余时间维护的开源项目。您的理解、支持和贡献是它不断前进的动力！

---

## 📄 许可证

本项目的主体代码基于 [MIT License](https://github.com/riceshowerX/SnapForge/blob/main/LICENSE) 开源。

同时，本项目依赖的第三方库（如 `streamlit`, `rembg` 等）各自拥有其独立的开源许可证。我们已尽力遵守并尊重所有相关许可证的要求。

---

## ⚠️ 免责声明

本项目按“原样”提供，不附带任何明示或暗示的保证。对于因使用本软件（或其任何部分）而导致的任何直接或间接的损害、数据丢失或业务中断，开发者和贡献者概不负责。所有风险均由用户自行承担。
