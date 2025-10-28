# app.py (Final, Upgraded and Corrected Version)

import streamlit as st
import zipfile
import io
import tempfile
import shutil
import os
import uuid
import time
import logging
import atexit
import json
import yaml
from pathlib import Path
from PIL import Image
from dataclasses import dataclass, field, asdict
from typing import List, Callable, Dict, Any, Set, Optional, Union

# 获取logger实例
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
        plot_image_histogram, select_best_image_in_group
    )
    # 导入性能监控模块
    from performance_monitor import performance_monitor, debug_helper, get_performance_dashboard, monitor_performance
except ImportError as e:
    st.error(
        f"关键错误：无法导入必要的模块。错误: {e}"
        "请确保您已经拥有升级后的后端逻辑文件 'logic.py'，并与此应用脚本 'app.py' 放在同一目录下。"
    )
    st.stop()

# 假设的多语言翻译工具
try:
    from utils_i18n import get_translator
except ImportError:
    def get_translator(lang: str):
        return lambda s: s

# -----------------------------------------------------------------------------
# 2. UI与状态管理封装 (UI & State Management Encapsulation)
# -----------------------------------------------------------------------------

@dataclass
class AppState:
    """集中管理所有会话状态，避免魔法字符串，增强代码可维护性"""
    # 修复缺陷1：使用更安全的资源管理方式
    result_file_paths: List[Path] = field(default_factory=list)
    duplicate_groups: List[List[str]] = field(default_factory=list)
    run_dedup: bool = False
    log_messages: List[str] = field(default_factory=list)
    temp_dirs: Set[Path] = field(default_factory=set)  # 跟踪所有临时目录
    # 新增：配置预设功能
    presets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    current_preset: Optional[str] = None
    
    def register_temp_dir(self, temp_dir: Path):
        """注册临时目录以便后续清理"""
        self.temp_dirs.add(temp_dir)
    
    def cleanup_resources(self):
        """清理所有临时资源"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    logging.info(f"已清理临时目录: {temp_dir}")
                except Exception as e:
                    logging.error(f"清理临时目录失败: {temp_dir}, 错误: {e}")
        self.temp_dirs.clear()
    
    def save_preset(self, name: str, config: Dict[str, Any]):
        """保存配置预设"""
        self.presets[name] = config
    
    def delete_preset(self, name: str):
        """删除配置预设"""
        if name in self.presets:
            del self.presets[name]

    @classmethod
    def init(cls) -> 'AppState':
        """在Streamlit会话中初始化或获取状态对象"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = cls()
        return st.session_state.app_state

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
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cg fill-rule='evenodd'%3E%3Cg fill='%232a324f' fill-opacity='0.2'%3E%3Cpath d='M0 38.59l2.83-2.83 1.41 1.41L1.41 40H0v-1.41zM0 1.4l2.83 2.83 1.41-1.41L1.41 0H0v1.41zM38.59 40l-2.83-2.83 1.41-1.41L40 38.59V40h-1.41zM40 1.41l-2.83 2.83-1.41-1.41L38.59 0H40v1.41z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
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
    </style>
    """
    HEADER_HTML_TEMPLATE = """
    <div class="header-banner">
        <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 3H4C2.897 3 2 3.897 2 5v14c0 1.103.897 2 2 2h16c1.103 0 2-.897 2-1V5c0-1.103-.897-2-2-2zM4 19V5h16l.002 14H4z"></path>
          <path d="M10.293 14.293 8.464 12.464 6 15h12l-3.536-4.42-2.171 2.713z"></path>
          <path d="m19.207 2.207-1.414 1.414L19.207 5.035l1.414-1.414L22.035 2.207l-1.414-1.414zm-2.828 4.243L15 8.464l1.414 1.414 1.414-1.414L19.243 7.05l-1.414-1.414zM15 2.207l1.414-1.414L17.828 2.207l-1.414 1.414z"></path>
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
    
    def create_info_card(self, title: str, content: str, icon: str = "ℹ️"):
        """创建信息卡片组件"""
        st.markdown(f"""
        <div class="res-card" style="margin: 10px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                <h4 style="margin: 0; color: #333;">{title}</h4>
            </div>
            <p style="margin: 0; color: #666; line-height: 1.5;">{content}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_stat_card(self, title: str, value: str, subtitle: str = "", color: str = "#406aff"):
        """创建统计卡片组件"""
        st.markdown(f"""
        <div class="res-card" style="text-align: center; padding: 20px; margin: 10px 0;">
            <div style="font-size: 32px; font-weight: bold; color: {color}; margin-bottom: 5px;">{value}</div>
            <div style="font-size: 14px; color: #666; font-weight: 600;">{title}</div>
            {f'<div style="font-size: 12px; color: #999; margin-top: 5px;">{subtitle}</div>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def create_progress_with_stats(self, current: int, total: int, success: int = 0, errors: int = 0):
        """创建带统计信息的进度条"""
        progress = current / total if total > 0 else 0
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.progress(progress, text=f"处理进度: {current}/{total} ({progress*100:.1f}%)")
        
        with col2:
            st.metric("成功", success, delta=f"{success/total*100:.1f}%" if total > 0 else "0%")
        
        with col3:
            st.metric("错误", errors, delta=f"{errors/total*100:.1f}%" if total > 0 else "0%")
        
        return progress
    
    def create_loading_spinner(self, message: str = "处理中..."):
        """创建加载动画"""
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #406aff; border-radius: 50%; animation: spin 2s linear infinite;"></div>
            <p style="margin-top: 10px; color: #666;">{message}</p>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. 辅助函数 (Helper Functions)
# -----------------------------------------------------------------------------

def save_uploaded_files(uploaded_files, output_dir: Path) -> List[Path]:
    """
    将上传文件保存到临时目录。
    使用UUID确保即使原始文件名相同或清理后相同，也不会发生文件覆盖。
    增加了文件类型验证，只接受图像文件。
    """
    file_paths = []
    if not uploaded_files: return []
    
    # 允许的图像文件扩展名
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    
    for f in uploaded_files:
        try:
            f.seek(0)
            original_path = Path(f.name)
            file_ext = original_path.suffix.lower()
            
            # 验证文件类型
            if file_ext not in ALLOWED_EXTENSIONS:
                st.warning(f"跳过非图像文件: {original_path.name}")
                continue
                
            # 进一步验证文件内容是否为有效图像
            try:
                img_data = f.getvalue()
                Image.open(io.BytesIO(img_data))
                f.seek(0)  # 重置文件指针
            except Exception:
                st.warning(f"跳过无效图像文件: {original_path.name}")
                continue
            
            safe_filename = "".join(c for c in original_path.name if c.isalnum() or c in "._-").strip() or "unnamed_file"
            
            # 使用UUID生成唯一前缀，防止任何形式的文件名冲突
            unique_prefix = uuid.uuid4().hex[:8]
            temp_filename = f"{unique_prefix}_{safe_filename}"
            temp_path = output_dir / temp_filename
            
            with open(temp_path, "wb") as out:
                out.write(f.getvalue())
            file_paths.append(temp_path)
        except Exception as e:
            st.warning(f"处理文件 {getattr(f, 'name', '未知')} 时出错: {str(e)}")
    
    return file_paths

def pack_files_to_zip(file_paths: List[Path]) -> io.BytesIO:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            if file_path.exists(): zf.write(file_path, arcname=file_path.name)
    zip_buffer.seek(0)
    return zip_buffer

def display_results_grid(image_paths: List[Path], _: Callable[[str], str], num_columns: int = 4):
    if not image_paths: return
    st.markdown("---"); st.subheader(_("结果预览"))
    for i in range(0, len(image_paths), num_columns):
        cols = st.columns(num_columns)
        for j, col in enumerate(cols):
            if i + j < len(image_paths):
                path = Path(image_paths[i + j])  # 确保转换为Path对象
                if path.exists():
                    col.image(str(path), caption=path.name, use_container_width=True)
                else:
                    col.warning(f"{path.name}\n{_('文件不存在')}")

def render_processing_options(_: Callable[[str], str], app_state: AppState) -> ProcessConfig:
    """
    【修复缺陷3】渲染批量处理选项，并使用新的分层结构创建ProcessConfig。
    新增：配置预设功能
    """
    st.markdown(f'<h3 style="margin-top: 2rem;">{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    
    # 配置预设功能
    if hasattr(app_state, 'presets'):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            preset_name = st.selectbox(
                _("选择预设"), 
                [_("默认")] + list(app_state.presets.keys()),
                index=0 if not app_state.current_preset else list(app_state.presets.keys()).index(app_state.current_preset) + 1 if app_state.current_preset in app_state.presets else 0
            )
        with col2:
            new_preset_name = st.text_input(_("保存为新预设"), "")
        with col3:
            save_preset_btn = st.button(_("保存预设"), disabled=not new_preset_name)
        
        # 删除预设按钮
        if app_state.presets:
            del_preset_name = st.selectbox(_("删除预设"), [""] + list(app_state.presets.keys()), index=0)
            if st.button(_("删除"), disabled=not del_preset_name):
                app_state.delete_preset(del_preset_name)
                st.success(_("预设已删除"))
                st.rerun()
    
    # 默认配置
    default_config = {
        'enable_rename': True,
        'prefix': 'image',
        'start_num': 1,
        'naming_template': '{prefix}_{counter:04d}',
        'enable_convert': False,
        'target_ext': '.png',
        'enable_compress': True,
        'quality': 85,
        'progressive_jpeg': True,
        'enable_resize': False,
        'width': 800,
        'height': 600,
        'resize_mode': _("适应边界"),
        'only_shrink': True,
        'preserve_meta': True,
        'num_proc': max(1, os.cpu_count() or 1) // 2,
        'enable_wm': False,
        'wm_txt': 'SnapForge',
        'wm_pos': 'bottom-right',
        'wm_size': 36,
        'enable_crop': False,
        'crop_x': 0,
        'crop_y': 0,
        'crop_width': 100,
        'crop_height': 100,
        'rotate_angle': 0,
        'filter': ""
    }
    
    # 应用选中的预设
    config = default_config.copy()
    if hasattr(app_state, 'presets') and preset_name != _("默认") and preset_name in app_state.presets:
        config.update(app_state.presets[preset_name])
        app_state.current_preset = preset_name
    
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        enable_rename = st.checkbox(_("启用重命名"), value=config['enable_rename'])
        c1, c2 = st.columns(2)
        prefix = c1.text_input(_("前缀"), config['prefix'], disabled=not enable_rename)
        start_num = c2.number_input(_("起始编号"), 1, 10000, config['start_num'], disabled=not enable_rename)
        naming_template = st.text_input(_("命名模板"), config['naming_template'], disabled=not enable_rename)
        
        c1, c2 = st.columns(2)
        enable_convert = c1.checkbox(_("启用格式转换"), value=config['enable_convert'])
        target_ext = c1.selectbox(_("目标格式"), [".png", ".jpg", ".webp"], index=[".png", ".jpg", ".webp"].index(config['target_ext']), disabled=not enable_convert)
        enable_compress = c2.checkbox(_("启用质量压缩"), config['enable_compress'])
        quality = c2.slider(_("压缩质量"), 1, 100, config['quality'], disabled=not enable_compress or not enable_convert)
        
        # 新增：优化文件大小选项
        progressive_jpeg = st.checkbox(_("渐进式JPEG"), value=True, disabled=not enable_convert or not (target_ext.lower() == '.jpg' or target_ext.lower() == '.jpeg'), help=_(
"生成渐进式JPEG，提高网页加载体验"))

    with st.expander(_("尺寸、水印与高级调整")):
        enable_resize = st.checkbox(_("启用尺寸调整"), value=config['enable_resize'])
        c1, c2 = st.columns(2)
        w = c1.number_input(_("宽"), 1, 8000, config['width'], disabled=not enable_resize)
        h = c2.number_input(_("高"), 1, 8000, config['height'], disabled=not enable_resize)
        resize_map = {_("适应边界"): ResizeMode.CONTAIN, _("裁剪填充"): ResizeMode.COVER, _("拉伸"): ResizeMode.STRETCH}
        mode_disp = st.selectbox(_("模式"), list(resize_map.keys()), index=list(resize_map.keys()).index(config['resize_mode']) if config['resize_mode'] in resize_map.keys() else 0, disabled=not enable_resize)
        only_shrink = st.checkbox(_("仅缩小"), config['only_shrink'], disabled=not enable_resize)
        
        # 新增：边框设置
        enable_border = st.checkbox(_("添加边框"), disabled=not enable_resize)
        if enable_border and enable_resize:
            border_color = st.color_picker(_("边框颜色"), "#000000", disabled=not enable_resize)
            border_width = st.slider(_("边框宽度"), 1, 50, 5, disabled=not enable_resize)
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        preserve_meta = c1.checkbox(_("保留EXIF"), config['preserve_meta'])
        cpus = os.cpu_count() or 1
        num_proc = c2.number_input(_("核心数"), 1, cpus, config['num_proc'])
        
        enable_wm = st.checkbox(_("启用水印"), value=config['enable_wm'])
        wm_cfg = None
        if enable_wm: 
            c1, c2, c3 = st.columns(3)
            wm_txt = c1.text_input(_("内容"), config['wm_txt'])
            wm_pos = c2.selectbox(_("位置"), ["bottom-right", "center"], index=["bottom-right", "center"].index(config['wm_pos']) if config['wm_pos'] in ["bottom-right", "center"] else 0)
            wm_size = c3.slider(_("字号"), 10, 200, config['wm_size'])
            
            # 新增：水印高级设置
            st.markdown("**" + _("水印高级设置") + "**")
            c1, c2, c3 = st.columns(3)
            wm_color = c1.color_picker(_("字体颜色"), "#ffffff")
            wm_opacity = c2.slider(_("透明度"), 0.1, 1.0, 0.8, step=0.1)
            wm_bg = c3.checkbox(_("背景"), False)
            if wm_bg:
                wm_bg_color = st.color_picker(_("背景颜色"), "#000000")
                wm_bg_opacity = st.slider(_("背景透明度"), 0.1, 1.0, 0.5, step=0.1)
            
            wm_cfg = WatermarkConfig(wm_txt, size=wm_size, position=wm_pos)
            # 动态添加额外属性
            setattr(wm_cfg, 'color', wm_color)
            setattr(wm_cfg, 'opacity', wm_opacity)
            if wm_bg:
                setattr(wm_cfg, 'background', True)
                setattr(wm_cfg, 'bg_color', wm_bg_color)
                setattr(wm_cfg, 'bg_opacity', wm_bg_opacity)

        enable_crop = st.checkbox(_("启用裁剪"), value=config['enable_crop'])
        crop_cfg = None
        if enable_crop: 
            c1, c2, c3, c4 = st.columns(4)
            x = c1.number_input("X", 0, 10000, config['crop_x'])
            y = c2.number_input("Y", 0, 10000, config['crop_y'])
            cw = c3.number_input(_("裁剪宽"), 1, 10000, config['crop_width'])
            ch = c4.number_input(_("裁剪高"), 1, 10000, config['crop_height'])
            crop_cfg = CropConfig(x, y, cw, ch)
        
        # 新增：特效调整
        st.markdown("**" + _("特效调整") + "**")
        c1, c2, c3, c4 = st.columns(4)
        brightness = c1.slider(_("亮度"), -100, 100, 0)
        contrast = c2.slider(_("对比度"), -100, 100, 0)
        saturation = c3.slider(_("饱和度"), -100, 100, 0)
        sharpness = c4.slider(_("锐度"), -100, 100, 0)
        
        c1, c2 = st.columns(2)
        rot = c1.number_input(_("旋转角度"), -360, 360, config['rotate_angle'], 1)
        flt_map = {"": None, **{f.value: f for f in FilterType}}
        flt_disp = c2.selectbox(_("滤镜"), list(flt_map.keys()), index=list(flt_map.keys()).index(config['filter']) if config['filter'] in flt_map.keys() else 0)
    
    # 保存当前配置为预设
    current_config = {
        'enable_rename': enable_rename,
        'prefix': prefix,
        'start_num': start_num,
        'naming_template': naming_template,
        'enable_convert': enable_convert,
        'target_ext': target_ext,
        'enable_compress': enable_compress,
        'quality': quality,
        'progressive_jpeg': progressive_jpeg,
        'enable_resize': enable_resize,
        'width': w,
        'height': h,
        'resize_mode': mode_disp,
        'only_shrink': only_shrink,
        'preserve_meta': preserve_meta,
        'num_proc': num_proc,
        'enable_wm': enable_wm,
        'wm_txt': wm_txt if enable_wm else config['wm_txt'],
        'wm_pos': wm_pos if enable_wm else config['wm_pos'],
        'wm_size': wm_size if enable_wm else config['wm_size'],
        'enable_crop': enable_crop,
        'crop_x': x if enable_crop else config['crop_x'],
        'crop_y': y if enable_crop else config['crop_y'],
        'crop_width': cw if enable_crop else config['crop_width'],
        'crop_height': ch if enable_crop else config['crop_height'],
        'rotate_angle': rot,
        'filter': flt_disp
    }
    
    if hasattr(app_state, 'presets') and save_preset_btn and new_preset_name:
        app_state.save_preset(new_preset_name, current_config)
        st.success(_("预设已保存"))
        st.rerun()

    return ProcessConfig(
        rename_config=RenameConfig(prefix, start_num, naming_template) if enable_rename else None,
        convert_config=ConvertConfig(target_ext, quality) if enable_convert and enable_compress else ConvertConfig(target_ext) if enable_convert else None,
        resize_config=ResizeConfig(w, h, resize_map[mode_disp], only_shrink) if enable_resize else None,
        watermark_config=wm_cfg, crop_config=crop_cfg,
        rotate_config=RotateConfig(rot) if rot!=0 else None,
        filter_config=FilterConfig(flt_map[flt_disp]) if flt_map[flt_disp] else None,
        preserve_metadata=preserve_meta, num_processes=num_proc,
    )

# -----------------------------------------------------------------------------
# 4. 主应用渲染 (Main Application Rendering)
# -----------------------------------------------------------------------------

def main_app(_: Callable[[str], str], TEMP_DIR: Path, app_state: AppState, ui):
    tab_titles = [_("批量处理"), _("信息查看"), _("图片去重"), _("处理记录"), _("性能监控")]
    tabs = st.tabs(tab_titles)

    with tabs[0]: # 批量处理
        processor = ImageProcessor()
        
        # 使用新的UI组件
        ui.create_info_card(
            _("批量图片处理"),
            _("支持批量上传JPG、PNG、BMP、WebP格式图片，提供重命名、格式转换、尺寸调整、水印添加等丰富功能。大文件处理可能需要更长时间。"),
            "🖼️"
        )
        
        def on_batch_upload_change():
            app_state.result_file_paths.clear()
            app_state.log_messages.clear()
        
        uploaded_files = st.file_uploader(_("上传图片"), type=["jpg","png","bmp","webp"], accept_multiple_files=True, key="batch_upload", on_change=on_batch_upload_change)
        
        # 显示上传的文件信息
        if uploaded_files:
            # 计算总文件大小
            total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024 / 1024
            
            col1, col2, col3 = st.columns(3)
            with col1:
                ui.create_stat_card(_("文件数量"), str(len(uploaded_files)), _("个图片文件"))
            with col2:
                ui.create_stat_card(_("总大小"), f"{total_size:.1f}", _("MB"))
            with col3:
                avg_size = total_size / len(uploaded_files) if uploaded_files else 0
                ui.create_stat_card(_("平均大小"), f"{avg_size:.1f}", _("MB/文件"))
            
            # 显示文件列表（可选）
            if st.checkbox(_("显示文件列表")):
                st.markdown("**" + _("上传的文件列表") + "**")
                for i, f in enumerate(uploaded_files, 1):
                    file_size = len(f.getvalue()) / 1024
                    st.text(f"{i}. {f.name} ({file_size:.1f} KB)")
        
        config = render_processing_options(_, app_state)
        if st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not uploaded_files):
            app_state.result_file_paths.clear(); app_state.log_messages=[_("任务开始...")]
            with st.container():
                progress_container = st.empty()
                result_area = st.empty()
                stats_container = st.empty()
                
                # 改进的进度回调函数
                def progress_cb(pct, filename="", success_count=0, error_count=0):
                    with progress_container:
                        ui.create_progress_with_stats(
                            int(pct * len(uploaded_files)), 
                            len(uploaded_files), 
                            success_count, 
                            error_count
                        )
                        if filename:
                            st.info(f"{_("正在处理")}: {Path(filename).name}")
                
                try:
                    # 预处理验证
                    if len(uploaded_files) > 100:
                        ui.create_info_card(
                            _("文件数量提醒"),
                            _("上传文件较多，处理时间可能较长。建议分批处理以获得更好的体验。"),
                            "⚠️"
                        )
                    
                    file_paths = save_uploaded_files(uploaded_files, TEMP_DIR)
                    
                    if not file_paths:
                        result_area.error(_("❌ 没有有效的图片文件可供处理。"))
                        return
                    
                    with st.spinner(_("图片并行处理中...")):
                        result_area.info(_("使用 {} 核心加速处理...").format(config.num_processes), icon="⏳")
                        
                        # 初始化进度显示
                        progress_cb(0, "", 0, 0)
                        
                        p, t, r_paths = processor.batch_process([str(p) for p in file_paths], str(TEMP_DIR), config, progress_cb)
                        
                        # 处理完成
                        progress_cb(1.0, _("处理完成"), p, t-p)
                        
                        if not r_paths:
                            result_area.error(_("❌ 未成功处理任何图片。"))
                        else:
                            result_area.success(_("✅ 处理完成：{} / {}").format(p, t))
                            
                            # 计算处理统计信息
                            total_original_size = sum(f.stat().st_size for f in file_paths)
                            total_processed_size = sum(f.stat().st_size for f in [Path(p) for p in r_paths] if f.exists())
                            size_reduction = ((total_original_size - total_processed_size) / total_original_size * 100) if total_original_size > 0 else 0
                            
                            # 使用新的统计卡片显示信息
                            with stats_container:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    ui.create_stat_card(
                                        _("原始大小"), 
                                        f"{total_original_size / 1024 / 1024:.1f}", 
                                        _("MB")
                                    )
                                with col2:
                                    ui.create_stat_card(
                                        _("处理后大小"), 
                                        f"{total_processed_size / 1024 / 1024:.1f}", 
                                        _("MB")
                                    )
                                with col3:
                                    ui.create_stat_card(
                                        _("节省空间"), 
                                        f"{size_reduction:.1f}", 
                                        _("%")
                                    )
                            
                            # 记录处理历史
                            import datetime
                            processing_details = []
                            if config.rename_config:
                                processing_details.append(_("重命名"))
                            if config.convert_config:
                                processing_details.append(_("格式转换"))
                            if config.resize_config:
                                processing_details.append(_("调整大小"))
                            if config.watermark_config:
                                processing_details.append(_("添加水印"))
                            
                            # 创建处理记录
                            history_record = {
                                'id': str(uuid.uuid4()),
                                'timestamp': datetime.datetime.now().isoformat(),
                                'operation': _('批量处理'),
                                'file_count': len(file_paths),
                                'status': _('成功'),
                                'details': ', '.join(processing_details) if processing_details else _('基本处理'),
                                'original_size': f"{total_original_size / 1024 / 1024:.2f} MB",
                                'processed_size': f"{total_processed_size / 1024 / 1024:.2f} MB",
                                'savings': f"{size_reduction:.1f}%"
                            }
                            
                            # 保存到会话状态
                            if 'processing_history' not in st.session_state:
                                st.session_state.processing_history = []
                            st.session_state.processing_history.append(history_record)
                            
                            # 显示结果预览
                            if r_paths:
                                app_state.result_file_paths = [Path(p) for p in r_paths]
                                
                                # 使用信息卡片显示处理完成
                                ui.create_info_card(
                                    _("处理完成"),
                                    _("所有图片已处理完成，您可以查看处理结果或下载文件。"),
                                    "✅"
                                )
                                
                                # 显示处理结果网格
                                st.subheader(_("📸 处理结果"))
                                display_results_grid(r_paths, _)
                                
                                # 打包下载功能
                                st.subheader(_("📦 下载处理结果"))
                                zip_buffer = pack_files_to_zip(app_state.result_file_paths)
                                if zip_buffer:
                                    st.download_button(
                                        label=_("📥 下载所有处理后的图片"),
                                        data=zip_buffer,
                                        file_name="processed_images.zip",
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                except Exception as e: 
                    st.error(_("处理中发生严重错误: {}").format(e), icon="❗")
                    
                    # 改进的错误处理和用户提示
                    error_details = []
                    error_msg = str(e).lower()
                    
                    if "memory" in error_msg or "memoria" in error_msg:
                        error_details.append(_("• 内存不足：尝试减少同时处理的图片数量或降低图片分辨率"))
                    if "disk" in error_msg or "space" in error_msg or "espacio" in error_msg:
                        error_details.append(_("• 磁盘空间不足：请清理临时文件并确保有足够的可用空间"))
                    if "permission" in error_msg or "permis" in error_msg:
                        error_details.append(_("• 文件权限问题：请检查应用是否有正确的文件访问权限"))
                    if "timeout" in error_msg or "tiempo" in error_msg:
                        error_details.append(_("• 处理超时：尝试减少图片数量或简化处理参数"))
                    if "corrupt" in error_msg or "corromp" in error_msg:
                        error_details.append(_("• 文件损坏：检查是否有损坏的图片文件，尝试重新上传"))
                    
                    # 通用解决方案
                    if not error_details:
                        error_details.extend([
                            _("• 尝试刷新页面并重新上传图片"),
                            _("• 检查图片格式是否支持"),
                            _("• 减少同时处理的图片数量")
                        ])
                    
                    # 显示详细的错误信息和解决方案
                    with st.expander(_("🔍 错误详情与解决方案"), expanded=True):
                        st.markdown(_("## 可能的原因："))
                        for detail in error_details:
                            st.markdown(detail)
                        
                        st.markdown("\n" + _("## 技术错误详情："))
                        st.code(str(e))
                    
                    # 记录详细错误信息
                    logging.exception("处理过程中发生严重错误")

    with tabs[1]: # 信息查看
        def on_info_upload_change():
            # 清空信息查看相关的状态
            pass  # 信息查看是实时显示的，不需要持久化状态
        
        # 使用信息卡片作为标题
        ui.create_info_card(
            _("图片信息查看"),
            _("上传图片文件，查看详细的图片信息、EXIF数据和颜色统计。"),
            "🔍"
        )
        
        uploaded_info = st.file_uploader(_("上传图片以查看信息"), type=["jpg","png","bmp","webp"], key="info_upload", on_change=on_info_upload_change)
        if uploaded_info:
            p = save_uploaded_files([uploaded_info], TEMP_DIR)[0]; img=Image.open(p)
            
            # 图片预览和基本信息
            col1, col2 = st.columns([1, 2])
            with col1:
                # 使用上下文管理器安全显示图片，避免资源泄漏
                try:
                    st.image(img, use_column_width=True)
                finally:
                    # 关闭文件句柄
                    pass  # img对象由PIL管理，不需要手动关闭
            with col2:
                # 基础信息显示
                st.markdown(f"### {_("基础信息")}")
                
                # 文件信息
                file_size = os.path.getsize(p) / 1024
                file_size_text = f"{file_size:.2f} KB" if file_size < 1024 else f"{file_size/1024:.2f} MB"
                
                # 使用统计卡片显示关键信息
                col_size, col_dim, col_format = st.columns(3)
                with col_size:
                    ui.create_stat_card(_("文件大小"), file_size_text.split()[0], file_size_text.split()[1])
                with col_dim:
                    ui.create_stat_card(_("图片尺寸"), f"{img.width}×{img.height}", _("像素"))
                with col_format:
                    ui.create_stat_card(_("图片格式"), img.format or "未知", "")
                
                # 详细信息列表
                info_data = [
                    (_("文件名称"), uploaded_info.name),
                    (_("色彩模式"), img.mode),
                    (_("位深度"), str(len(img.getbands()) * 8) if img.mode != 'P' else '8（索引色）')
                ]
                
                for label, value in info_data:
                    st.markdown(f"**{label}**: {value}")
            
            # EXIF信息显示
            st.markdown(f"### {_("EXIF信息")}")
            try:
                exif_data = None
                # 尝试多种方式获取EXIF数据
                if hasattr(img, '_getexif'):
                    exif_data = img._getexif()
                elif hasattr(img, 'info') and 'exif' in img.info:
                    # 对于某些格式，EXIF可能在info字典中
                    exif_data = img.info['exif']
                
                if exif_data:
                    # 格式化EXIF数据
                    if isinstance(exif_data, bytes):
                        # 如果是二进制数据，尝试解析
                        import piexif
                        try:
                            exif_dict = piexif.load(exif_data)
                            exif_info = {}
                            for ifd_name in exif_dict:
                                if ifd_name == "thumbnail":
                                    exif_info["缩略图大小"] = f"{len(exif_dict[ifd_name])} 字节"
                                else:
                                    for tag, value in exif_dict[ifd_name].items():
                                        tag_name = piexif.TAGS[ifd_name].get(tag, {}).get('name', str(tag))
                                        # 转换字节数据为可读形式
                                        if isinstance(value, bytes):
                                            try:
                                                value = value.decode('utf-8')
                                            except:
                                                value = f"[二进制数据，长度: {len(value)}]"
                                        exif_info[tag_name] = value
                        except:
                            exif_info = {_("EXIF数据"): _("存在但无法解析详细内容")}
                    else:
                        exif_info = {EXIF_TAGS.get(k, k): v for k, v in exif_data.items() if k in EXIF_TAGS}
                    
                    # 提取关键EXIF信息直接显示
                    key_exif = {}
                    common_tags = [
                        _("设备制造商"), "Make",
                        _("设备型号"), "Model",
                        _("拍摄时间"), "DateTime",
                        _("曝光时间"), "ExposureTime",
                        _("光圈值"), "FNumber",
                        _("ISO"), "ISOSpeedRatings",
                        _("焦距"), "FocalLength"
                    ]
                    
                    for display_name, tag_name in zip(common_tags[::2], common_tags[1::2]):
                        for k, v in exif_info.items():
                            if tag_name.lower() in str(k).lower():
                                # 格式化常见值
                                if tag_name == "ExposureTime" and isinstance(v, tuple):
                                    value = f"1/{int(v[1]/v[0])}" if v[0] != 0 and v[1] != 0 else f"{v[0]}/{v[1]}"
                                elif tag_name == "FNumber" and isinstance(v, tuple):
                                    value = v[0]/v[1]
                                elif tag_name == "FocalLength" and isinstance(v, tuple):
                                    value = f"{v[0]/v[1]:.1f}mm"
                                else:
                                    value = v
                                
                                key_exif[display_name] = str(value)
                                break
                    
                    if key_exif:
                        st.markdown("**" + _("关键拍摄信息") + "**")
                        col1, col2 = st.columns(2)
                        for i, (k, v) in enumerate(key_exif.items()):
                            col = col1 if i % 2 == 0 else col2
                            col.text(f"{k}: {v}")
                    
                    # 折叠显示完整EXIF
                    with st.expander(_("查看完整EXIF详情")):
                        if len(exif_info) > 0:
                            for k, v in sorted(exif_info.items()):
                                # 避免显示过大的值
                                v_str = str(v)
                                if len(v_str) > 150: v_str = v_str[:150] + "..."
                                st.text(f"{k}: {v_str}")
                        else:
                            st.info(_("未能提取出可解析的EXIF标签"))
                else: 
                    st.info(_("该图片不包含EXIF信息"))
            except Exception as e: 
                st.error(f"{_("读取EXIF信息时出错")}: {e}")
                
                with st.expander(_("错误详情"), expanded=False):
                    st.code(str(e))
                
                st.info(_("提示：某些图片格式或被处理过的图片可能没有EXIF信息"))
            
            # 新增：颜色统计信息
            st.markdown(f"### {_("颜色统计")}")
            try:
                # 转换图像为RGB模式以进行颜色分析
                rgb_img = img.convert("RGB")
                
                # 获取颜色直方图（简化版，避免占用过多内存）
                width, height = img.size
                if width * height > 1000000:  # 对于大图片，进行采样
                    sample_size = 1000000
                    step = max(1, int((width * height) / sample_size))
                    pixels = list(rgb_img.getdata()[::step])
                else:
                    pixels = list(rgb_img.getdata())
                
                # 计算平均颜色
                total_r, total_g, total_b = 0, 0, 0
                for r, g, b in pixels:
                    total_r += r
                    total_g += g
                    total_b += b
                avg_r = total_r // len(pixels)
                avg_g = total_g // len(pixels)
                avg_b = total_b // len(pixels)
                
                # 显示平均颜色
                avg_color_hex = f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
                st.markdown(f"**{_("平均颜色")}**: {avg_color_hex}")
                st.markdown(
                    f'<div style="width: 100px; height: 30px; background-color: {avg_color_hex}; border: 1px solid #ddd;"></div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.info(_("颜色统计功能暂不可用或不支持该图片格式"))
    
    with tabs[2]: # 图片去重
        # 使用信息卡片作为标题
        ui.create_info_card(
            _("图片去重检测"),
            _("上传多张图片，系统将自动检测相似或重复的图片。支持JPG、PNG、BMP、WebP格式。"),
            "🔍"
        )
        
        def on_dedup_upload_change():
            app_state.duplicate_groups.clear()
            app_state.run_dedup = False
        
        uploaded_dedup = st.file_uploader(
            _("上传待检测图片"), 
            type=["jpg","png","bmp","webp"], 
            accept_multiple_files=True, 
            key="dedup_upload", 
            on_change=on_dedup_upload_change
        )
        
        # 显示已上传图片数量
        if uploaded_dedup:
            # 使用统计卡片显示上传信息
            col1, col2 = st.columns(2)
            with col1:
                ui.create_stat_card(_("已上传图片"), str(len(uploaded_dedup)), _("张"))
            with col2:
                total_size = sum(f.size for f in uploaded_dedup) / 1024 / 1024
                ui.create_stat_card(_("总大小"), f"{total_size:.1f}", _("MB"))
            
            # 可选：显示图片列表
            if st.checkbox(_("显示上传的图片列表")):
                for f in uploaded_dedup:
                    st.text(f.name)
        
        # 增强的相似度设置
        st.markdown("**" + _("检测设置") + "**")
        col1, col2 = st.columns(2)
        
        # 修改选项格式，使用更简单的结构
        similarity_levels = [
            {"value": 0.80, "label": _("宽松 (80%)")},
            {"value": 0.85, "label": _("较宽松 (85%)")},
            {"value": 0.90, "label": _("标准 (90%)")},
            {"value": 0.95, "label": _("严格 (95%)")},
            {"value": 0.99, "label": _("非常严格 (99%)")}
        ]
        
        # 使用更简单的滑块设置
        similarity_threshold = col1.slider(
            _("相似度阈值"),
            min_value=0.80,
            max_value=0.99,
            value=0.90,
            step=0.01,
            format="%.2f"
        )
        
        # 根据阈值显示对应级别标签
        selected_label = next((level["label"] for level in similarity_levels if abs(level["value"] - similarity_threshold) < 0.01), _("自定义"))
        col1.text(f"当前级别: {selected_label}")
        
        # 新增：检测模式选择
        detection_mode = col2.selectbox(
            _("检测模式"),
            [
                _("仅检测完全重复"),
                _("检测相似图片"),
                _("检测相似且相似裁剪")
            ]
        )
        
        # 显示当前阈值
        st.info(f"{_("当前相似度阈值")}: {similarity_threshold:.2%}")
        
        if st.button(_("开始检测"), type="primary", disabled=not uploaded_dedup or len(uploaded_dedup) < 2):
            app_state.run_dedup = True
            
        if app_state.run_dedup and uploaded_dedup:
            with st.spinner(_("正在检测重复图片...")):
                file_paths = save_uploaded_files(uploaded_dedup, TEMP_DIR)
                
                try:
                    # 根据检测模式调整相似度阈值
                    adjusted_threshold = similarity_threshold
                    if detection_mode == _("仅检测完全重复"):
                        adjusted_threshold = 0.99  # 非常高的相似度要求
                    elif detection_mode == _("检测相似且相似裁剪"):
                        adjusted_threshold = similarity_threshold * 0.9  # 稍微降低阈值以捕捉裁剪图片
                    
                    # 将浮点数相似度阈值转换为汉明距离
                    # 64位哈希，1.0表示完全相同，0.9表示最多6-7位不同
                    hash_length = 64
                    max_distance = int(hash_length * (1.0 - adjusted_threshold))
                    logger.info(f"转换相似度 {adjusted_threshold} 为汉明距离 {max_distance}（检测模式：{detection_mode}）")
                    
                    # 调用重复图片检测函数
                    duplicate_groups = find_duplicate_images([str(p) for p in file_paths], threshold=max_distance)
                    app_state.duplicate_groups = duplicate_groups
                    
                    if not duplicate_groups:
                        ui.create_info_card(
                            _("检测完成"),
                            _("未发现重复或相似图片。尝试降低相似度阈值可能会发现更多相似图片。"),
                            "✅"
                        )
                    else:
                        ui.create_info_card(
                            _("发现重复图片"),
                            _("检测到{}组重复或相似图片，请查看下面的详细结果。").format(len(duplicate_groups)),
                            "⚠️"
                        )
                        
                        # 统计信息
                        total_duplicates = sum(len(group) for group in duplicate_groups)
                        saveable_space = sum(os.path.getsize(p) for group in duplicate_groups for i, p in enumerate(group) if i > 0) / 1024 / 1024
                        
                        # 使用统计卡片显示检测结果
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            ui.create_stat_card(_("总图片数"), str(len(file_paths)), "")
                        with col2:
                            ui.create_stat_card(_("重复组数"), str(len(duplicate_groups)), "")
                        with col3:
                            ui.create_stat_card(_("重复图片数"), str(total_duplicates), "")
                        with col4:
                            ui.create_stat_card(_("可节省空间"), f"{saveable_space:.1f}", _("MB"))
                        
                        # 记录去重历史
                        import datetime
                        history_record = {
                            'id': str(uuid.uuid4()),
                            'timestamp': datetime.datetime.now().isoformat(),
                            'operation': _('图片去重'),
                            'file_count': len(file_paths),
                            'status': _('发现重复') if duplicate_groups else _('未发现重复'),
                            'details': _('找到{}组重复图片').format(len(duplicate_groups)) if duplicate_groups else _('未发现重复图片'),
                            'duplicate_groups': len(duplicate_groups),
                            'duplicate_files': total_duplicates,
                            'saveable_space': f"{saveable_space:.2f} MB"
                        }
                        
                        # 保存到会话状态
                        if 'processing_history' not in st.session_state:
                            st.session_state.processing_history = []
                        st.session_state.processing_history.append(history_record)
                        
                        # 新增：全选功能
                        st.markdown(f"**{_("选择操作")}**")
                        col1, col2 = st.columns(2)
                        select_all_keep_first = col1.checkbox(_("每组保留第一张，选择其余"))
                        select_all_keep_largest = col2.checkbox(_("每组保留最大文件，选择其余"))
                        
                        # 存储用户选择的文件
                        if 'selected_duplicates' not in st.session_state:
                            st.session_state.selected_duplicates = []
                        else:
                            st.session_state.selected_duplicates = []
                        
                        for i, group in enumerate(duplicate_groups):
                            st.markdown(f"### {_("重复/相似组")} {i+1} - {len(group)} {_("张图片")}")
                            
                            # 为每组创建一个列表存储选择状态
                            group_selected = []
                            
                            # 计算组内图片的相似度评分（简化版）
                            group_info = []
                            for img_path in group:
                                img_size = os.path.getsize(img_path)
                                try:
                                    img = Image.open(img_path)
                                    width, height = img.size
                                except:
                                    width, height = 0, 0
                                group_info.append((img_path, img_size, width, height))
                            
                            # 按文件大小排序（用于"保留最大文件"功能）
                            group_info.sort(key=lambda x: x[1], reverse=True)
                            
                            # 显示图片网格
                            cols = st.columns(3)
                            for j, (img_path, img_size, width, height) in enumerate(group_info):
                                col = cols[j % 3]
                                with col:
                                    try:
                                        img = Image.open(img_path)
                                        st.image(img, use_column_width=True, caption=Path(img_path).name)
                                        
                                        # 显示文件信息
                                        size_text = f"{img_size/1024:.1f} KB"
                                        dim_text = f"{width}×{height}"
                                        st.text(f"{size_text} · {dim_text}")
                                        
                                        # 选择框
                                        is_selected = False
                                        if select_all_keep_first and j > 0:
                                            is_selected = True
                                        elif select_all_keep_largest:
                                            # 找到最大文件（第一个）
                                            max_size = group_info[0][1]
                                            if img_size < max_size:
                                                is_selected = True
                                        
                                        selected = st.checkbox(
                                            _("选择删除"),
                                            value=is_selected,
                                            key=f"duplicate_{i}_{j}"
                                        )
                                        
                                        if selected:
                                            group_selected.append(img_path)
                                            st.session_state.selected_duplicates.append(img_path)
                                    except Exception as e:
                                        st.error(f"{_("无法显示图片")}: {e}")
                            
                            # 显示组内选择统计
                            if group_selected:
                                st.info(f"{_("本组已选择")} {len(group_selected)} {_("张图片")}")
                            
                            st.markdown("---")
                        
                        # 批量操作按钮
                        if st.session_state.selected_duplicates:
                            st.markdown(f"**{_("批量操作")}**")
                            col1, col2 = st.columns(2)
                            
                            # 模拟删除操作
                            if col1.button(
                                _("🗑️ 模拟删除所选") + f" ({len(st.session_state.selected_duplicates)})",
                                type="primary"
                            ):
                                st.success(
                                    f"✅ {_("模拟删除成功")}！{_("将删除")} {len(st.session_state.selected_duplicates)} {_("张图片")}\n" +
                                    f"{_("实际应用中，这些图片将被从上传队列中移除。")}"
                                )
                                # 显示将要删除的文件列表
                                with st.expander(_("查看将删除的文件")):
                                    for f_path in st.session_state.selected_duplicates:
                                        st.text(Path(f_path).name)
                            
                            # 取消选择全部
                            if col2.button(_("取消全部选择")):
                                st.session_state.selected_duplicates = []
                                st.rerun()
                except Exception as e:
                    st.error(f"{_("检测过程中出错")}: {e}")
                    with st.expander(_("错误详情")):
                        st.code(str(e))
    
    with tabs[3]: # 处理记录
        import datetime  # 添加datetime导入，避免UnboundLocalError
        
        # 使用信息卡片作为标题
        ui.create_info_card(
            _("处理记录"),
            _("查看历史处理记录，包括批量处理和图片去重的详细信息。"),
            "📋"
        )
        
        # 初始化处理历史记录（如果不存在）
        if 'processing_history' not in st.session_state:
            st.session_state.processing_history = []
            ui.create_info_card(
                _("暂无记录"),
                _("完成图片处理或去重后，记录将显示在这里。"),
                "ℹ️"
            )
        
        # 显示历史记录列表
        if st.session_state.processing_history:
            # 显示统计信息
            total_records = len(st.session_state.processing_history)
            processing_count = sum(1 for r in st.session_state.processing_history if r['operation'] == _('批量处理'))
            dedup_count = sum(1 for r in st.session_state.processing_history if r['operation'] == _('图片去重'))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                ui.create_stat_card(_("总记录数"), str(total_records), "")
            with col2:
                ui.create_stat_card(_("处理记录"), str(processing_count), "")
            with col3:
                ui.create_stat_card(_("去重记录"), str(dedup_count), "")
            
            for record in reversed(st.session_state.processing_history):
                # 使用卡片样式显示每条记录
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #333;">{record['operation']}</h4>
                            <span style="color: #666; font-size: 0.9em;">{datetime.datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                                <div><strong>{_("状态")}:</strong> {record['status']}</div>
                                <div><strong>{_("文件数量")}:</strong> {record['file_count']}</div>
                                <div><strong>{_("详情")}:</strong> {record['details']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 添加操作按钮
                    col1, col2 = st.columns(2)
                    if col1.button(_("查看详情"), key=f"view_{record['id']}", use_container_width=True):
                        st.info(_("此功能正在开发中：显示详细的处理日志和参数。"))
                    if col2.button(_("重新应用"), key=f"reapply_{record['id']}", use_container_width=True):
                        st.info(_("此功能正在开发中：将相同的处理参数应用到新的文件。"))
                    
                    st.markdown("---")
        else:
            ui.create_info_card(
                _("暂无记录"),
                _("完成图片处理后，记录将显示在这里。"),
                "ℹ️"
            )
        
        # 清除历史记录按钮
        if st.session_state.processing_history:
            if st.button(_("清除所有历史记录"), type="secondary", use_container_width=True):
                if st.checkbox(_("确定要清除所有历史记录吗？此操作不可恢复。"), key="confirm_clear"):
                    st.session_state.processing_history = []
                    st.success(_("历史记录已清除"))
                    st.rerun()
    
    with tabs[4]: # 性能监控
        # 使用信息卡片作为标题
        ui.create_info_card(
            _("性能监控"),
            _("实时监控系统性能指标，包括内存使用、处理时间和系统资源。"),
            "📊"
        )
        
        # 性能监控控制面板
        st.subheader(_("性能监控控制"))
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(_("开始监控"), use_container_width=True):
                performance_monitor.start_monitoring()
                st.success(_("性能监控已启动"))
        
        with col2:
            if st.button(_("停止监控"), use_container_width=True):
                performance_monitor.stop_monitoring()
                st.success(_("性能监控已停止"))
        
        with col3:
            if st.button(_("重置数据"), use_container_width=True):
                performance_monitor.reset_data()
                st.success(_("监控数据已重置"))
        
        # 实时性能指标
        st.subheader(_("实时性能指标"))
        
        # 获取当前性能数据
        current_stats = performance_monitor.get_current_stats()
        
        if current_stats:
            # 显示关键指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ui.create_stat_card(
                    _("内存使用率"), 
                    f"{current_stats.get('memory_percent', 0):.1f}%", 
                    _("系统内存")
                )
            
            with col2:
                ui.create_stat_card(
                    _("CPU使用率"), 
                    f"{current_stats.get('cpu_percent', 0):.1f}%", 
                    _("系统CPU")
                )
            
            with col3:
                ui.create_stat_card(
                    _("磁盘使用率"), 
                    f"{current_stats.get('disk_percent', 0):.1f}%", 
                    _("临时目录")
                )
            
            with col4:
                ui.create_stat_card(
                    _("处理时间"), 
                    f"{current_stats.get('processing_time', 0):.2f}s", 
                    _("最近操作")
                )
            
            # 性能图表
            st.subheader(_("性能趋势"))
            
            # 获取历史数据
            history_data = performance_monitor.get_history()
            
            if history_data:
                # 创建图表数据
                timestamps = [h['timestamp'] for h in history_data]
                memory_data = [h['memory_percent'] for h in history_data]
                cpu_data = [h['cpu_percent'] for h in history_data]
                
                # 显示内存使用趋势
                st.line_chart(
                    data={
                        _("时间"): timestamps,
                        _("内存使用率%"): memory_data,
                        _("CPU使用率%"): cpu_data
                    },
                    x=_("时间")
                )
            
            # 性能阈值设置
            st.subheader(_("性能阈值设置"))
            
            col1, col2 = st.columns(2)
            
            with col1:
                memory_threshold = st.slider(
                    _("内存使用阈值 (%)："),
                    min_value=50,
                    max_value=95,
                    value=80,
                    help=_("当内存使用超过此阈值时发出警告")
                )
            
            with col2:
                cpu_threshold = st.slider(
                    _("CPU使用阈值 (%)："),
                    min_value=50,
                    max_value=95,
                    value=85,
                    help=_("当CPU使用超过此阈值时发出警告")
                )
            
            # 检查阈值
            if current_stats.get('memory_percent', 0) > memory_threshold:
                st.warning(_("⚠️ 内存使用率过高！建议优化内存使用或增加系统内存。"))
            
            if current_stats.get('cpu_percent', 0) > cpu_threshold:
                st.warning(_("⚠️ CPU使用率过高！建议优化处理逻辑或减少并发任务。"))
        else:
            st.info(_("性能监控未启动，请点击'开始监控'按钮启动性能监控。"))
        
        # 调试工具
        st.subheader(_("调试工具"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(_("内存快照"), use_container_width=True):
                snapshot = debug_helper.take_memory_snapshot()
                st.success(_("内存快照已创建"))
                with st.expander(_("查看内存快照")):
                    st.json(snapshot)
        
        with col2:
            if st.button(_("系统信息"), use_container_width=True):
                system_info = debug_helper.get_system_info()
                st.success(_("系统信息已获取"))
                with st.expander(_("查看系统信息")):
                    st.json(system_info)
        
        # 性能优化建议
        st.subheader(_("性能优化建议"))
        
        suggestions = performance_monitor.get_optimization_suggestions()
        
        if suggestions:
            for suggestion in suggestions:
                st.info(f"💡 {suggestion}")
        else:
            st.info(_("系统性能良好，暂无优化建议。"))

# --- 运行主应用并渲染页脚 ---
def run():
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    st.set_page_config(page_title="SnapForge", page_icon="🖼️", layout="wide")
    app_state = AppState.init()
    
    # 注册退出时的资源清理
    atexit.register(app_state.cleanup_resources)
    
    #【修复缺陷1】使用上下文管理器安全处理临时目录，杜绝资源泄露
    with tempfile.TemporaryDirectory(prefix="snapforge_") as temp_dir_str:
        TEMP_DIR = Path(temp_dir_str)
        # 注册临时目录以便在异常情况下也能清理
        app_state.register_temp_dir(TEMP_DIR)
        
        with st.sidebar:
            st.title("SnapForge")
            lang = st.selectbox("Language/语言", ["English", "中文"])
            _ = get_translator(lang)
            st.header(_("⚙️ 设置"))
            if st.button(_("清理会话状态"), use_container_width=True, type="secondary"):
                # 不再需要手动清理文件夹，但可以保留此按钮来重置会话状态
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.success(_("会话已重置！页面将刷新。")); st.rerun()

        ui = UIManager(_)
        ui.load_resources()

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        main_app(_, TEMP_DIR, app_state, ui)
        st.markdown('</div>', unsafe_allow_html=True)
        
        ui.display_footer()

if __name__ == "__main__":
    run()