# app.py (Final, Upgraded and Corrected Version - No remove_background and No OCR)
import streamlit as st
import zipfile
import io
import tempfile
import shutil
import os
import uuid
import sys
import logging
import datetime
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
        plot_image_histogram,  # 移除了ocr_image
        select_best_image_in_group,
        ResourceManager,
        InvalidConfigError,
        FileProcessingError
    )
except ImportError as e:
    st.error(
        "关键错误：无法导入 'logic.py' 文件。\n"
        f"错误详情: {str(e)}\n"
        f"当前工作目录: {os.getcwd()}\n"
        f"Python路径: {sys.path}\n"
        f"app.py所在目录: {os.path.dirname(os.path.abspath(__file__))}\n"
        f"目录内容: {os.listdir(os.path.dirname(os.path.abspath(__file__)))}\n"
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
                "处理记录": "处理记录",  # 移除了"智能工具"
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
                "格式": "格式",
                "图片去重": "图片去重",
                "相似度阈值 (值越小越严格)": "相似度阈值 (值越小越严格)",
                "上传需要去重的图片(至少2张)": "上传需要去重的图片(至少2张)",
                "查找重复图片": "查找重复图片",
                "未检测到重复图片。": "未检测到重复图片。",
                "检测到 {} 组重复图片。": "检测到 {} 组重复图片。",
                "处理记录": "处理记录",
                "暂无最近处理结果。": "暂无最近处理结果。",
                "X": "X",
                "Y": "Y",
                "使用 {} 核心加速...": "使用 {} 核心加速...",
                "图片并行处理中...": "图片并行处理中...",
                "处理中...": "处理中...",
                "处理完成！": "处理完成！",
                "处理中": "处理中",
                "由": "由",
                "设计与开发": "设计与开发",
                "适应边界": "适应边界",
                "裁剪填充": "裁剪填充",
                "拉伸": "拉伸",
                "低": "低",
                "中": "中",
                "高": "高",
                "共显示 {num} 个结果，点击图片可查看大图，享受二次元般的视觉体验~": "共显示 {num} 个结果，点击图片可查看大图，享受二次元般的视觉体验~",
                "重命名、格式转换和质量压缩设置，让您的图片更加精致~": "重命名、格式转换和质量压缩设置，让您的图片更加精致~",
                "调整图片尺寸、添加水印和高级图像处理，打造专属二次元风格~": "调整图片尺寸、添加水印和高级图像处理，打造专属二次元风格~",
                "水印设置，为您的图片添加个性化标识~": "水印设置，为您的图片添加个性化标识~",
                "裁剪设置，精准裁剪您需要的部分~": "裁剪设置，精准裁剪您需要的部分~",
                "旋转和滤镜设置，为图片添加独特效果~": "旋转和滤镜设置，为图片添加独特效果~",
                "拖放图片到此区域或点击上传。支持JPG, PNG, BMP, WEBP格式。最大文件大小: 200MB。注意: 上传前请确保图片不包含敏感信息。": "拖放图片到此区域或点击上传。支持JPG, PNG, BMP, WEBP格式。最大文件大小: 200MB。注意: 上传前请确保图片不包含敏感信息。",
                "二次元风格UI设计 | 像樱花般轻盈的图片处理体验": "二次元风格UI设计 | 像樱花般轻盈的图片处理体验"
            },
            "English": {
                "高效、专业、美观的批量图片处理平台": "Efficient, professional and beautiful batch image processing platform",
                "前往GitHub仓库": "Visit GitHub Repository",
                "反馈建议/提Issue": "Feedback/Suggest Issues",
                "反馈建议": "Feedback",
                "批量处理": "Batch Processing",
                "信息查看": "Image Info",
                "图片去重": "Deduplicate Images",
                "处理记录": "Processing History",  # 移除了"Smart Tools"
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
                "格式": "Format",
                "图片去重": "Image Deduplication",
                "相似度阈值 (值越小越严格)": "Similarity Threshold (lower = stricter)",
                "上传需要去重的图片(至少2张)": "Upload images to deduplicate (at least 2)",
                "查找重复图片": "Find Duplicate Images",
                "未检测到重复图片。": "No duplicate images detected.",
                "检测到 {} 组重复图片。": "Detected {} groups of duplicate images.",
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
                "拉伸": "Stretch",
                "低": "Low",
                "中": "Medium",
                "高": "High",
                "共显示 {num} 个结果，点击图片可查看大图，享受二次元般的视觉体验~": "Showing {num} results, click to view full image and enjoy the anime-style experience~",
                "重命名、格式转换和质量压缩设置，让您的图片更加精致~": "Rename, format conversion and quality compression settings to make your images more refined~",
                "调整图片尺寸、添加水印和高级图像处理，打造专属二次元风格~": "Adjust image size, add watermark and advanced image processing to create your own anime style~",
                "水印设置，为您的图片添加个性化标识~": "Watermark settings to add personalized identification to your images~",
                "裁剪设置，精准裁剪您需要的部分~": "Crop settings for precise cropping of the parts you need~",
                "旋转和滤镜设置，为图片添加独特效果~": "Rotation and filter settings to add unique effects to your images~",
                "拖放图片到此区域或点击上传。支持JPG, PNG, BMP, WEBP格式。最大文件大小: 200MB。注意: 上传前请确保图片不包含敏感信息。": "Drag and drop images here or click to upload. Supports JPG, PNG, BMP, WEBP formats. Max file size: 200MB. Note: Ensure images do not contain sensitive information before uploading.",
                "二次元风格UI设计 | 像樱花般轻盈的图片处理体验": "Anime-style UI design | Light as cherry blossoms image processing experience"
            }
        }
        return lambda s: translations.get(lang, {}).get(s, s)

# -----------------------------------------------------------------------------
# 2. 二次元风格UI管理器
# -----------------------------------------------------------------------------
class UIManager:
    """二次元风格UI管理器"""
    CUSTOM_CSS = """
    <style>
    :root {
        --primary-color: #ff6b6b;
        --secondary-color: #4ecdc4;
        --accent-color: #ff9ff3;
        --background-color: #f8f9fa;
        --card-bg: #ffffff;
        --text-color: #2d3748;
        --border-radius-lg: 1.5rem;
        --border-radius-md: 1rem;
        --border-radius-sm: 0.5rem;
        --shadow-sm: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* 二次元风格背景 */
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        background-attachment: fixed;
        color: var(--text-color);
        font-family: 'Noto Sans JP', 'Noto Sans SC', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255, 159, 243, 0.05) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(78, 205, 196, 0.05) 0%, transparent 20%);
    }
    
    /* 二次元风格标题和卡片 */
    .header-banner {
        margin-top: -2.5rem;
        margin-bottom: 2rem;
        padding: 3rem 1.5rem;
        background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
        border-radius: var(--border-radius-lg);
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .header-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        z-index: 0;
    }
    
    .header-banner h1 {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
        background: linear-gradient(to right, #ffffff, #f0f4ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: textShine 3s linear infinite;
    }
    
    @keyframes textShine {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .header-banner .subtitle {
        font-size: 1.2rem;
        font-weight: 500;
        opacity: 0.9;
        max-width: 650px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    
    .header-actions {
        text-align: center;
        margin: -1.5rem auto 2.5rem auto;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 1.2em;
        position: relative;
        z-index: 1;
    }
    
    .header-actions a {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        color: white;
        font-weight: 700;
        padding: 0.7em 1.8em;
        border-radius: 2em;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        font-size: 1.05rem;
        text-decoration: none;
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-actions a::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: 0.5s;
    }
    
    .header-actions a:hover::before {
        left: 100%;
    }
    
    .header-actions a:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 7px 20px rgba(0, 0, 0, 0.25);
        background: rgba(255, 255, 255, 0.25);
    }
    
    /* 二次元风格卡片 */
    .main-card {
        background: var(--card-bg);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin: 0 auto 2rem auto;
        box-shadow: var(--shadow-lg);
        border: 1px solid rgba(0, 0, 0, 0.08);
        background: linear-gradient(to bottom right, #ffffff 0%, #f9fafb 100%);
        position: relative;
        overflow: hidden;
    }
    
    .main-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }
    
    .card h3, .main-card h3 {
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: var(--primary-color);
        position: relative;
        padding-left: 1rem;
    }
    
    .card h3::before, .main-card h3::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 1.2em;
        background: var(--accent-color);
        border-radius: 2px;
    }
    
    /* 二次元风格标签页 */
    .stTabs [role="tablist"] {
        gap: 1.2rem;
        border-bottom: 2px solid rgba(0, 0, 0, 0.08);
        margin-bottom: 1.8rem;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(5px);
        border-radius: var(--border-radius-md) var(--border-radius-md) 0 0;
        padding: 0.5rem;
    }
    
    .stTabs [role="tab"] {
        font-weight: 600;
        color: #6c757d;
        padding: 0.9rem 1.3rem;
        transition: all 0.3s;
        border-radius: var(--border-radius-sm);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [role="tab"]::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        transition: width 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary-color);
        background: rgba(255, 107, 107, 0.1);
    }
    
    .stTabs [aria-selected="true"]::after {
        width: 100%;
    }
    
    /* 二次元风格按钮 */
    .stButton>button, .stDownloadButton>button {
        border-radius: var(--border-radius-md);
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.75rem 1.6rem;
        border: none;
        background: linear-gradient(135deg, var(--primary-color), #ff5252);
        color: white;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .stButton>button::before, .stDownloadButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: 0.6s;
        z-index: 0;
    }
    
    .stButton>button:hover::before, .stDownloadButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
        background: linear-gradient(135deg, #ff5252, #ff3333);
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--secondary-color), #38c9c1);
        box-shadow: 0 4px 10px rgba(78, 205, 196, 0.3);
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #38c9c1, #2eb8b2);
        box-shadow: 0 6px 15px rgba(78, 205, 196, 0.4);
    }
    
    .stButton>button[kind="secondary"], .stDownloadButton>button[type="button"] {
        background: linear-gradient(135deg, var(--accent-color), #e076f0);
        box-shadow: 0 4px 10px rgba(255, 159, 243, 0.3);
    }
    
    .stButton>button[kind="secondary"]:hover, .stDownloadButton>button[type="button"]:hover {
        background: linear-gradient(135deg, #e076f0, #d35de8);
        box-shadow: 0 6px 15px rgba(255, 159, 243, 0.4);
    }
    
    /* 二次元风格输入框 */
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div {
        border-radius: var(--border-radius-sm);
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.6rem 1rem;
        transition: all 0.2s;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput>div>input:focus, .stNumberInput>div>input:focus, .stSelectbox>div>div>div:focus-within {
        border-color: var(--secondary-color);
        box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
        outline: none;
    }
    
    /* 二次元风格结果卡片 */
    .res-card {
        background: linear-gradient(100deg, #fef2f2 0%, #fff9f9 100%);
        border-radius: var(--border-radius-lg);
        padding: 1.6rem;
        margin: 1.5rem 0;
        border-left: 4px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s;
    }
    
    .res-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    
    .info-card {
        background: linear-gradient(to right, #e6f7ff, #f0f9ff);
        border-radius: var(--border-radius-lg);
        padding: 1.2rem;
        margin: 1.2rem 0;
        border-left: 4px solid var(--secondary-color);
    }
    
    .param-help {
        font-size: 0.9rem;
        color: #718096;
        margin-top: -0.4rem;
        margin-bottom: 0.8rem;
        line-height: 1.5;
        background: #f8fafc;
        padding: 0.6rem 1rem;
        border-radius: var(--border-radius-sm);
        border-left: 3px solid var(--accent-color);
    }
    
    /* 二次元风格页脚 */
    .footer {
        text-align: center;
        color: #718096;
        padding: 1.8rem 0;
        margin-top: 2rem;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .footer a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .footer a:hover {
        color: var(--accent-color);
        text-decoration: underline;
    }
    
    /* 添加二次元装饰元素 */
    .decoration {
        position: fixed;
        z-index: -1;
        opacity: 0.05;
    }
    
    .decoration.top-left {
        top: 10%;
        left: 5%;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, var(--primary-color), transparent 70%);
    }
    
    .decoration.bottom-right {
        bottom: 10%;
        right: 5%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, var(--accent-color), transparent 70%);
    }
    
    /* 添加二次元风格角色插画 */
    .character-illustration {
        position: fixed;
        bottom: 0;
        right: 0;
        width: 250px;
        height: 300px;
        opacity: 0.9;
        pointer-events: none;
        z-index: -1;
        background: url('image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 250"><path fill="%23ff6b6b" d="M100,20 C140,20 170,50 170,90 C170,130 140,160 100,160 C60,160 30,130 30,90 C30,50 60,20 100,20 Z"/><circle fill="%23ffffff" cx="80" cy="80" r="15"/><circle fill="%23ffffff" cx="120" cy="80" r="15"/><circle fill="%23000000" cx="80" cy="80" r="7"/><circle fill="%23000000" cx="120" cy="80" r="7"/><path fill="%23000000" d="M90,110 Q100,120 110,110"/><path fill="%23ff9ff3" d="M100,160 L100,200 L70,250 L130,250 Z"/></svg>') no-repeat center bottom;
        background-size: contain;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* 添加二次元风格加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 二次元风格进度条 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: var(--border-radius-sm);
        box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3);
    }
    
    /* 二次元风格警告和成功消息 */
    .stAlert > div {
        border-radius: var(--border-radius-md);
        border: none;
        box-shadow: var(--shadow-sm);
    }
    
    .stAlert[role="alert"][data-baseweb="toast"] {
        border-left: 4px solid var(--primary-color);
    }
    
    .stAlert[role="alert"][data-baseweb="toast"].success {
        border-left-color: var(--secondary-color);
    }
    
    .stAlert[role="alert"][data-baseweb="toast"].info {
        border-left-color: var(--accent-color);
    }
    
    /* 二次元风格图片预览 */
    .preview-image {
        border-radius: var(--border-radius-md);
        overflow: hidden;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .preview-image:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
        border-color: var(--secondary-color);
    }
    
    /* 二次元风格选项卡 */
    .tab-content {
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 添加樱花飘落效果 */
    .sakura {
        position: fixed;
        top: -50px;
        z-index: -1;
        pointer-events: none;
        animation: fall linear forwards;
        opacity: 0.7;
    }
    
    @keyframes fall {
        to { transform: translateY(100vh) translateX(20px); }
    }
    </style>
    
    <!-- 樱花飘落效果脚本 -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        function createSakura() {
            const sakura = document.createElement('div');
            sakura.className = 'sakura';
            sakura.innerHTML = '✿';
            sakura.style.fontSize = Math.random() * 20 + 10 + 'px';
            sakura.style.left = Math.random() * 100 + 'vw';
            sakura.style.animationDuration = Math.random() * 10 + 15 + 's';
            document.body.appendChild(sakura);
            
            setTimeout(() => {
                sakura.remove();
            }, 25000);
        }
        
        // 每2秒创建一个樱花
        setInterval(createSakura, 2000);
        
        // 初始化创建几个樱花
        for (let i = 0; i < 5; i++) {
            setTimeout(createSakura, i * 500);
        }
    });
    </script>
    """

    HEADER_HTML_TEMPLATE = """
    <div class="header-banner">
        <div class="decoration top-left"></div>
        <div class="decoration bottom-right"></div>
        <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" 
             style="width: 70px; height: 70px; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.5));">
          <path d="M20 3H4C2.897 3 2 3.897 2 5v14c0 1.103.897 2 2 2h16c1.103 0 2-.897 2-1V5c0-1.103-.897-2-2-2zM4 19V5h16l.002 14H4z"></path>
          <path d="M10.293 14.293 8.464 12.464 6 15h12l-3.536-4.42-2.171 2.713z"></path>
          <path d="m19.207 2.207-1.414 1.414L19.207 5.035l1.414-1.414L22.035 2.207l-1.414-1.414zM15 2.207l1.414-1.414L17.828 2.207l-1.414 1.414z"></path>
        </svg>
        <h1>SnapForge</h1>
        <div class="subtitle">让您的图片处理体验如二次元般美好~</div>
    </div>
    <div class="header-actions">
        <a href="https://github.com/riceshowerX/SnapForge" target="_blank" title="{github_tooltip}">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16" style="vertical-align: -2px; margin-right: 8px;">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub
        </a>
        <a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" title="{feedback_tooltip}">{feedback_link_text}</a>
    </div>
    <div class="character-illustration"></div>
    """
    
    def __init__(self, translator: Callable[[str], str]):
        self._ = translator
    
    def load_resources(self):
        st.markdown(self.CUSTOM_CSS, unsafe_allow_html=True)
        st.markdown(self.HEADER_HTML_TEMPLATE.format(
            github_tooltip=self._('前往GitHub仓库'),
            feedback_tooltip=self._('反馈建议/提Issue'),
            feedback_link_text=self._("反馈建议")
        ), unsafe_allow_html=True)
        
        # 添加二次元风格字体
        st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
        body, .stTextInput, .stNumberInput, .stSelectbox, .stButton {
            font-family: 'Noto Sans JP', 'Noto Sans SC', 'Segoe UI', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def display_footer(self):
        st.markdown(f"""
        <div class="footer">
            <span>© 2025 <b>SnapForge</b> | {self._('由')} <a href="https://github.com/riceshowerX" target="_blank">riceshowerX</a> {self._('设计与开发')}</span>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #a0aec0;">
                {self._('二次元风格UI设计 | 像樱花般轻盈的图片处理体验')}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 辅助函数 (Helper Functions)
# -----------------------------------------------------------------------------
class TempFileRecord:
    """记录临时文件信息，便于清理"""
    def __init__(self, file_path: str, original_name: str):
        self.file_path = file_path
        self.original_name = original_name
        self.created_at = datetime.datetime.now()
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

@dataclass
class AppState:
    """改进的会话状态管理，避免内存泄漏"""
    # 使用临时文件路径代替存储io.BytesIO对象
    result_files: List[TempFileRecord] = field(default_factory=list)
    duplicate_groups: List[List[TempFileRecord]] = field(default_factory=list)
    run_dedup: bool = False
    log_messages: List[str] = field(default_factory=list)
    resource_manager: Optional[ResourceManager] = None
    
    @classmethod
    def init(cls) -> 'AppState':
        """初始化应用状态，创建资源管理器"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = cls()
            # 创建资源管理器
            st.session_state.app_state.resource_manager = ResourceManager()
        return st.session_state.app_state
        
    def cleanup(self):
        """清理所有临时资源"""
        if self.resource_manager:
            self.resource_manager.cleanup()
        # 清空文件记录
        self.result_files = []
        self.duplicate_groups = []

def save_uploaded_files(uploaded_files, resource_manager: ResourceManager) -> List[Tuple[str, str]]:
    """
    安全地保存上传文件，防止路径遍历攻击
    """
    file_data = []
    if not uploaded_files: 
        return []
    
    # 创建安全的临时目录
    temp_dir = resource_manager.create_temp_dir(prefix="snapforge_uploads_")
    output_dir = Path(temp_dir)
    
    for f in uploaded_files:
        f.seek(0)
        file_content = f.read()
        original_path = Path(f.name)
        
        # 安全清理文件名，防止路径遍历
        safe_name = "".join(c for c in original_path.stem if c.isalnum() or c in "._-").strip()
        if not safe_name:
            safe_name = f"image_{uuid.uuid4().hex[:6]}"
        ext = original_path.suffix.lower()
        
        # 确保扩展名安全
        if ext not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
            ext = ".png"  # 默认安全扩展名
            
        # 创建唯一文件名
        unique_name = f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"
        temp_path = output_dir / unique_name
        
        # 保存文件
        with open(temp_path, "wb") as out:
            out.write(file_content)
            
        # 记录文件信息
        file_size = os.path.getsize(temp_path)
        file_data.append((
            original_path.name,  # 保留原始文件名用于显示
            str(temp_path)       # 实际存储路径
        ))
        
    return file_data

def pack_files_to_zip(file_records: List[TempFileRecord]) -> io.BytesIO:
    """
    将文件打包为ZIP格式，确保文件名唯一避免冲突
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, record in enumerate(file_records):
            # 使用唯一名称防止压缩包内文件名冲突
            arcname = f"processed_{i}_{record.original_name}"
            with open(record.file_path, "rb") as f:
                zf.writestr(arcname, f.read())
    zip_buffer.seek(0)
    return zip_buffer

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小为易读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def display_results_grid(file_records: List[TempFileRecord], _: Callable[[str], str], num_columns: int = 4):
    """显示结果图片网格，添加二次元风格效果"""
    if not file_records: 
        return
        
    st.markdown("---")
    st.subheader(_("结果预览"))
    
    # 添加二次元风格的结果说明
    st.markdown(f'<div class="info-card">{_("共显示 {num} 个结果，点击图片可查看大图，享受二次元般的视觉体验~")}</div>'.format(num=len(file_records)), 
                unsafe_allow_html=True)
    
    # 创建图片网格
    for i in range(0, len(file_records), num_columns):
        cols = st.columns(num_columns)
        for j, col in enumerate(cols):
            if i + j < len(file_records):
                record = file_records[i + j]
                # 二次元风格图片卡片
                with col:
                    st.markdown(f'<div class="preview-image">', unsafe_allow_html=True)
                    # 显示图片
                    try:
                        with open(record.file_path, "rb") as f:
                            img_bytes = io.BytesIO(f.read())
                        st.image(img_bytes, caption=record.original_name, use_container_width=True)
                    except Exception as e:
                        st.error(_("无法显示图片"), icon="❌")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 添加二次元风格的文件信息
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 0.5rem; font-size: 0.85rem; color: #718096;">
                        <span style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); 
                                      -webkit-background-clip: text; 
                                      background-clip: text; 
                                      color: transparent;
                                      font-weight: 600;">
                            {record.original_name}
                        </span>
                        <br/>
                        <span style="color: #a0aec0;">{format_file_size(record.file_size)}</span>
                    </div>
                    """, unsafe_allow_html=True)

def get_filter_emoji(filter_type: FilterType) -> str:
    """为滤镜类型添加表情符号"""
    emoji_map = {
        FilterType.GRAYSCALE: "⚫",
        FilterType.SHARPEN: "✨",
        FilterType.BLUR: "☁️",
        FilterType.CONTOUR: "✏️",
        FilterType.EMBOSS: "🔲",
        FilterType.EDGE: "✂️",
        FilterType.ENHANCE: "🌈"
    }
    return emoji_map.get(filter_type, "")

def process_with_error_handling(func, *args, **kwargs):
    """带错误处理的函数执行"""
    try:
        return func(*args, **kwargs)
    except InvalidConfigError as e:
        st.error(f"❌ 配置错误: {str(e)}", icon="⚠️")
        logger.error(f"配置错误: {str(e)}")
        return None
    except FileProcessingError as e:
        st.error(f"❌ 文件处理错误: {str(e)}", icon="⚠️")
        logger.error(f"文件处理错误: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        st.error(f"❌ 发生未知错误: {str(e)}", icon="❗")
        logger.exception("发生未处理的异常")
        return None

def render_processing_options(_: Callable[[str], str]) -> ProcessConfig:
    """
    渲染批量处理选项，添加二次元风格设计
    """
    st.markdown(f'<h3 style="margin-top: 2rem; display: flex; align-items: center;">'
                f'<span style="background: linear-gradient(90deg, var(--primary-color), var(--accent-color)); '
                f'-webkit-background-clip: text; background-clip: text; color: transparent;">'
                f'🛠️ {_("图片处理参数")}</span></h3>', 
                unsafe_allow_html=True)
    
    # 二次元风格参数说明
    st.markdown(f'<div class="param-help">{_("设置图片处理的各项参数，调整后点击顶部的【开始处理图片】按钮应用。"
                                          "享受二次元般流畅的图片处理体验~")}</div>', 
                unsafe_allow_html=True)
    
    # 重命名、格式转换与压缩部分（二次元风格）
    with st.expander(_("✨ 重命名、格式转换与压缩"), expanded=True):
        st.markdown(f'<div class="param-help">{_("重命名、格式转换和质量压缩设置，让您的图片更加精致~")}</div>', 
                    unsafe_allow_html=True)
        
        enable_rename = st.checkbox(_("启用重命名"), value=True, 
                                   help=_("为您的图片添加独特的二次元风格命名"))
        col1, col2 = st.columns(2)
        prefix = col1.text_input(_("前缀"), "snap", disabled=not enable_rename,
                                help=_("例如：'snap' 会生成 snap_0001.jpg 等文件名"))
        start_num = col2.number_input(_("起始编号"), 1, 9999, 1, disabled=not enable_rename)
        
        # 添加命名模板帮助（二次元风格）
        st.markdown(f'<div class="param-help">{_("可用变量: {prefix}, {counter}, {original_name}, {ext}。"
                                              "例如：{prefix}_{counter:04d} 会生成 snap_0001.jpg")}</div>', 
                    unsafe_allow_html=True)
        naming_template = st.text_input(_("命名模板"), "{prefix}_{counter:04d}", disabled=not enable_rename)
        
        st.markdown("---")
        
        enable_convert = st.checkbox(_("启用格式转换"), 
                                   help=_("转换图片格式，适应不同平台需求"))
        col1, col2 = st.columns(2)
        target_ext = col1.selectbox(_("目标格式"), [".png", ".jpg", ".webp"], disabled=not enable_convert)
        enable_compress = col2.checkbox(_("启用质量压缩"), True, 
                                      help=_("压缩图片大小，保持良好画质"))
        quality = col2.slider(_("压缩质量"), 1, 100, 85, disabled=not enable_convert or not enable_compress)
        
        # 二次元风格质量指示器
        if enable_compress:
            quality_level = _("低") if quality < 30 else _("中") if quality < 70 else _("高")
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-top: -10px; margin-bottom: 10px;">
                <span style="margin-right: 8px; font-size: 0.85rem; color: #718096;">{_("质量等级")}:</span>
                <span style="background: {'#feb2b2' if quality < 30 else '#fc8c8c' if quality < 70 else '#ff6b6b'}; 
                              padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; color: white;">
                    {quality_level}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # 尺寸、水印与高级调整部分（二次元风格）
    with st.expander(_("🎨 尺寸、水印与高级调整")):
        st.markdown(f'<div class="param-help">{_("调整图片尺寸、添加水印和高级图像处理，打造专属二次元风格~")}</div>', 
                    unsafe_allow_html=True)
        
        enable_resize = st.checkbox(_("启用尺寸调整"), 
                                   help=_("调整图片尺寸，适应不同场景需求"))
        col1, col2 = st.columns(2)
        width = col1.number_input(_("宽"), 1, 8000, 800, disabled=not enable_resize)
        height = col2.number_input(_("高"), 1, 8000, 600, disabled=not enable_resize)
        
        # 创建模式映射（二次元风格）
        resize_mode_map = {
            _("适应边界") + " 📐": ResizeMode.CONTAIN,
            _("裁剪填充") + " ✂️": ResizeMode.COVER,
            _("拉伸") + " 📏": ResizeMode.STRETCH
        }
        mode_display = st.selectbox(_("模式"), list(resize_mode_map.keys()), disabled=not enable_resize)
        only_shrink = st.checkbox(_("仅缩小"), True, disabled=not enable_resize,
                                 help=_("只缩小图片，不放大，保持图片清晰度"))
        
        st.markdown("---")
        
        # 核心设置和元数据（二次元风格）
        col1, col2 = st.columns(2)
        preserve_meta = col1.checkbox(_("保留EXIF"), True,
                                     help=_("保留图片的拍摄信息等元数据"))
        cpus = os.cpu_count() or 1
        num_proc = col2.number_input(
            _("核心数"), 
            min_value=1, 
            max_value=cpus, 
            value=max(1, cpus-1),
            help=_("使用的核心数越多处理越快，但可能影响系统性能。建议保留1核给系统~")
        )
        
        # 水印设置（二次元风格）
        st.markdown(f'<div class="param-help">{_("水印设置，为您的图片添加个性化标识~")}</div>', 
                    unsafe_allow_html=True)
        enable_wm = st.checkbox(_("启用水印"), 
                              help=_("在图片上添加文字水印，防止盗用"))
        wm_cfg = None
        if enable_wm:
            col1, col2, col3 = st.columns(3)
            wm_txt = col1.text_input(_("内容"), "SnapForge ©", 
                                   help=_("水印显示的文字内容"))
            wm_pos = col2.selectbox(_("位置"), ["bottom-right", "center", "top-left", "top-right", "bottom-left"])
            wm_size = col3.slider(_("字号"), 10, 200, 36)
            wm_cfg = WatermarkConfig(wm_txt, size=wm_size, position=wm_pos)
        
        # 裁剪设置（二次元风格）
        st.markdown(f'<div class="param-help">{_("裁剪设置，精准裁剪您需要的部分~")}</div>', 
                    unsafe_allow_html=True)
        enable_crop = st.checkbox(_("启用裁剪"), 
                                help=_("裁剪图片的特定区域"))
        crop_cfg = None
        if enable_crop:
            col1, col2, col3, col4 = st.columns(4)
            x = col1.number_input(_("X"), min_value=0, value=0)
            y = col2.number_input(_("Y"), min_value=0, value=0)
            crop_width = col3.number_input(_("裁剪宽"), min_value=0, value=0)
            crop_height = col4.number_input(_("裁剪高"), min_value=0, value=0)
            crop_cfg = CropConfig(x, y, crop_width, crop_height)
        
        # 旋转和滤镜（二次元风格）
        st.markdown(f'<div class="param-help">{_("旋转和滤镜设置，为图片添加独特效果~")}</div>', 
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        rotation = col1.number_input(_("旋转角度"), -360, 360, 0, 1)
        
        # 滤镜映射（二次元风格）
        filter_map = {"无": None}
        for f in FilterType:
            filter_map[f"{f.value} {get_filter_emoji(f)}"] = f
        
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
    """主应用界面，添加二次元风格元素"""
    tab_titles = [
        _("✨ 批量处理"), 
        _("🔍 信息查看"), 
        _("👯‍♀️ 图片去重"), 
        _("📋 处理记录")
    ]
    tabs = st.tabs(tab_titles)
    
    # 批量处理标签
    with tabs[0]:
        processor = ImageProcessor()
        st.markdown(f'<h3>📂 {_("上传文件")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("拖放图片到此区域或点击上传。支持JPG, PNG, BMP, WEBP格式。"
                                              "最大文件大小: 200MB。注意: 上传前请确保图片不包含敏感信息。")}</div>', 
                    unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            _("上传图片"), 
            type=["jpg", "png", "bmp", "webp"], 
            accept_multiple_files=True, 
            key="batch_upload"
        )
        
        # 二次元风格的文件上传区域
        if not uploaded_files:
            st.markdown("""
            <div style="border: 2px dashed #e2e8f0; border-radius: 1rem; padding: 2rem; text-align: center; background: #f8fafc;">
                <div style="font-size: 3rem; color: #cbd5e0; margin-bottom: 1rem;">🖼️</div>
                <h3 style="color: #718096; margin-bottom: 0.5rem;">{upload_title}</h3>
                <p style="color: #a0aec0; margin-bottom: 1.5rem;">{upload_desc}</p>
                <div style="background: linear-gradient(90deg, #ff6b6b, #ff5252); 
                            color: white; padding: 0.6rem 1.5rem; border-radius: 0.5rem; 
                            display: inline-block; font-weight: 600; cursor: pointer;
                            box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);">
                    {upload_button}
                </div>
            </div>
            """.format(
                upload_title=_("拖放图片到这里或点击上传"),
                upload_desc=_("支持JPG, PNG, BMP, WEBP格式。最大文件大小: 200MB。"),
                upload_button=_("选择图片")
            ), unsafe_allow_html=True)
        
        config = render_processing_options(_)
        
        # 添加参数验证
        if st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not uploaded_files):
            # 清理之前的处理结果
            app_state.result_files = []
            app_state.log_messages = [_("任务开始...")]
            
            with st.container():
                log_area = st.empty()
                progress_bar = st.empty()
                result_area = st.empty()
                dl_area = st.empty()
                
                def progress_callback(pct: float, filename: str = ""):
                    """进度回调函数"""
                    progress_bar.progress(pct, f"{_('处理中')}: {filename}" if filename else _("处理中..."))
                
                try:
                    # 保存上传的文件
                    file_data = save_uploaded_files(uploaded_files, app_state.resource_manager)
                    
                    # 显示处理信息
                    with st.spinner(_("图片并行处理中...")):
                        result_area.info(
                            _("使用 {num} 核心加速，共 {total} 个文件").format(
                                num=config.num_processes, 
                                total=len(file_data)
                            ), 
                            icon="⏳"
                        )
                        
                        # 正确使用batch_process方法
                        input_paths = [f[1] for f in file_data]  # 获取实际路径
                        processed, total, result_paths, file_mapping = processor.batch_process(
                            input_paths, 
                            str(TEMP_DIR), 
                            config, 
                            progress_callback
                        )
                        
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
                            
                            # 将结果文件转换为TempFileRecord
                            result_records = []
                            for orig_path, result_path in file_mapping.items():
                                # 找到原始文件名
                                original_name = next((f[0] for f in file_data if f[1] == orig_path), Path(orig_path).name)
                                # 创建记录
                                record = TempFileRecord(result_path, original_name)
                                result_records.append(record)
                            
                            # 保存结果数据
                            app_state.result_files = result_records
                            
                            # 提供下载按钮
                            if app_state.result_files:
                                zip_data = pack_files_to_zip(app_state.result_files)
                                dl_area.download_button(
                                    _("⬇️ 下载全部结果 ({num}个文件)").format(num=len(app_state.result_files)),
                                    zip_data,
                                    "processed_images.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                    key="download_all_results"
                                )
                                
                                # 显示结果预览
                                display_results_grid(app_state.result_files, _)
                except Exception as e:
                    logger.exception("处理图片时出错")
                    st.error(_("处理中发生严重错误: {error}").format(error=str(e)), icon="❗")
    
    # 信息查看标签
    with tabs[1]:
        st.markdown(f'<h3>🔍 {_("图片信息查看")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("上传图片以查看详细信息")}</div>', 
                    unsafe_allow_html=True)
        uploaded_info = st.file_uploader(
            _("上传图片以查看信息"), 
            type=["jpg", "png", "bmp", "webp"], 
            key="info_upload"
        )
        
        if uploaded_info:
            try:
                # 保存并处理文件
                uploaded_info.seek(0)
                file_content = uploaded_info.read()
                img_bytes = io.BytesIO(file_content)
                
                # 显示图片
                img_bytes.seek(0)
                st.image(img_bytes, use_container_width=True)
                
                # 创建临时文件以获取信息
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_info.name).suffix) as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name
                
                try:
                    # 显示基本信息
                    img = Image.open(img_bytes)
                    col1, col2, col3 = st.columns(3)
                    col1.info(f"**{_('尺寸')}:** {img.width}x{img.height}")
                    col2.info(f"**{_('大小')}:** {len(file_content)/1024:.1f}KB")
                    col3.info(f"**{_('格式')}:** {img.format}")
                    
                    # 显示EXIF信息（如果存在）
                    try:
                        exif_data = get_exif_data(tmp_path)
                        if exif_data:
                            with st.expander(_("EXIF信息")):
                                for tag, value in exif_data.items():
                                    st.text(f"{tag}: {value}")
                    except Exception as e:
                        logger.debug(f"获取EXIF信息失败: {str(e)}")
                    
                    # 显示颜色分析
                    try:
                        main_color, palette = get_image_main_color(tmp_path)
                        if main_color:
                            with st.expander(_("主色调分析")):
                                # 显示主色调
                                st.markdown(
                                    f'<div style="background-color: #{main_color[0]:02x}{main_color[1]:02x}{main_color[2]:02x}; '
                                    f'padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">'
                                    f'<p style="color: white; font-weight: bold;">{_("主色调:")} '
                                    f'#{main_color[0]:02x}{main_color[1]:02x}{main_color[2]:02x}</p></div>',
                                    unsafe_allow_html=True
                                )
                                
                                # 显示调色板
                                if palette:
                                    st.subheader(_("调色板"))
                                    cols = st.columns(len(palette))
                                    for i, color in enumerate(palette):
                                        cols[i].markdown(
                                            f'<div style="background-color: #{color[0]:02x}{color[1]:02x}{color[2]:02x}; '
                                            f'padding: 1rem; border-radius: 0.5rem; height: 50px;"></div>',
                                            unsafe_allow_html=True
                                        )
                                        cols[i].text(f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
                    except Exception as e:
                        logger.debug(f"获取主色调失败: {str(e)}")
                    
                    # 显示直方图
                    try:
                        hist_buf = plot_image_histogram(tmp_path)
                        if hist_buf:
                            st.subheader(_("RGB直方图"))
                            st.image(hist_buf)
                    except Exception as e:
                        logger.debug(f"生成直方图失败: {str(e)}")
                finally:
                    # 清理临时文件
                    os.unlink(tmp_path)
            except Exception as e:
                st.error(_("无法打开图片: {error}").format(error=str(e)))
    
    # 图片去重标签
    with tabs[2]:
        st.markdown(f'<h3>👯‍♀️ {_("图片去重")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("查找并标记重复或相似的图片")}</div>', 
                    unsafe_allow_html=True)
        
        # 添加阈值说明
        st.markdown(f'<div class="param-help">{_("值越小越严格（0=完全相同，20=非常宽松）")}</div>', 
                    unsafe_allow_html=True)
        threshold = st.slider(_("相似度阈值 (值越小越严格)"), 0, 20, 8)
        
        files = st.file_uploader(
            _("上传需要去重的图片(至少2张)"), 
            type=["jpg", "png", "bmp", "webp"], 
            accept_multiple_files=True, 
            key="dedup_upload"
        )
        
        if st.button(_("查找重复图片"), use_container_width=True, disabled=len(files) < 2):
            app_state.run_dedup = True
            app_state.duplicate_groups = []
            with st.spinner(_("正在查找重复图片...")):
                # 创建临时文件以进行去重
                temp_files = []
                try:
                    # 保存上传的文件
                    file_data = save_uploaded_files(files, app_state.resource_manager)
                    temp_files = [f[1] for f in file_data]  # 获取实际路径
                    
                    # 执行去重
                    groups = find_duplicate_images(
                        temp_files, 
                        threshold
                    )
                    
                    # 转换为TempFileRecord格式
                    for group in groups:
                        record_group = []
                        for path in group:
                            # 找到原始文件名
                            original_name = next((f[0] for f in file_data if f[1] == path), Path(path).name)
                            record = TempFileRecord(path, original_name)
                            record_group.append(record)
                        app_state.duplicate_groups.append(record_group)
                except Exception as e:
                    logger.error(f"去重过程中出错: {str(e)}")
                    st.error(_("去重过程中发生错误: {error}").format(error=str(e)))
        
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
                        display_results_grid(group, _, num_columns=3)
                        
                        # 提供选择最佳图片的选项
                        st.markdown(f"**{_('建议保留:')}**")
                        best_image = select_best_image_in_group([r.file_path for r in group])
                        if best_image:
                            try:
                                # 找到对应的记录
                                best_record = next((r for r in group if r.file_path == best_image), None)
                                if best_record:
                                    with open(best_record.file_path, "rb") as f:
                                        img_bytes = io.BytesIO(f.read())
                                    st.image(img_bytes, width=200)
                                    st.text(best_record.original_name)
                            except Exception as e:
                                st.error(_("无法显示最佳图片"))
    
    # 处理记录标签
    with tabs[3]:
        st.markdown(f'<h3>📋 {_("处理记录")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-help">{_("显示最近处理的图片结果")}</div>', 
                    unsafe_allow_html=True)
        
        if app_state.result_files:
            st.success(
                _("✅ 最近成功处理 {num} 个文件").format(
                    num=len(app_state.result_files)
                )
            )
            
            # 提供下载所有结果的选项
            zip_data = pack_files_to_zip(app_state.result_files)
            st.download_button(
                _("⬇️ 下载全部结果 ({num}个文件)").format(num=len(app_state.result_files)),
                zip_data,
                "recent_processing_results.zip",
                mime="application/zip",
                use_container_width=True,
                key="download_history"
            )
            
            # 显示结果
            display_results_grid(app_state.result_files, _)
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
        
        # 修复：先获取默认翻译器，不要尝试翻译语言选择框的标签
        lang = st.selectbox("Language/语言", ["中文", "English"])
        _ = get_translator(lang)  # 现在定义翻译函数
        
        st.header(_("⚙️ 设置"))
        
        # 状态清理按钮
        if st.button(_("清理会话状态"), use_container_width=True, type="secondary"):
            # 清理会话状态
            app_state.cleanup()
            st.success(_("会话已重置！页面将刷新。"))
            st.rerun()
        
        # 添加应用信息
        st.markdown("---")
        st.markdown(f"**{_('版本')}**: 2.1.0")
        st.markdown(f"**{_('开发者')}**: riceshowerX")
        st.markdown(f"**{_('GitHub')}**: [SnapForge](https://github.com/riceshowerX/SnapForge)")
        
        # 添加使用说明
        st.markdown("---")
        st.markdown(f"### {_('使用说明')}")
        st.markdown(f"- {_('上传图片后设置处理参数')}")
        st.markdown(f"- {_('点击【开始处理图片】按钮应用')}")
        st.markdown(f"- {_('处理结果可预览和下载')}")
        st.markdown(f"- {_('使用侧边栏清理会话状态')}")
    
    # 加载UI资源 - 现在 _ 已经定义
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
