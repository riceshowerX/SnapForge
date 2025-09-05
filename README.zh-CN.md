
<div align="center">

  <!-- Logo -->
  <a href="https://snapforge.streamlit.app/" target="_blank">
    <img src="https://github.com/riceshowerX/picx-images-hosting/raw/master/%E7%BD%91%E7%AB%99/android-chrome-192x192-1.6wqw9el8i6.webp" alt="SnapForge Logo" width="90" height="90">
  </a>

  <h1>SnapForge</h1>

  <p><strong>一个强大、优雅且开源的图像处理平台，旨在提供极致的效率。</strong></p>
  
  <p>SnapForge 提供了一个由 Streamlit 驱动的现代化网页界面，利用 <strong>多核并行处理</strong> 技术，使复杂的批量图像任务变得比以往更简单、更快速。从格式转换和 <strong>高级模板重命名</strong> 到智能重复图像检测，一切尽在掌握。</p>

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

### 📖 目录

- [✨ 线上演示](#-线上演示)
- [🛡️ 隐私声明与使用建议](#️-隐私声明与使用建议)
- [🌟 主要功能](#-主要功能)
- [📸 界面预览](#-界面预览)
- [🔧 本地安装与使用](#-本地安装与使用)
- [🧠 技术栈与架构](#-技术栈与架构)
- [🛣️ 路线图](#️-路线图)
- [🤝 贡献代码](#-贡献代码)
- [📄 许可证](#-许可证)
- [⚠️ 免责声明](#️-免责声明)

---

### ✨ 线上演示

可以直接在浏览器中尝试 SnapForge，无需安装！

<div align="center" style="margin: 30px;">
  <a href="https://snapforge.streamlit.app/" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #406aff; color: white; text-align: center; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); transition: all 0.2s ease;">
    🚀 启动线上演示 🚀
  </a>
</div>

---

### 🛡️ 隐私声明与使用建议

我们强烈建议您使用 **线上演示** 来快速评估功能和处理非敏感图像。

为了**确保数据隐私和安全**并实现**最佳处理性能**（通过充分利用本地 CPU 核心），我们建议在处理私人、重要或商业图像时，**在本地运行 SnapForge**。

本地部署可以确保所有图像文件仅保留在您的计算机上，绝不会上传到任何云服务器，从而让您对数据拥有完全的控制权。

---

### 🌟 主要功能

| 功能模块 | 描述 |
| :--- | :--- |
| **🚀 高性能批量处理** | 利用多核并行处理显著加速操作，如**格式转换**、**调整大小**、**压缩**、**水印**、**旋转**和**滤镜**等。 |
| **✍️ 高级重命名模板** | 使用动态占位符如 `{prefix}`、`{counter}`、`{original_name}`、`{width}` 和 `{height}` 完全自定义文件命名规则。 |
| **💡 智能去重** | 使用先进的 BK-Tree 算法进行高效的重复图像检测，并提供可配置的相似度阈值。 |
| **📊 全面信息查看器** | 即时查看图像的详细信息，包括**尺寸**、**文件大小**、**EXIF 元数据**、**主色调**、**色彩调色板**和 **RGB 色彩图**。 |
| **🌐 现代化界面** | 使用 Streamlit 打造美观、响应迅速的界面。支持一键**语言切换（EN/CN）**，并提供清晰的**处理日志**和进度反馈。 |

---

### 🏗️ 技术栈与架构

#### 前端（UI层）
- **Streamlit** - 现代化的网页界面框架
- **自定义CSS** - 专业的渐变UI设计
- **多语言支持** - 动态翻译系统

#### 后端（逻辑层）
- **模块化架构** - 清晰的 UI、状态管理和业务逻辑分离
- **多进程处理** - 自动利用 CPU 核心实现最大性能
- **高级算法** - BK-Tree 算法用于高效的重复图像检测

#### 核心功能
```python
# 配置系统
ProcessConfig(
    rename_config=RenameConfig(prefix="demo"),
    convert_config=ConvertConfig(format="jpeg", quality=80),
    resize_config=ResizeConfig(width=150, height=150),
    # ... 其他配置
)

# 多进程处理
processor.batch_process(files, output_dir, config, progress_callback)

# 去重检测
find_duplicate_images(file_paths, threshold=8)
````

#### 关键优化

* **资源管理** - 使用UUID命名的临时目录清理
* **错误处理** - 完备的异常处理和详细日志记录
* **性能优化** - 多核并行处理及备份机制

---

### 🔧 本地安装与使用

**1. 克隆代码库**

```bash
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge
```

**2. 创建并激活虚拟环境（推荐）**

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

**4. 运行应用**

```bash
streamlit run app.py
```

应用会自动在浏览器中打开 `http://localhost:8501`。

> **提示**：应用提供多核支持的高性能图像处理。

---

### 🛣️ 路线图

* [x] **UI/UX**: 现代化、多语言的网页界面（EN/CN）
* [x] **核心处理**: 批量转换、重命名、压缩、调整大小
* [x] **高级处理**: 批量水印、旋转、滤镜
* [x] **命名系统**: 高级自定义重命名模板
* [x] **性能**: 多进程并行处理引擎
* [x] **去重检测**: 使用先进的 BK-Tree 算法进行高效的重复图像检测
* [x] **信息查看器**: EXIF、主色调、色彩图显示
* [ ] **工作流**: 保存和加载处理预设，以便一键操作
* [ ] **便携性**: 提供一键可执行桌面版

---

### 🤝 贡献代码

我们热烈欢迎各类贡献！无论是**提交新功能**、**修复 bug**、**优化代码**、**改进文档**，还是**提出创意**，您的参与对项目至关重要。

* **报告问题**：请通过 \[**Issues**]\([https://github.com/riceshower](https://github.com/riceshower)


X/SnapForge/issues) 详细描述任何 bug 或问题

* **提交代码**：请通过 [**Pull Requests**](https://github.com/riceshowerX/SnapForge/pulls) 提交您的代码更改

> 这是一个由个人业余时间维护的开源项目，感谢您的理解、支持与贡献，它是项目持续发展的动力源泉！

---

### 📄 许可证

本项目的主体代码遵循 [**MIT 许可证**](https://github.com/riceshowerX/SnapForge/blob/main/LICENSE)。

本项目所依赖的第三方库（如 `streamlit`）将遵循各自独立的开源许可证。我们已尽最大努力遵守并尊重所有相关许可证要求。

---

### ⚠️ 免责声明

**重要：请在使用 SnapForge 之前仔细阅读本免责声明**

#### 1. 无担保

SnapForge 提供的服务是 **"按现状"** 和 **"按可用"** 提供的，不附带任何形式的明示或暗示的担保，包括但不限于适销性、特定用途的适用性或非侵权担保。

#### 2. 无责任

在任何情况下，作者、贡献者或任何相关方不对因使用本软件而产生的任何直接、间接、偶然、特殊、惩戒性或继发性损害负责（包括但不限于替代商品或服务的采购、使用、数据或利润损失，或业务中断），无论是合同、严格责任还是侵权（包括疏忽或其他原因）。

#### 3. 用户责任

* 您有责任**备份数据**，在使用 SnapForge 之前确保数据安全。
* 使用本软件所带来的所有风险由您自行承担。
* 您有责任确保您的使用符合所有适用的法律法规。
* 您有责任为处理的任何受版权保护的材料获取相应的许可证。

#### 4. 数据保护警告

* 处理敏感或重要图像时，请始终**在本地计算机上进行处理**。
* 线上演示会在远程服务器上处理图像，仅适用于非敏感内容。
* 我们无法保证通过线上演示处理的图像的安全性。

#### 5. 技术限制

* 部分图像格式可能不完全支持。
* 处理非常大的图像可能需要大量系统资源。
* 软件可能包含会影响图像质量或元数据的 bug。

**通过使用 SnapForge，您承认您已阅读并理解本免责声明，并同意接受其条款和条件。如果您不同意这些条款，请不要使用本软件。**
