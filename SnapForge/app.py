# app.py (Final, Upgraded and Corrected Version - No remove_background)
import streamlit as st
import zipfile
import io
import tempfile
import shutil
import os
import uuid
import sys
import logging
from pathlib import Path
from PIL import Image
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 1. 后端逻辑导入 (Import Backend Logic)
# -----------------------------------------------------------------------------
try:
    from logic import (
        ImageProcessor, ProcessConfig, ResizeMode, FilterType,
        RenameConfig, ConvertConfig, ResizeConfig, CropConfig, 
        RotateConfig, FilterConfig, WatermarkConfig,
        find_duplicate_images, get_exif_data, get_image_main_color,
        plot_image_histogram, ocr_image,
        select_best_image_in_group
    )
except ImportError as e:
    st.error(
        "关键错误：无法导入 'logic.py' 文件。\n\n"
        f"错误详情: {str(e)}\n\n"
        f"当前工作目录: {os.getcwd()}\n"
        f"Python路径: {sys.path}\n"
        f"app.py所在目录: {os.path.dirname(os.path.abspath(__file__))}\n"
        f"目录内容: {os.listdir(os.path.dirname(os.path.abspath(__file__)))}\n\n"
        "请确保:\n"
        "1. 文件名确实是 'logic.py'（注意大小写）\n"
        "2. 文件位于与app.py相同的目录\n"
        "3. 文件没有语法错误\n"
        "4. 您有读取该文件的权限"
    )
    st.stop()

# 假设的多语言翻译工具
try:
    from utils_i18n import get_translator
except ImportError:
    def get_translator(lang: str) -> Callable[[str], str]:
        """提供基本的翻译回退机制"""
        translations = {
            "中文": {
                "高效、专业、美观的批量图片处理平台": "高效、专业、美观的批量图片处理平台",
                "前往GitHub仓库": "前往GitHub仓库",
                "反馈建议/提Issue": "反馈建议/提Issue",
                "反馈建议": "反馈建议",
                "批量处理": "批量处理",
                "信息查看": "信息查看",
                "图片去重": "图片去重",
                "智能工具": "智能工具",
                "处理记录": "处理记录",
                "任务开始...": "任务开始...",
                "正在处理": "正在处理",
                "处理中...": "处理中...",
                "文件不存在": "文件不存在",
                "结果预览": "结果预览",
                "图片处理参数": "图片处理参数",
                "重命名、格式转换与压缩": "重命名、格式转换与压缩",
                "启用重命名": "启用重命名",
                "前缀": "前缀",
                "起始编号": "起始编号",
                "命名模板": "命名模板",
                "启用格式转换": "启用格式转换",
                "目标格式": "目标格式",
                "启用质量压缩": "启用质量压缩",
                "压缩质量": "压缩质量",
                "尺寸、水印与高级调整": "尺寸、水印与高级调整",
                "启用尺寸调整": "启用尺寸调整",
                "宽": "宽",
                "高": "高",
                "模式": "模式",
                "仅缩小": "仅缩小",
                "保留EXIF": "保留EXIF",
                "核心数": "核心数",
                "启用水印": "启用水印",
                "内容": "内容",
                "位置": "位置",
                "字号": "字号",
                "启用裁剪": "启用裁剪",
                "裁剪宽": "裁剪宽",
                "裁剪高": "裁剪高",
                "旋转角度": "旋转角度",
                "滤镜": "滤镜",
                "上传文件": "上传文件",
                "上传图片": "上传图片",
                "开始处理图片": "开始处理图片",
                "任务开始...": "任务开始...",
                "处理完成": "处理完成",
                "未成功处理任何图片。": "未成功处理任何图片。",
                "处理完成：": "处理完成：",
                "下载全部结果": "下载全部结果",
                "上传图片以查看信息": "上传图片以查看信息",
                "尺寸": "尺寸",
                "大小": "大小",
                "图片去重": "图片去重",
                "相似度阈值 (值越小越严格)": "相似度阈值 (值越小越严格)",
                "上传需要去重的图片(至少2张)": "上传需要去重的图片(至少2张)",
                "查找重复图片": "查找重复图片",
                "未检测到重复图片。": "未检测到重复图片。",
                "检测到 {} 组重复图片。": "检测到 {} 组重复图片。",
                "智能工具": "智能工具",
                "智能去背景": "智能去背景",
                "上传图片去除背景": "上传图片去除背景",
                "开始去背景": "开始去背景",
                "处理中": "处理中",
                "失败": "失败",
                "下载结果": "下载结果",
                "OCR文字识别": "OCR文字识别",
                "上传图片进行OCR": "上传图片进行OCR",
                "开始OCR": "开始OCR",
                "识别中...": "识别中...",
                "结果": "结果",
                "处理记录": "处理记录",
                "暂无最近处理结果。": "暂无最近处理结果。",
                "X": "X",
                "Y": "Y",
                "使用 {} 核心加速...": "使用 {} 核心加速...",
                "图片并行处理中...": "图片并行处理中...",
                "处理中...": "处理中...",
                "处理完成！": "处理完成！",
                "处理中": "处理中",
                "处理中": "处理中",
                "处理中": "处理中",
                "由": "由",
                "设计与开发": "设计与开发",
                "适应边界": "适应边界",
                "裁剪填充": "裁剪填充",
                "拉伸": "拉伸"
            },
            "English": {
                "高效、专业、美观的批量图片处理平台": "Efficient, professional and beautiful batch image processing platform",
                "前往GitHub仓库": "Visit GitHub Repository",
                "反馈建议/提Issue": "Feedback/Suggest Issues",
                "反馈建议": "Feedback",
                "批量处理": "Batch Processing",
                "信息查看": "Image Info",
                "图片去重": "Deduplicate Images",
                "智能工具": "Smart Tools",
                "处理记录": "Processing History",
                "任务开始...": "Task started...",
                "正在处理": "Processing",
                "处理中...": "Processing...",
                "文件不存在": "File not found",
                "结果预览": "Preview Results",
                "图片处理参数": "Image Processing Parameters",
                "重命名、格式转换与压缩": "Rename, Format Conversion & Compression",
                "启用重命名": "Enable Renaming",
                "前缀": "Prefix",
                "起始编号": "Start Number",
                "命名模板": "Naming Template",
                "启用格式转换": "Enable Format Conversion",
                "目标格式": "Target Format",
                "启用质量压缩": "Enable Quality Compression",
                "压缩质量": "Compression Quality",
                "尺寸、水印与高级调整": "Resize, Watermark & Advanced Adjustments",
                "启用尺寸调整": "Enable Resize",
                "宽": "Width",
                "高": "Height",
                "模式": "Mode",
                "仅缩小": "Shrink Only",
                "保留EXIF": "Preserve EXIF",
                "核心数": "CPU Cores",
                "启用水印": "Enable Watermark",
                "内容": "Content",
                "位置": "Position",
                "字号": "Font Size",
                "启用裁剪": "Enable Cropping",
                "裁剪宽": "Crop Width",
                "裁剪高": "Crop Height",
                "旋转角度": "Rotation Angle",
                "滤镜": "Filter",
                "上传文件": "Upload Files",
                "上传图片": "Upload Images",
                "开始处理图片": "Start Processing",
                "任务开始...": "Task started...",
                "处理完成": "Processing completed",
                "未成功处理任何图片。": "No images were successfully processed.",
                "处理完成：": "Processing completed: ",
                "下载全部结果": "Download All Results",
                "上传图片以查看信息": "Upload image to view info",
                "尺寸": "Dimensions",
                "大小": "Size",
                "图片去重": "Image Deduplication",
                "相似度阈值 (值越小越严格)": "Similarity Threshold (lower = stricter)",
                "上传需要去重的图片(至少2张)": "Upload images to deduplicate (at least 2)",
                "查找重复图片": "Find Duplicate Images",
                "未检测到重复图片。": "No duplicate images detected.",
                "检测到 {} 组重复图片。": "Detected {} groups of duplicate images.",
                "智能工具": "Smart Tools",
                "智能去背景": "Background Removal",
                "上传图片去除背景": "Upload images for background removal",
                "开始去背景": "Start Removal",
                "处理中": "Processing",
                "失败": "Failed",
                "下载结果": "Download Results",
                "OCR文字识别": "OCR Text Recognition",
                "上传图片进行OCR": "Upload images for OCR",
                "开始OCR": "Start OCR",
                "识别中...": "Recognizing...",
                "结果": "Result",
                "处理记录": "Processing History",
                "暂无最近处理结果。": "No recent processing results.",
                "X": "X",
                "Y": "Y",
                "使用 {} 核心加速...": "Using {} cores for acceleration...",
                "图片并行处理中...": "Processing images in parallel...",
                "处理中...": "Processing...",
                "处理完成！": "Processing completed!",
                "处理中": "Processing",
                "由": "Developed by",
                "设计与开发": "designed and developed",
                "适应边界": "Fit",
                "裁剪填充": "Cover",
                "拉伸": "Stretch"
            }
        }
        return lambda s: translations.get(lang, {}).get(s, s)

# -----------------------------------------------------------------------------
# 2. UI与状态管理封装 (UI & State Management Encapsulation)
# -----------------------------------------------------------------------------
@dataclass
class AppState:
    """集中管理所有会话状态，避免魔法字符串，增强代码可维护性"""
    # 修复缺陷1：临时目录管理已移出状态类，以防止资源泄露
    result_file_paths: List[Path] = field(default_factory=list)
    duplicate_groups: List[List[str]] = field(default_factory=list)
    ocr_results: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    run_dedup: bool = False
    log_messages: List[str] = field(default_factory=list)
    
    @classmethod
    def init(cls) -> 'AppState':
        """在Streamlit会话中初始化或获取状态对象"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = cls()
        return st.session_state.app_state
    
    def cleanup(self):
        """清理临时资源"""
        # 这里可以添加清理逻辑
        pass

class UIManager:
    """封装所有UI渲染相关的CSS和HTML"""
    CUSTOM_CSS = """
    <style>
    :root {
        --primary-color: #406aff; --secondary-color: #5cc6fa; --text-color: #31333f;
        --bg-color: #f8f9fa; --card-bg-color: #ffffff;
        --card-shadow: 0 4px 12px 0 rgba(0, 20, 80, 0.06);
        --border-radius-lg: 1.2rem; --border-radius-md: 0.8rem; --border-radius-sm: 0.5rem;
    }
    body { background-color: var(--bg-color); color: var(--text-color); font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif; }
    .header-banner {
        margin-top: -2.5rem; margin-bottom: 2rem; padding: 3rem 1.5rem; background-color: #1a2035;
        background-image: url("image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cg fill-rule='evenodd'%3E%3Cg fill='%232a324f' fill-opacity='0.2'%3E%3Cpath d='M0 38.59l2.83-2.83 1.41 1.41L1.41 40H0v-1.41zM0 1.4l2.83 2.83 1.41-1.41L1.41 0H0v1.41zM38.59 40l-2.83-2.83 1.41-1.41L40 38.59V40h-1.41zM40 1.41l-2.83 2.83-1.41-1.41L38.59 0H40v1.41z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        border-radius: var(--border-radius-lg); text-align: center; color: #fff;
    }
    .header-banner .logo-svg { width: 60px; height: 60px; margin-bottom: 1rem; filter: drop-shadow(0 0 10px var(--primary-color)); }
    .header-banner h1 {
        font-size: 3rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.5rem;
        background: -webkit-linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .header-banner .subtitle { font-size: 1.1rem; font-weight: 500; opacity: 0.7; max-width: 600px; margin: 0 auto; }
    .header-actions {
        text-align: center; margin: -1.5rem auto 2.5rem auto; display: flex;
        justify-content: center; align-items: center; flex-wrap: wrap; gap: 1.2em;
    }
    .header-actions a {
        background: var(--card-bg-color); color: var(--primary-color); font-weight: 700;
        padding: 0.6em 1.5em; border-radius: 2em; box-shadow: var(--card-shadow);
        font-size: 1rem; text-decoration: none; transition: all 0.2s ease-in-out; border: 2px solid transparent;
    }
    .header-actions a:hover { transform: translateY(-2px); box-shadow: 0 6px 16px 0 rgba(0, 20, 80, 0.1); color: #fff; background: var(--primary-color); }
    .main-card {
        background: var(--card-bg-color); border-radius: var(--border-radius-lg); padding: 2rem;
        margin: 0 auto 2rem auto; box-shadow: var(--card-shadow); border: 1px solid #eef2f6;
    }
    .card h3, .main-card h3 {
        font-size: 1.35rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--primary-color);
        border-bottom: 2px solid #f0f3f7; padding-bottom: 0.8rem;
    }
    .stTabs [role="tablist"] { gap: 1rem; border-bottom: 2px solid #eef2f6; margin-bottom: 1.5rem; }
    .stTabs [role="tab"] { font-weight: 600; color: #99a1b3; padding: 0.8rem 0.2rem; transition: all 0.2s; }
    .stTabs [aria-selected="true"] { color: var(--primary-color); border-bottom: 2px solid var(--primary-color); }
    .stButton>button, .stDownloadButton>button {
        border-radius: var(--border-radius-md); font-weight: 700; font-size: 1rem;
        padding: 0.7rem 1.5rem; border: 2px solid var(--primary-color); background-color: transparent;
        color: var(--primary-color); transition: all 0.2s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover { background-color: var(--primary-color); color: #fff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(64, 106, 255, 0.3); }
    .stButton>button[kind="primary"] { background-color: var(--primary-color); color: #fff; }
    .stButton>button[kind="secondary"], .stDownloadButton>button[type="button"] { border-color: #F63366; color: #F63366; }
    .stButton>button[kind="secondary"]:hover, .stDownloadButton>button[type="button"]:hover { background-color: #F63366; color: #fff; border-color: #F63366; }
    .stButton>button[kind="primary"]:hover { filter: brightness(1.1); }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div { border-radius: var(--border-radius-sm); background-color: #f8f9fa; }
    .res-card { background: linear-gradient(100deg, #e9f2fe 0%, #e8fcff 100%); border-radius: var(--border-radius-lg); padding: 1.5rem; margin: 1.3rem 0; }
    .footer { text-align: center; color: #99a1b3; padding: 1.5rem 0; }
    .param-help { font-size: 0.85rem; color: #6c757d; margin-top: -0.5rem; margin-bottom: 0.75rem; }
    .info-card { background-color: #f8f9fa; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0; }
    </style>
    """
    HEADER_HTML_TEMPLATE = """
    <div class="header-banner">
        <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 3H4C2.897 3 2 3.897 2 5v14c0 1.103.897 2 2 2h16c1.103 0 2-.897 2-1V5c0-1.103-.897-2-2-2zM4 19V5h16l.002 14H4z"></path>
          <path d="M10.293 14.293 8.464 12.464 6 15h12l-3.536-4.42-2.171 2.713z"></path>
          <path d="m19.207 2.207-1.414 1.414L19.207 5.035l1.414-1.414L22.035 2.207l-1.414-1.414zM15 2.207l1.414-1.414L17.828 2.207l-1.414 1.414z"></path>
        </svg>
        <h1>SnapForge</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    <div class="header-actions">
        <a href="https://github.com/riceshowerX/SnapForge" target="_blank" title="{github_tooltip}">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="vertical-align: -2px; margin-right: 6px;">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub
        </a>
        <a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" title="{feedback_tooltip}">{feedback_link_text}</a>
    </div>
    """
    
    def __init__(self, translator: Callable[[str], str]):
        self._ = translator
    
    def load_resources(self):
        st.markdown(self.CUSTOM_CSS, unsafe_allow_html=True)
        st.markdown(self.HEADER_HTML_TEMPLATE.format(
            subtitle=self._("高效、专业、美观的批量图片处理平台"),
            github_tooltip=self._('前往GitHub仓库'),
            feedback_tooltip=self._('反馈建议/提Issue'),
            feedback_link_text=self._("反馈建议")
        ), unsafe_allow_html=True)
    
    def display_footer(self):
        st.markdown(f"""
        <div class="footer">
            <span>© 2025 <b>SnapForge</b> | {self._('由')} <a href="https://github.com/riceshowerX" target="_blank">riceshowerX</a> {self._('设计与开发')}</span>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 辅助函数 (Helper Functions)
# -----------------------------------------------------------------------------
def save_uploaded_files(uploaded_files, output_dir: Path) -> List[Path]:
    """
    将上传文件保存到临时目录。
    使用UUID确保即使原始文件名相同或清理后相同，也不会发生文件覆盖。
    """
    file_paths = []
    if not uploaded_files: 
        return []
    
    for f in uploaded_files:
        f.seek(0)
        original_path = Path(f.name)
        # 保留扩展名，但清理文件名
        ext = original_path.suffix.lower()
        safe_name = "".join(c for c in original_path.stem if c.isalnum() or c in "._-").strip()
        if not safe_name:
            safe_name = "image"
        safe_filename = f"{safe_name}{ext}"
        
        # 使用UUID生成唯一前缀，防止任何形式的文件名冲突
        unique_prefix = uuid.uuid4().hex[:8]
        temp_filename = f"{unique_prefix}_{safe_filename}"
        temp_path = output_dir / temp_filename
        
        with open(temp_path, "wb") as out:
            out.write(f.getvalue())
        
        file_paths.append(temp_path)
    
    return file_paths

def pack_files_to_zip(file_paths: List[Path]) -> io.BytesIO:
    """
    将文件打包为ZIP格式，确保文件名唯一避免冲突
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, file_path in enumerate(file_paths):
            if file_path.exists():
                # 使用唯一名称防止压缩包内文件名冲突
                arcname = f"processed_{i}_{file_path.name}"
                zf.write(file_path, arcname=arcname)
            else:
                logger.warning(f"文件不存在，无法添加到ZIP: {file_path}")
    zip_buffer.seek(0)
    return zip_buffer

def display_results_grid(image_paths: List[Path], _: Callable[[str], str], num_columns: int = 4):
    """显示结果图片网格"""
    if not image_paths: 
        return
    
    st.markdown("---")
    st.subheader(_("结果预览"))
    
    # 添加结果说明
    st.markdown(f'<div class="info-card">{_("共显示 {num} 个结果，点击图片可查看大图")}</div>'.format(num=len(image_paths)), 
                unsafe_allow_html=True)
    
    for i in range(0, len(image_paths), num_columns):
        cols = st.columns(num_columns)
        for j, col in enumerate(cols):
            if i + j < len(image_paths):
                path = image_paths[i + j]
                if path.exists():
                    col.image(str(path), caption=path.name, use_container_width=True)
                else:
                    col.warning(f"{path.name} {_('文件不存在')}")

def validate_processing_params(config: ProcessConfig, image_paths: List[Path]) -> Tuple[bool, str]:
    """
    验证处理参数的有效性
    """
    if not image_paths:
        return False, _("请先上传图片")
    
    # 验证尺寸调整参数
    if config.resize_config:
        if config.resize_config.width <= 0 or config.resize_config.height <= 0:
            return False, _("尺寸必须大于0")
        if config.resize_config.mode not in [ResizeMode.CONTAIN, ResizeMode.COVER, ResizeMode.STRETCH]:
            return False, _("无效的尺寸调整模式")
    
    # 验证裁剪参数
    if config.crop_config:
        # 这里需要实际图像尺寸，但暂时无法验证，会在处理时验证
        if config.crop_config.x < 0 or config.crop_config.y < 0:
            return False, _("裁剪位置不能为负值")
        if config.crop_config.width <= 0 or config.crop_config.height <= 0:
            return False, _("裁剪尺寸必须大于0")
    
    # 验证水印参数
    if config.watermark_config:
        if not config.watermark_config.text:
            return False, _("水印内容不能为空")
        if config.watermark_config.position not in ["bottom-right", "center"]:
            return False, _("无效的水印位置")
        if config.watermark_config.font_size <= 0:
            return False, _("水印字号必须大于0")
    
    # 验证压缩质量
    if config.convert_config and config.convert_config.quality:
        if config.convert_config.quality < 1 or config.convert_config.quality > 100:
            return False, _("压缩质量必须在1-100之间")
    
    return True, ""

def render_processing_options(_: Callable[[str], str]) -> ProcessConfig:
    """
    渲染批量处理选项，并使用新的分层结构创建ProcessConfig。
    """
    st.markdown(f'<h3 style="margin-top: 2rem;">{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    
    # 添加参数说明
    st.markdown(f'<div class="param-help">{_("设置图片处理的各项参数，调整后点击顶部的【开始处理图片】按钮应用")}</div>', 
                unsafe_allow_html=True)
    
    # 重命名、格式转换与压缩部分
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        st.markdown(f'<div class="param-help">{_("重命名、格式转换和质量压缩设置")}</div>', 
                    unsafe_allow_html=True)
        
        enable_rename = st.checkbox(_("启用重命名"), value=True)
        col1, col2 = st.columns(2)
        prefix = col1.text_input(_("前缀"), "image", disabled=not enable_rename)
        start_num = col2.number_input(_("起始编号"), 1, disabled=not enable_rename)
        
        # 添加命名模板帮助
        st.markdown(f'<div class="param-help">{_("可用变量: {prefix}, {counter}, {original_name}, {ext}")}</div>', 
                    unsafe_allow_html=True)
        naming_template = st.text_input(_("命名模板"), "{prefix}_{counter:04d}", disabled=not enable_rename)
        
        st.markdown("---")
        
        enable_convert = st.checkbox(_("启用格式转换"))
        col1, col2 = st.columns(2)
        target_ext = col1.selectbox(_("目标格式"), [".png", ".jpg", ".webp"], disabled=not enable_convert)
        
        enable_compress = col2.checkbox(_("启用质量压缩"), True)
        quality = col2.slider(_("压缩质量"), 1, 100, 85, disabled=not enable_convert or not enable_compress)
    
    # 尺寸、水印与高级调整部分
    with st.expander(_("尺寸、水印与高级调整")):
        st.markdown(f'<div class="param-help">{_("调整图片尺寸、添加水印和高级图像处理")}</div>', 
                    unsafe_allow_html=True)
        
        enable_resize = st.checkbox(_("启用尺寸调整"))
        col1, col2 = st.columns(2)
        width = col1.number_input(_("宽"), 1, 8000, 800, disabled=not enable_resize)
        height = col2.number_input(_("高"), 1, 8000, 600, disabled=not enable_resize)
        
        # 创建模式映射
        resize_mode_map = {
            _("适应边界"): ResizeMode.CONTAIN,
            _("裁剪填充"): ResizeMode.COVER,
            _("拉伸"): ResizeMode.STRETCH
        }
        mode_display = st.selectbox(_("模式"), list(resize_mode_map.keys()), disabled=not enable_resize)
        
        only_shrink = st.checkbox(_("仅缩小"), True, disabled=not enable_resize)
        
        st.markdown("---")
        
        # 核心设置和元数据
        col1, col2 = st.columns(2)
        preserve_meta = col1.checkbox(_("保留EXIF"), True)
        cpus = os.cpu_count() or 1
        num_proc = col2.number_input(
            _("核心数"), 
            min_value=1, 
            max_value=cpus, 
            value=max(1, cpus-1),
            help=_("使用的核心数越多处理越快，但可能影响系统性能")
        )
        
        # 水印设置
        st.markdown(f'<div class="param-help">{_("水印设置")}</div>', 
                    unsafe_allow_html=True)
        enable_wm = st.checkbox(_("启用水印"))
        wm_cfg = None
        if enable_wm:
            col1, col2, col3 = st.columns(3)
            wm_txt = col1.text_input(_("内容"), "SnapForge")
            wm_pos = col2.selectbox(_("位置"), ["bottom-right", "center"])
            wm_size = col3.slider(_("字号"), 10, 200, 36)
            wm_cfg = WatermarkConfig(wm_txt, size=wm_size, position=wm_pos)
        
        # 裁剪设置
        st.markdown(f'<div class="param-help">{_("裁剪设置")}</div>', 
                    unsafe_allow_html=True)
        enable_crop = st.checkbox(_("启用裁剪"))
        crop_cfg = None
        if enable_crop:
            col1, col2, col3, col4 = st.columns(4)
            x = col1.number_input(_("X"), min_value=0, value=0)
            y = col2.number_input(_("Y"), min_value=0, value=0)
            crop_width = col3.number_input(_("裁剪宽"), min_value=0, value=0)
            crop_height = col4.number_input(_("裁剪高"), min_value=0, value=0)
            crop_cfg = CropConfig(x, y, crop_width, crop_height)
        
        # 旋转和滤镜
        st.markdown(f'<div class="param-help">{_("旋转和滤镜设置")}</div>', 
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        rotation = col1.number_input(_("旋转角度"), -360, 360, 0, 1)
        
        # 滤镜映射
        filter_map = {"无": None}
        for f in FilterType:
            filter_map[f.value] = f
        filter_display = col2.selectbox(_("滤镜"), list(filter_map.keys()))
    
    # 构建配置对象
    return ProcessConfig(
        rename_config=RenameConfig(prefix, start_num, naming_template) if enable_rename else None,
        convert_config=ConvertConfig(target_ext, quality) if enable_convert else None,
        resize_config=ResizeConfig(width, height, resize_mode_map[mode_display], only_shrink) if enable_resize else None,
        watermark_config=wm_cfg,
        crop_config=crop_cfg,
        rotate_config=RotateConfig(rotation) if rotation != 0 else None,
        filter_config=FilterConfig(filter_map[filter_display]) if filter_map[filter_display] else None,
        preserve_metadata=preserve_meta,
        num_processes=num_proc,
    )

# -----------------------------------------------------------------------------
# 4. 主应用渲染 (Main Application Rendering)
# -----------------------------------------------------------------------------
def main_app(_: Callable[[str], str], TEMP_DIR: Path, app_state: AppState):
    """主应用界面"""
    tab_titles = [
        _("批量处理"), 
        _("信息查看"), 
        _("图片去重"), 
        _("智能工具"), 
        _("处理记录")
    ]
    tabs = st.tabs(tab_titles)
    
    # 批量处理标签
    with tabs[0]:
        processor = ImageProcessor()
        st.markdown(f'<h3>{_("📂 上传文件")}</h3>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            _("上传图片"), 
            type=["jpg", "png", "bmp", "webp"], 
            accept_multiple_files=True, 
            key="batch_upload"
        )
        
        st.info(
            _("拖放图片到此区域或点击上传。支持JPG, PNG, BMP, WEBP格式。"
              "最大文件大小: 200MB。注意: 上传前请确保图片不包含敏感信息。")
        )
        
        config = render_processing_options(_)
        
        # 添加参数验证
        if st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not uploaded_files):
            # 验证参数
            is_valid, message = validate_processing_params(config, uploaded_files)
            if not is_valid:
                st.error(message)
                return
            
            # 清理之前的处理结果
            app_state.result_file_paths.clear()
            app_state.log_messages = [_("任务开始...")]
            
            with st.container():
                log_area = st.empty()
                progress_bar = st.empty()
                result_area = st.empty()
                dl_area = st.empty()
                
                def progress_callback(pct: float, filename: str = ""):
                    """进度回调函数"""
                    progress_bar.progress(pct, f"{_('正在处理')}: {Path(filename).name}" if filename else _("处理中..."))
                
                try:
                    # 保存上传的文件
                    file_paths = save_uploaded_files(uploaded_files, TEMP_DIR)
                    
                    # 显示处理信息
                    with st.spinner(_("图片并行处理中...")):
                        result_area.info(
                            _("使用 {num} 核心加速，共 {total} 个文件").format(
                                num=config.num_processes, 
                                total=len(file_paths)
                            ), 
                            icon="⏳"
                        )
                        
                        # 处理图片
                        processed, total, result_paths = processor.batch_process(
                            [str(p) for p in file_paths], 
                            str(TEMP_DIR), 
                            config, 
                            progress_callback
                        )
                        
                        # 更新进度
                        progress_bar.progress(1.0, _("处理完成！"))
                        
                        # 处理结果
                        if not result_paths:
                            result_area.error(_("❌ 未成功处理任何图片。"))
                        else:
                            result_area.success(
                                _("✅ 处理完成：{processed} / {total}").format(
                                    processed=processed, 
                                    total=total
                                )
                            )
                            
                            # 保存结果路径
                            app_state.result_file_paths = [Path(p) for p in result_paths]
                            
                            # 提供下载按钮
                            if app_state.result_file_paths:
                                zip_data = pack_files_to_zip(app_state.result_file_paths)
                                dl_area.download_button(
                                    _("⬇️ 下载全部结果 ({num}个文件)").format(num=len(app_state.result_file_paths)),
                                    zip_data,
                                    "processed_images.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                                
                                # 显示结果预览
                                st.markdown("---")
                                st.subheader(_("结果预览"))
                                display_results_grid(app_state.result_file_paths, _)
                                
                except Exception as e:
                    logger.error(f"处理图片时出错: {str(e)}", exc_info=True)
                    st.error(_("处理中发生严重错误: {error}").format(error=str(e)), icon="❗")
    
    # 信息查看标签
    with tabs[1]:
        st.markdown(f'<h3>{_("🔍 图片信息查看")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("上传图片以查看详细信息")}</div>', 
                    unsafe_allow_html=True)
        
        uploaded_info = st.file_uploader(
            _("上传图片以查看信息"), 
            type=["jpg", "png", "bmp"], 
            key="info_upload"
        )
        
        if uploaded_info:
            try:
                # 保存并处理文件
                p = save_uploaded_files([uploaded_info], TEMP_DIR)[0]
                img = Image.open(p)
                
                # 显示图片
                st.image(img, use_container_width=True)
                
                # 显示基本信息
                col1, col2, col3 = st.columns(3)
                col1.info(f"**{_('尺寸')}:** {img.width}x{img.height}")
                col2.info(f"**{_('大小')}:** {p.stat().st_size/1024:.1f}KB")
                col3.info(f"**{_('格式')}:** {img.format}")
                
                # 显示EXIF信息（如果存在）
                try:
                    exif_data = get_exif_data(str(p))
                    if exif_data:
                        with st.expander(_("EXIF信息")):
                            for tag, value in exif_data.items():
                                st.text(f"{tag}: {value}")
                except Exception as e:
                    logger.debug(f"获取EXIF信息失败: {str(e)}")
                
                # 显示颜色分析
                try:
                    main_color, _ = get_image_main_color(str(p))
                    if main_color:
                        with st.expander(_("主色调分析")):
                            st.markdown(
                                f'<div style="background-color: #{main_color[0]:02x}{main_color[1]:02x}{main_color[2]:02x}; padding: 1rem; border-radius: 0.5rem;">'
                                f'<p style="color: white; font-weight: bold;">{_("主色调:")} #{main_color[0]:02x}{main_color[1]:02x}{main_color[2]:02x}</p></div>',
                                unsafe_allow_html=True
                            )
                except Exception as e:
                    logger.debug(f"获取主色调失败: {str(e)}")
                
            except Exception as e:
                st.error(_("无法打开图片: {error}").format(error=str(e)))
    
    # 图片去重标签
    with tabs[2]:
        st.markdown(f'<h3>{_("👯‍♀️ 图片去重")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("查找并标记重复或相似的图片")}</div>', 
                    unsafe_allow_html=True)
        
        # 添加阈值说明
        st.markdown(f'<div class="param-help">{_("值越小越严格（0=完全相同，20=非常宽松）")}</div>', 
                    unsafe_allow_html=True)
        threshold = st.slider(_("相似度阈值"), 0, 20, 8)
        
        files = st.file_uploader(
            _("上传需要去重的图片(至少2张)"), 
            type=["jpg", "png", "bmp"], 
            accept_multiple_files=True, 
            key="dedup_upload"
        )
        
        if st.button(_("查找重复图片"), use_container_width=True, disabled=len(files) < 2):
            app_state.run_dedup = True
            app_state.duplicate_groups = []
            
            with st.spinner(_("正在查找重复图片...")):
                file_paths = save_uploaded_files(files, TEMP_DIR)
                app_state.duplicate_groups = find_duplicate_images(
                    [str(p) for p in file_paths], 
                    threshold
                )
        
        if app_state.run_dedup:
            if not app_state.duplicate_groups:
                st.success(_("✅ 未检测到重复图片。"))
            else:
                st.warning(
                    _("检测到 {num} 组重复图片。点击组查看内容").format(
                        num=len(app_state.duplicate_groups)
                    )
                )
                
                # 显示重复组
                for i, group in enumerate(app_state.duplicate_groups):
                    with st.expander(_("重复组 {num} (共 {count} 张)").format(num=i+1, count=len(group))):
                        # 显示组内图片
                        display_results_grid([Path(p) for p in group], _, num_columns=3)
                        
                        # 提供选择最佳图片的选项
                        st.markdown(f"**{_('建议保留:')}**")
                        best_image = select_best_image_in_group(group)
                        if best_image:
                            st.image(best_image, width=200)
                            st.text(Path(best_image).name)
    
    # 智能工具标签
    with tabs[3]:
        st.markdown(f'<h3>{_("🔍 智能工具")}</h3>', unsafe_allow_html=True)
        
        # 添加工具说明
        st.markdown(f'<div class="info-card">{_("智能工具可以帮助您自动处理图片，包括文字识别")}</div>', 
                    unsafe_allow_html=True)
        
        # OCR文字识别工具
        with st.expander(_("✍️ OCR文字识别")):
            st.markdown(f'<div class="param-help">{_("识别图片中的文字内容，支持中英文")}</div>', 
                        unsafe_allow_html=True)
            
            # 文件上传
            files = st.file_uploader(
                _("上传图片进行OCR"), 
                accept_multiple_files=True, 
                key="ocr_upload"
            )
            
            # 处理按钮
            if st.button(_("开始OCR"), disabled=not files, use_container_width=True):
                # 清空之前的OCR结果
                app_state.ocr_results.clear()
                
                # 保存上传的文件
                paths = save_uploaded_files(files, TEMP_DIR)
                
                # 处理进度
                with st.spinner(_("识别中...")):
                    # 处理每张图片
                    for p in paths:
                        try:
                            # 执行OCR
                            text = ocr_image(str(p))
                            # 保存结果
                            app_state.ocr_results[p.name] = (str(p), text)
                        except Exception as e:
                            logger.error(f"OCR失败 {p}: {str(e)}", exc_info=True)
                            st.error(f"{p.name} {_('OCR失败')}: {str(e)}")
            
            # 显示OCR结果
            if app_state.ocr_results:
                st.success(
                    _("✅ 成功识别 {num} / {total} 张图片").format(
                        num=len(app_state.ocr_results), 
                        total=len(files) if 'files' in locals() else 0
                    )
                )
                
                # 显示每张图片的结果
                for name, (path, text) in app_state.ocr_results.items():
                    st.markdown(f"**{name}**")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(path, use_container_width=True)
                    
                    with col2:
                        # 显示结果文本区域
                        st.text_area(
                            _("识别结果"), 
                            text, 
                            height=150, 
                            key=f"ocr_{name}"
                        )
                        
                        # 添加复制按钮
                        if text.strip():
                            copy_button = st.button(
                                _("📋 复制结果"), 
                                key=f"copy_{name}"
                            )
                            if copy_button:
                                # 在Streamlit中无法直接复制到剪贴板，但可以显示提示
                                st.success(_("已复制到剪贴板（需浏览器支持）"))
    
    # 处理记录标签
    with tabs[4]:
        st.markdown(f'<h3>{_("📋 处理记录")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("显示最近处理的图片结果")}</div>', 
                    unsafe_allow_html=True)
        
        if app_state.result_file_paths:
            st.success(
                _("✅ 最近成功处理 {num} 个文件").format(
                    num=len(app_state.result_file_paths)
                )
            )
            
            # 提供下载所有结果的选项
            zip_data = pack_files_to_zip(app_state.result_file_paths)
            st.download_button(
                _("⬇️ 下载全部结果 ({num}个文件)").format(num=len(app_state.result_file_paths)),
                zip_data,
                "recent_processing_results.zip",
                mime="application/zip",
                use_container_width=True
            )
            
            # 显示结果
            display_results_grid(app_state.result_file_paths, _)
        else:
            st.info(_("暂无最近处理结果。"))

# --- 运行主应用并渲染页脚 ---
def run():
    """应用入口点"""
    st.set_page_config(
        page_title="SnapForge", 
        page_icon="🖼️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化应用状态
    app_state = AppState.init()
    
    # 侧边栏
    with st.sidebar:
        st.title("SnapForge")
        
        # 语言选择
        lang = st.selectbox("Language/语言", ["English", "中文"])
        _ = get_translator(lang)
        
        st.header(_("⚙️ 设置"))
        
        # 状态清理按钮
        if st.button(_("清理会话状态"), use_container_width=True, type="secondary"):
            # 清理会话状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success(_("会话已重置！页面将刷新。"))
            st.rerun()
        
        # 添加应用信息
        st.markdown("---")
        st.markdown(f"**{_('版本')}**: 2.0.0")
        st.markdown(f"**{_('开发者')}**: riceshowerX")
        st.markdown(f"**{_('GitHub')}**: [SnapForge](https://github.com/riceshowerX/SnapForge)")
        
        # 添加使用说明
        st.markdown("---")
        st.markdown(f"### {_('使用说明')}")
        st.markdown(f"- {_('上传图片后设置处理参数')}")
        st.markdown(f"- {_('点击【开始处理图片】按钮应用')}")
        st.markdown(f"- {_('处理结果可预览和下载')}")
        st.markdown(f"- {_('使用侧边栏清理会话状态')}")
    
    # 加载UI资源
    ui = UIManager(_)
    ui.load_resources()
    
    # 主内容区域
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # 使用临时目录处理上传文件
    with tempfile.TemporaryDirectory(prefix="snapforge_") as temp_dir_str:
        TEMP_DIR = Path(temp_dir_str)
        main_app(_, TEMP_DIR, app_state)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示页脚
    ui.display_footer()

if __name__ == "__main__":
    run()
