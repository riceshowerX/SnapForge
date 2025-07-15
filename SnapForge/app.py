# app.py (Upgraded Version)

import streamlit as st
import zipfile
import io
import tempfile
import shutil
import os
from pathlib import Path
from PIL import Image
from dataclasses import dataclass, field
from typing import List

# -----------------------------------------------------------------------------
# 1. 后端逻辑导入 (Import Backend Logic)
# -----------------------------------------------------------------------------
# 从优化后的逻辑文件中导入，并使用新的枚举类型
try:
    from logic import (
        ImageProcessor, ProcessConfig, ResizeMode, FilterType,
        find_duplicate_images, get_exif_data, get_image_main_color,
        plot_image_histogram, ocr_image, remove_background,
        select_best_image_in_group
    )
except ImportError:
    st.error("错误：无法找到 'logic_optimized.py' 文件。请确保它与 'app.py' 在同一目录下。")
    st.stop()

# 假设的多语言翻译工具，如果不存在则使用默认实现
try:
    from utils_i18n import get_translator
except ImportError:
    st.warning("提示：未找到 'utils_i18n.py'，将使用默认语言（不翻译）。")
    def get_translator(lang: str):
        return lambda s: s

# -----------------------------------------------------------------------------
# 2. UI与状态管理封装 (UI & State Management Encapsulation)
# -----------------------------------------------------------------------------

@dataclass
class AppState:
    """集中管理所有会话状态的键，避免使用魔法字符串，增强代码可维护性"""
    temp_dir: str = field(default_factory=lambda: tempfile.mkdtemp(prefix="snapforge_"))
    result_file_paths: List[Path] = field(default_factory=list)
    duplicate_groups: List[List[str]] = field(default_factory=list)
    ocr_files: List[Path] = field(default_factory=list)
    bg_removed_files: List[Path] = field(default_factory=list)
    run_dedup: bool = False
    log_messages: List[str] = field(default_factory=list)

    @classmethod
    def init(cls):
        """在Streamlit会话中初始化或获取状态对象"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = cls()
        return st.session_state.app_state

class UIManager:
    """封装所有UI渲染相关的CSS和HTML，使主应用逻辑更清爽"""
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
        margin: 0 auto 2rem auto; box-shadow: var(--card-shadow); max-width: 820px; border: 1px solid #eef2f6;
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

    def __init__(self, translator):
        self._ = translator

    def load_resources(self):
        st.markdown(self.CUSTOM_CSS, unsafe_allow_html=True)
        header_html = self.HEADER_HTML_TEMPLATE.format(
            subtitle=self._("高效、专业、美观的批量图片处理平台"),
            github_tooltip=self._('前往GitHub仓库'),
            feedback_tooltip=self._('反馈建议/提Issue'),
            feedback_link_text=self._("反馈建议")
        )
        st.markdown(header_html, unsafe_allow_html=True)

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
    """将上传的文件保存到临时目录并返回路径列表"""
    file_paths = []
    if not uploaded_files: return []
    for f in uploaded_files:
        f.seek(0)
        safe_filename = "".join(c for c in Path(f.name).name if c.isalnum() or c in "._-").strip()
        if not safe_filename: safe_filename = f"file_{hash(f.name)}.tmp"
        
        temp_path = output_dir / safe_filename
        with open(temp_path, "wb") as out:
            out.write(f.getvalue())
        file_paths.append(temp_path)
    return file_paths

def pack_files_to_zip(file_paths: List[Path]) -> io.BytesIO:
    """将文件路径列表打包成ZIP内存对象"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if file_path.exists():
                zipf.write(file_path, arcname=file_path.name)
    zip_buffer.seek(0)
    return zip_buffer

def display_results_grid(image_paths: List[Path], num_columns: int = 4):
    """以网格形式展示图片结果"""
    if not image_paths: return
    st.markdown("---")
    st.subheader(_("结果预览"))
    for i in range(0, len(image_paths), num_columns):
        cols = st.columns(num_columns)
        for j, col in enumerate(cols):
            if i + j < len(image_paths):
                path = image_paths[i + j]
                if path.exists():
                    col.image(str(path), caption=path.name, use_container_width=True)
                else:
                    col.warning(f"{path.name}\n{_('文件不存在')}")

def render_processing_options() -> ProcessConfig:
    """渲染批量处理的所有配置选项并返回ProcessConfig对象"""
    st.markdown(f'<h3 style="margin-top: 2rem;">{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        enable_rename = st.checkbox(_("启用重命名"), value=True)
        c1, c2 = st.columns(2)
        prefix = c1.text_input(_("文件名前缀"), "image", disabled=not enable_rename)
        start_num = c2.number_input(_("起始编号"), min_value=1, value=1, disabled=not enable_rename)
        naming_template = st.text_input(_("高级命名模板"), value="{prefix}_{counter:04d}", help=_("可用占位符: {prefix}, {counter}, {original_filename}, {width}, {height}"), disabled=not enable_rename)
        
        c1, c2 = st.columns(2)
        enable_convert = c1.checkbox(_("启用格式转换"))
        target_ext = c1.selectbox(_("目标格式"), [".png", ".jpg", ".webp", ".bmp", ".tiff"], index=0, disabled=not enable_convert)
        enable_compress = c2.checkbox(_("启用质量压缩"), value=True)
        quality = c2.slider(_("压缩质量"), 1, 100, 85, disabled=not enable_compress, help=_("对JPG/WEBP生效，PNG会转换为压缩等级。"))

    with st.expander(_("尺寸、水印与高级调整"), expanded=False):
        enable_resize = st.checkbox(_("启用尺寸调整"))
        c1, c2 = st.columns(2)
        resize_width = c1.number_input(_("目标宽度(px)"), 1, 8000, 800, disabled=not enable_resize)
        resize_height = c2.number_input(_("目标高度(px)"), 1, 8000, 600, disabled=not enable_resize)
        
        resize_mode_options = {
            _("保持比例适应边界 (Contain)"): ResizeMode.CONTAIN, 
            _("保持比例裁剪填充 (Cover)"): ResizeMode.COVER, 
            _("拉伸至指定尺寸 (Stretch)"): ResizeMode.STRETCH,
        }
        resize_mode_display = st.selectbox(_("缩放模式"), options=list(resize_mode_options.keys()), disabled=not enable_resize)
        
        resize_only_shrink = st.checkbox(_("仅缩小不放大"), value=True, disabled=not enable_resize)
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        preserve_metadata = c1.checkbox(_("保留元数据 (EXIF)"), value=True)
        num_cpus = os.cpu_count() or 1
        num_processes = c2.number_input(_("并行处理核心数"), min_value=1, max_value=num_cpus, value=max(1, num_cpus - 1))

        enable_watermark = st.checkbox(_("启用批量水印"))
        watermark = None
        if enable_watermark:
            c1, c2, c3 = st.columns(3)
            wm_text = c1.text_input(_("水印内容"), "SnapForge")
            wm_pos = c2.selectbox(_("水印位置"), ["bottom-right","bottom-left","top-right","top-left","center"])
            wm_size = c3.slider(_("水印字号"), 10, 200, 36)
            watermark = {"text": wm_text, "size": wm_size, "pos": wm_pos, "color": (255, 255, 255, 128)}

        enable_crop = st.checkbox(_("启用批量裁剪"), help=_("从左上角(x,y)开始裁剪一个(w,h)大小的区域"))
        crop_params = None
        if enable_crop:
            c1, c2, c3, c4 = st.columns(4)
            crop_x, crop_y = c1.number_input("X", 0), c2.number_input("Y", 0)
            crop_w, crop_h = c3.number_input(_("宽 W"), 0), c4.number_input(_("高 H"), 0)
            crop_params = {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}
        
        c1, c2 = st.columns(2)
        rotate = c1.number_input(_("批量旋转角度"), -360, 360, 0, 1)
        
        filter_options = {f.value: f for f in FilterType}
        filter_display = c2.selectbox(_("批量滤镜"), [""] + list(filter_options.keys()))

    return ProcessConfig(
        rename_enabled=enable_rename, prefix=prefix, start_number=start_num, naming_template=naming_template,
        convert_format=target_ext if enable_convert else None, quality=quality if enable_compress else None,
        resize_enabled=enable_resize, resize_width=resize_width, resize_height=resize_height,
        resize_mode=resize_mode_options[resize_mode_display], resize_only_shrink=resize_only_shrink,
        preserve_metadata=preserve_metadata, num_processes=num_processes,
        watermark_params=watermark, crop_params=crop_params, rotate_angle=rotate,
        filter_type=filter_options.get(filter_display)
    )

# -----------------------------------------------------------------------------
# 4. 主应用渲染 (Main Application Rendering)
# -----------------------------------------------------------------------------

# --- 初始化 ---
st.set_page_config(page_title="SnapForge", page_icon="🖼️", layout="wide")
app_state = AppState.init()
TEMP_DIR = Path(app_state.temp_dir)

# --- 侧边栏与国际化 ---
with st.sidebar:
    st.title("SnapForge")
    selected_lang = st.selectbox("Language / 语言", ["English", "中文"])
    _ = get_translator(selected_lang)
    st.header(_("⚙️ 设置"))
    if st.button(_("清理缓存和重置状态"), use_container_width=True, type="secondary"):
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
        st.session_state.app_state = AppState() # 完全重置状态
        st.success(_("缓存已清理！页面将刷新。"))
        st.rerun()

# --- 加载UI资源 ---
ui = UIManager(_)
ui.load_resources()

# --- 主应用内容 ---
def main_app():
    tab_titles = [_("批量处理"), _("信息查看"), _("图片去重"), _("智能工具"), _("处理记录")]
    tabs = st.tabs(tab_titles)

    # --- Tab 0: 批量处理 ---
    with tabs[0]:
        processor = ImageProcessor()
        st.markdown(f'<h3>{_("📂 上传文件")}</h3>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            _("上传图片文件（可混合格式）"), type=["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"], 
            accept_multiple_files=True, key="batch_upload"
        )
        config = render_processing_options()
        
        if st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not uploaded_files):
            app_state.result_file_paths.clear()
            app_state.log_messages = [_("任务开始...")]
            st.markdown('<div class="res-card">', unsafe_allow_html=True)
            log_area, progress_bar, result_area, download_area = st.empty(), st.empty(), st.empty(), st.empty()
            
            def streamlit_progress_callback(pct, filename=""):
                msg = f"{_('正在处理')}: {Path(filename).name}" if filename else _("处理中...")
                progress_bar.progress(pct, msg)

            try:
                file_paths = save_uploaded_files(uploaded_files, TEMP_DIR)
                with st.spinner(_("图片并行处理中，请稍候...")):
                    result_area.info(_("正在使用 {} 核心加速处理...").format(config.num_processes), icon="⏳")
                    processed, total, result_paths = processor.batch_process(
                        files=[str(p) for p in file_paths], output_dir=str(TEMP_DIR), config=config, 
                        progress_callback=streamlit_progress_callback
                    )
                    progress_bar.progress(1.0, _("处理完成！"))
                    
                    app_state.log_messages.append(_("任务报告："))
                    app_state.log_messages.append(f"  - {_('总文件数')}: {total}")
                    app_state.log_messages.append(f"  - {_('成功处理')}: {processed}")
                    app_state.log_messages.append(f"  - {_('失败或跳过')}: {total - processed}")
                    log_area.text_area(_("处理日志"), "\n".join(app_state.log_messages), height=200)
                    
                    if processed == 0 and total > 0: result_area.error(_("❌ 未成功处理任何图片，请检查日志。"))
                    else: result_area.success(_("✅ 处理完成：{} / {}").format(processed, total))
                    
                    if result_paths:
                        app_state.result_file_paths = [Path(p) for p in result_paths]
                        zip_buffer = pack_files_to_zip(app_state.result_file_paths)
                        download_area.download_button(_("⬇️ 下载全部结果"), zip_buffer, "processed_images.zip", "application/zip", use_container_width=True)
            except Exception as e:
                st.error(_("处理中发生严重错误: {}").format(e), icon="❗")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 1: 信息查看 ---
    with tabs[1]:
        st.markdown(f'<h3>{_("🖼️ 图片信息查看")}</h3>', unsafe_allow_html=True)
        uploaded_info = st.file_uploader(_("上传图片以查看详细信息"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], key="info_upload")
        if uploaded_info:
            temp_path_info = save_uploaded_files([uploaded_info], TEMP_DIR)[0]
            try:
                img = Image.open(temp_path_info)
                st.image(img, caption=_("图片预览"), use_container_width=True)
                c1, c2 = st.columns(2)
                c1.info(f"**{_('尺寸')}:** {img.width} x {img.height} px")
                c2.info(f"**{_('文件大小')}:** {temp_path_info.stat().st_size / 1024:.2f} KB")
                with st.expander(_("🎨 色彩与格式信息")):
                    st.write(f"**{_('模式')}:** {img.mode} | **{_('格式')}:** {img.format}")
                    dom_color, _palette = get_image_main_color(str(temp_path_info))
                    if dom_color:
                        st.write(f"**{_('主色调')}:**")
                        st.markdown(f'<div style="width:100%;height:30px;background:rgb{dom_color};border-radius:4px;border:1px solid #ccc"></div>', unsafe_allow_html=True)
                    buf = plot_image_histogram(str(temp_path_info))
                    if buf: st.image(buf, caption=_("RGB直方图"))
                exif_data = get_exif_data(str(temp_path_info))
                if exif_data:
                    with st.expander(_("📷 EXIF 元数据")): st.json(exif_data, expanded=False)
            except Exception as e: st.error(_("分析图片时出错: {}").format(e))

    # --- Tab 2: 图片去重 ---
    with tabs[2]:
        st.markdown(f'<h3>{_("👯‍♀️ 交互式图片去重")}</h3>', unsafe_allow_html=True)
        files_dedup = st.file_uploader(_("上传需要去重的图片(至少2张)"), type=["jpg","jpeg","png","bmp"], accept_multiple_files=True, key="dedup_upload")
        
        if st.button(_("查找重复图片"), use_container_width=True, disabled=len(files_dedup)<2, type="primary"):
            app_state.run_dedup = True
            file_paths_dedup = save_uploaded_files(files_dedup, TEMP_DIR)
            with st.spinner(_("正在查找重复图片...")):
                app_state.duplicate_groups = find_duplicate_images([str(p) for p in file_paths_dedup], 8)
        
        if app_state.run_dedup:
            if app_state.duplicate_groups:
                st.warning(_("检测到 {} 组重复图片：请检查下面的选择，然后下载您需要的结果。").format(len(app_state.duplicate_groups)))
                with st.form(key="dedup_form"):
                    kept_files_paths, to_delete_files_paths = [], []
                    for i, group in enumerate(app_state.duplicate_groups):
                        best_path_str = select_best_image_in_group(group)
                        def format_label(path_str):
                            try:
                                p = Path(path_str)
                                with Image.open(p) as img:
                                    return f"{p.name} ({img.width}x{img.height}, {p.stat().st_size//1024} KB)"
                            except Exception: return f"{Path(path_str).name} ({_('无法读取')})"
                        
                        kept_path = st.radio(
                            f"**{_('第')} {i+1}{_('组')} - {_('选择要保留的图片')}**",
                            options=group, format_func=format_label,
                            index=group.index(best_path_str) if best_path_str in group else 0, key=f"dedup_group_{i}"
                        )
                        kept_files_paths.append(Path(kept_path))
                        to_delete_files_paths.extend([Path(p) for p in group if p != kept_path])
                    
                    if st.form_submit_button(_("准备下载包"), use_container_width=True):
                        c1, c2 = st.columns(2)
                        c1.download_button(_("⬇️ 下载保留的图片 ({})").format(len(kept_files_paths)), pack_files_to_zip(kept_files_paths), "kept_images.zip", "application/zip", use_container_width=True, type="primary")
                        c2.download_button(_("⬇️ 下载多余的副本 ({})").format(len(to_delete_files_paths)), pack_files_to_zip(to_delete_files_paths), "redundant_images.zip", "application/zip", use_container_width=True)
            else:
                st.success(_("✅ 经过扫描，未在您的上传中检测到重复图片。"))

    # --- Tab 3: 智能工具 ---
    with tabs[3]:
        st.markdown(f'<h3>{_("🔍 智能工具")}</h3>', unsafe_allow_html=True)
        with st.expander(_("🪄 智能去背景 (Smart Background Removal)"), expanded=True):
            files_bg = st.file_uploader(_("上传图片去除背景"), accept_multiple_files=True, key="bg_upload")
            if st.button(_("开始去背景"), disabled=not files_bg):
                input_paths = save_uploaded_files(files_bg, TEMP_DIR)
                result_paths = []
                bar = st.progress(0, text=_("准备中..."))
                for i, p in enumerate(input_paths):
                    bar.progress((i + 1) / len(input_paths), text=f"{_('正在处理')} {p.name}...")
                    try:
                        out_p = p.with_name(f"{p.stem}_nobg.png")
                        remove_background(str(p), output_path=str(out_p))
                        result_paths.append(out_p)
                    except Exception as e: st.error(f"{p.name} {_('去背景失败')}: {e}")
                app_state.bg_removed_files = result_paths
            if app_state.bg_removed_files:
                st.download_button(_("⬇️ 下载去背景结果"), pack_files_to_zip(app_state.bg_removed_files), "bg_removed.zip", "application/zip", use_container_width=True)
                display_results_grid(app_state.bg_removed_files)
        
        with st.expander(_("✍️ 批量OCR文字识别 (Batch OCR)")):
            files_ocr = st.file_uploader(_("上传图片进行OCR"), accept_multiple_files=True, key="ocr_upload")
            if st.button(_("开始OCR识别"), disabled=not files_ocr):
                app_state.ocr_files = save_uploaded_files(files_ocr, TEMP_DIR)
            if app_state.ocr_files:
                for p in app_state.ocr_files:
                    c1, c2 = st.columns([1,2])
                    c1.image(str(p), use_container_width=True)
                    c2.text_area(_("识别结果"), ocr_image(str(p)), height=150, key=f"ocr_{p.name}")
                
    # --- Tab 4: 处理记录 ---
    with tabs[4]:
        st.markdown(f'<h3>{_("🗂️ 最近处理结果预览")}</h3>', unsafe_allow_html=True)
        if app_state.result_file_paths:
            st.info(_("这里将展示“批量处理”选项卡最近一次成功运行的结果。"))
            display_results_grid(app_state.result_file_paths, num_columns=4)
        else:
            st.info(_("暂无最近处理结果。请先在“批量处理”中运行一次任务。"))

# --- 运行主应用并渲染页脚 ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
main_app()
st.markdown('</div>', unsafe_allow_html=True)
ui.display_footer()