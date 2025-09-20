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
from pathlib import Path
from PIL import Image
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Set, Optional

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
except ImportError:
    st.error(
        "关键错误：无法找到 'logic.py' 文件。"
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
                path = image_paths[i + j]
                if path.exists():
                    col.image(str(path), caption=path.name, use_container_width=True)
                else:
                    col.warning(f"{path.name}\n{_('文件不存在')}")

def render_processing_options(_: Callable[[str], str]) -> ProcessConfig:
    """
    【修复缺陷3】渲染批量处理选项，并使用新的分层结构创建ProcessConfig。
    """
    st.markdown(f'<h3 style="margin-top: 2rem;">{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        enable_rename = st.checkbox(_("启用重命名"), value=True)
        c1, c2 = st.columns(2)
        prefix = c1.text_input(_("前缀"), "image", disabled=not enable_rename)
        start_num = c2.number_input(_("起始编号"), 1, 10000, 1, disabled=not enable_rename)
        naming_template = st.text_input(_("命名模板"), "{prefix}_{counter:04d}", disabled=not enable_rename)
        
        c1, c2 = st.columns(2)
        enable_convert = c1.checkbox(_("启用格式转换"))
        target_ext = c1.selectbox(_("目标格式"), [".png", ".jpg", ".webp"], disabled=not enable_convert)
        enable_compress = c2.checkbox(_("启用质量压缩"), True)
        quality = c2.slider(_("压缩质量"), 1, 100, 85, disabled=not enable_compress or not enable_convert)

    with st.expander(_("尺寸、水印与高级调整")):
        enable_resize = st.checkbox(_("启用尺寸调整"))
        c1, c2 = st.columns(2)
        w = c1.number_input(_("宽"), 1, 8000, 800, disabled=not enable_resize)
        h = c2.number_input(_("高"), 1, 8000, 600, disabled=not enable_resize)
        resize_map = {_("适应边界"): ResizeMode.CONTAIN, _("裁剪填充"): ResizeMode.COVER, _("拉伸"): ResizeMode.STRETCH}
        mode_disp = st.selectbox(_("模式"), list(resize_map.keys()), disabled=not enable_resize)
        only_shrink = st.checkbox(_("仅缩小"), True, disabled=not enable_resize)
        st.markdown("---")
        c1, c2 = st.columns(2)
        preserve_meta = c1.checkbox(_("保留EXIF"), True)
        cpus = os.cpu_count() or 1
        num_proc = c2.number_input(_("核心数"), 1, cpus, 2)
        
        enable_wm = st.checkbox(_("启用水印"))
        wm_cfg = None
        if enable_wm: 
            c1, c2, c3 = st.columns(3)
            wm_txt = c1.text_input(_("内容"), "SnapForge")
            wm_pos = c2.selectbox(_("位置"), ["bottom-right", "center"])
            wm_size = c3.slider(_("字号"), 10, 200, 36)
            wm_cfg = WatermarkConfig(wm_txt, size=wm_size, position=wm_pos)

        enable_crop = st.checkbox(_("启用裁剪"))
        crop_cfg = None
        if enable_crop: 
            c1, c2, c3, c4 = st.columns(4)
            x = c1.number_input("X", 0, 10000, 0)
            y = c2.number_input("Y", 0, 10000, 0)
            cw = c3.number_input(_("裁剪宽"), 1, 10000, 100)
            ch = c4.number_input(_("裁剪高"), 1, 10000, 100)
            crop_cfg = CropConfig(x, y, cw, ch)
        
        c1, c2 = st.columns(2)
        rot = c1.number_input(_("旋转角度"), -360, 360, 0, 1)
        flt_map = {"": None, **{f.value: f for f in FilterType}}
        flt_disp = c2.selectbox(_("滤镜"), list(flt_map.keys()))

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

def main_app(_: Callable[[str], str], TEMP_DIR: Path, app_state: AppState):
    tab_titles = [_("批量处理"), _("信息查看"), _("图片去重"), _("处理记录")]
    tabs = st.tabs(tab_titles)

    with tabs[0]: # 批量处理
        processor = ImageProcessor()
        st.markdown(f'<h3>{_("📂 上传文件")}</h3>', unsafe_allow_html=True)
        def on_batch_upload_change():
            app_state.result_file_paths.clear()
            app_state.log_messages.clear()
        
        uploaded_files = st.file_uploader(_("上传图片"), type=["jpg","png","bmp","webp"], accept_multiple_files=True, key="batch_upload", on_change=on_batch_upload_change)
        config = render_processing_options(_)
        if st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not uploaded_files):
            app_state.result_file_paths.clear(); app_state.log_messages=[_("任务开始...")]
            with st.container():
                log_area, progress_bar, result_area, dl_area = st.empty(), st.empty(), st.empty(), st.empty()
                def progress_cb(pct, filename=""): progress_bar.progress(pct, f"{_('正在处理')}: {Path(filename).name}" if filename else _("处理中..."))
                try:
                    file_paths = save_uploaded_files(uploaded_files, TEMP_DIR)
                    with st.spinner(_("图片并行处理中...")):
                        result_area.info(_("使用 {} 核心加速...").format(config.num_processes), icon="⏳")
                        p, t, r_paths = processor.batch_process([str(p) for p in file_paths], str(TEMP_DIR), config, progress_cb)
                        progress_bar.progress(1.0, _("处理完成！"))
                        if not r_paths: result_area.error(_("❌ 未成功处理任何图片。"))
                        else: result_area.success(_("✅ 处理完成：{} / {}").format(p, t))
                        if r_paths: app_state.result_file_paths = [Path(p) for p in r_paths]; dl_area.download_button(_("⬇️ 下载全部结果"), pack_files_to_zip(app_state.result_file_paths), "processed.zip", use_container_width=True)
                except Exception as e: 
                    st.error(_("处理中发生严重错误: {}").format(e), icon="❗")
                    # 提供更详细的错误信息和可能的解决方案
                    if "memory" in str(e).lower():
                        st.error(_("可能是内存不足。尝试减少处理的图片数量或降低图片分辨率。"))
                    elif "disk" in str(e).lower() or "space" in str(e).lower():
                        st.error(_("可能是磁盘空间不足。请清理磁盘空间后重试。"))
                    elif "permission" in str(e).lower():
                        st.error(_("可能是文件权限问题。请检查应用程序是否有足够的权限。"))
                    else:
                        st.error(_("请尝试重新上传图片或刷新页面。如果问题持续存在，请联系支持团队。"))
                    
                    # 记录详细错误信息
                    logging.exception("处理过程中发生严重错误")

    with tabs[1]: # 信息查看
        def on_info_upload_change():
            # 清空信息查看相关的状态
            pass  # 信息查看是实时显示的，不需要持久化状态
        
        uploaded_info = st.file_uploader(_("上传图片以查看信息"), type=["jpg","png","bmp"], key="info_upload", on_change=on_info_upload_change)
        if uploaded_info:
            p = save_uploaded_files([uploaded_info], TEMP_DIR)[0]; img=Image.open(p)
            st.image(img, use_container_width=True)
            c1,c2=st.columns(2); c1.info(f"**{_('尺寸')}:** {img.width}x{img.height}"); c2.info(f"**{_('大小')}:** {p.stat().st_size/1024:.1f}KB")
    
    with tabs[2]: # 图片去重
        st.markdown(f'<h3>{_("👯‍♀️ 图片去重")}</h3>', unsafe_allow_html=True)
        # 让阈值可配置
        threshold = st.slider(_("相似度阈值 (值越小越严格)"), 0, 20, 8)
        
        def on_dedup_change():
            app_state.run_dedup = False
            app_state.duplicate_groups.clear()
        
        files = st.file_uploader(_("上传需要去重的图片(至少2张)"), type=["jpg","png","bmp"], accept_multiple_files=True, key="dedup_upload", on_change=on_dedup_change)
        if st.button(_("查找重复图片"), use_container_width=True, disabled=len(files)<2):
            app_state.run_dedup = True
            file_paths = save_uploaded_files(files, TEMP_DIR)
            with st.spinner(_("正在查找...")):
                app_state.duplicate_groups = find_duplicate_images([str(p) for p in file_paths], threshold)
        if app_state.run_dedup:
            if not app_state.duplicate_groups:
                st.success(_("✅ 未检测到重复图片。"))
            else:
                st.warning(_("检测到 {} 组重复图片。").format(len(app_state.duplicate_groups)))
                # 显示重复图片组
                for i, group in enumerate(app_state.duplicate_groups):
                    st.write(f"第{i+1}组重复图片 ({len(group)}张):")
                    cols = st.columns(min(4, len(group)))
                    for j, img_path in enumerate(group):
                        if j < len(cols):
                            cols[j].image(img_path, use_container_width=True)
    
    with tabs[3]: # 处理记录
        if app_state.result_file_paths: display_results_grid(app_state.result_file_paths, _, num_columns=4)
        else: st.info(_("暂无最近处理结果。"))

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
        main_app(_, TEMP_DIR, app_state)
        st.markdown('</div>', unsafe_allow_html=True)
        
        ui.display_footer()

if __name__ == "__main__":
    run()