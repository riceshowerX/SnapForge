<div align="center">

  <!-- Logo -->
  <a href="https://snapforge.streamlit.app/" target="_blank">
    <img src="https://github.com/riceshowerX/picx-images-hosting/raw/master/%E7%BD%91%E7%AB%99/android-chrome-192x192-1.6wqw9el8i6.webp" alt="SnapForge Logo" width="90" height="90">
  </a>

  <h1>SnapForge</h1>

  <p><strong>A powerful, elegant, and open-source image processing platform, built for ultimate efficiency.</strong></p>
  
  <p>SnapForge provides a modern web interface powered by Streamlit, leveraging <strong>multi-core parallel processing</strong> to make complex batch image tasks simpler and faster than ever. From format conversion and <strong>advanced template-based renaming</strong> to intelligent duplicate detection, everything is at your fingertips.</p>

  <!-- Badges -->
  <p>
    <a href="https://snapforge.streamlit.app/" target="_blank"><img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App"></a>
    <a href="https://github.com/riceshowerX/SnapForge/blob/main/LICENSE"><img src="https://img.shields.io/github/license/riceshowerX/SnapForge?style=for-the-badge&color=007EC6" alt="License"></a>
    <a href="https://github.com/riceshowerX/SnapForge/stargazers"><img src="https://img.shields.io/github/stars/riceshowerX/SnapForge?style=for-the-badge&color=FE7D37" alt="Stars"></a>
    <a href="https://github.com/riceshowerX/SnapForge/issues"><img src="https://img.shields.io/github/issues/riceshowerX/SnapForge?style=for-the-badge&color=brightgreen" alt="Issues"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python Version">
  </p>
  
  <p>
    <strong>English</strong> | <a href="README.zh-CN.md">简体中文</a>
  </p>

</div>

---

### 📖 Table of Contents

- [✨ Live Demo](#-live-demo)
- [🛡️ Privacy Notice & Usage Recommendation](#️-privacy-notice--usage-recommendation)
- [🌟 Key Features](#-key-features)
- [📸 Interface Preview](#-interface-preview)
- [🔧 Local Installation & Usage](#-local-installation--usage)
- [🧠 Tech Stack & Architecture](#-tech-stack--architecture)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [⚠️ Disclaimer](#️-disclaimer)

---

### ✨ Live Demo

Try SnapForge directly in your browser without any installation!

<div align="center" style="margin: 30px;">
  <a href="https://snapforge.streamlit.app/" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #406aff; color: white; text-align: center; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); transition: all 0.2s ease;">
    🚀 Launch Live Demo 🚀
  </a>
</div>

---

### 🛡️ Privacy Notice & Usage Recommendation

We strongly recommend using the **Live Demo** for quick feature evaluation and processing non-sensitive images.

To **guarantee 100% data privacy and security** and to achieve **optimal processing performance** (by fully utilizing your local CPU cores), we advise you to **run SnapForge locally on your own machine** when handling private, critical, or commercial images.

Local deployment ensures that all image files remain on your computer and are never uploaded to any cloud server, giving you complete control over your data.

---

### 🌟 Key Features

| Feature Module | Description |
| :--- | :--- |
| **🚀 High-Performance Batch Processing** | Utilizes multi-core parallel processing to significantly speed up operations like **format conversion**, **resizing**, **compression**, **watermarking**, **rotation**, and **filters**. |
| **✍️ Advanced Renaming Templates** | Use dynamic placeholders like `{prefix}`, `{counter}`, `{original_name}`, `{width}`, and `{height}` to fully customize file naming conventions like a pro. |
| **💡 Intelligent Deduplication** | Advanced BK-Tree algorithm for efficient duplicate detection with configurable similarity thresholds. |
| **💡 Intelligent Deduplication** | Advanced BK-Tree algorithm for efficient duplicate detection with configurable similarity thresholds. |
| **📊 Comprehensive Info Viewer** | Instantly view detailed image information, including **dimensions**, **file size**, **EXIF metadata**, **dominant color**, **color palette**, and an **RGB color histogram**. |
| **🌐 Modern UI** | Built with Streamlit for a beautiful, responsive interface. Supports one-click **language switching (EN/CN)** and provides clear **processing logs** and progress feedback. |

---

### 🏗️ Tech Stack & Architecture

#### Frontend (UI Layer)
- **Streamlit** - Modern web interface framework
- **Custom CSS** - Professional gradient UI design
- **Multi-language Support** - Dynamic translation system

#### Backend (Logic Layer)
- **Modular Architecture** - Clean separation of UI, state management, and business logic
- **Multi-process Processing** - Automatic CPU core utilization for maximum performance
- **Advanced Algorithms** - BK-Tree for efficient duplicate detection

#### Core Features
```python
# Configuration System
ProcessConfig(
    rename_config=RenameConfig(prefix="demo"),
    convert_config=ConvertConfig(format="jpeg", quality=80),
    resize_config=ResizeConfig(width=150, height=150),
    # ... other configurations
)

# Multi-process Processing
processor.batch_process(files, output_dir, config, progress_callback)

# Duplicate Detection
find_duplicate_images(file_paths, threshold=8)
```

#### Key Optimizations
- **Resource Management** - Automatic temp directory cleanup with UUID-based file naming
- **Error Handling** - Comprehensive exception handling with detailed logging
- **Performance** - Multi-core parallel processing with fallback mechanisms

---

### 🔧 Local Installation & Usage

**1. Clone the Repository**
```bash
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge
```

**2. Create and Activate a Virtual Environment (Recommended)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

<details>
<summary><strong>👉 IMPORTANT: Install Tesseract OCR Engine (Required for OCR)</strong></summary>

The `pytesseract` library requires a system-level installation of the **Tesseract OCR engine**. Please install it according to your OS:

-   **Windows**: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). **Ensure you check "Add Tesseract to system PATH" during installation**.
-   **macOS**: `brew install tesseract tesseract-lang`
-   **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install tesseract-ocr`

</details>

**4. Run the Application**
```bash
streamlit run app.py
```
The application will automatically open at `http://localhost:8501` in your browser.

> **Note**: The first time you use the "AI Background Removal" feature, the required model file (approx. 176MB) will be downloaded automatically. Please be patient.

---

### 🛣️ Roadmap

- [x] **UI/UX**: Modern, multi-language web interface (EN/CN)
- [x] **Core Processing**: Batch conversion, renaming, compression, resizing
- [x] **Advanced Processing**: Batch watermarking, rotation, filters
- [x] **Naming System**: Advanced, customizable renaming templates
- [x] **Performance**: Multi-process parallel processing engine
- [x] **Deduplication**: Advanced BK-Tree algorithm for efficient duplicate detection
- [x] **Info Viewer**: EXIF, dominant color, histogram display
- [x] **Deduplication**: Advanced BK-Tree algorithm for efficient duplicate detection
- [ ] **Workflows**: Save and load processing presets for one-click operations
- [ ] **Portability**: Provide a one-click executable desktop version

---

### 🤝 Contributing

We warmly welcome contributions of all forms! Whether it's **submitting new features**, **fixing bugs**, **optimizing code**, **improving documentation**, or just **suggesting a great idea**, your input is vital to the project.

- **Report Issues**: Please describe any bugs or issues in detail via [**Issues**](https://github.com/riceshowerX/SnapForge/issues)
- **Submit Code**: Please submit your code changes via [**Pull Requests**](https://github.com/riceshowerX/SnapForge/pulls)

> This is an open-source project maintained by an individual in their spare time. Your understanding, support, and contributions are the driving force behind its continued development!

---

### 📄 License

The main body of this project is open-sourced under the [**MIT License**](https://github.com/riceshowerX/SnapForge/blob/main/LICENSE).

Third-party libraries relied upon by this project (such as `streamlit`, `rembg`, etc.) are subject to their own separate open-source licenses. We have made every effort to comply with and respect all relevant license requirements.

---

### ⚠️ Disclaimer

This project is provided "as is," without any express or implied warranty. In no event shall the developers or contributors be liable for any direct or indirect damages, data loss, or business interruption arising from the use of this software (or any part thereof). All risks are assumed by the user.