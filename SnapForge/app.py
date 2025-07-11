# app.py
import os
import streamlit as st
import zipfile
import io
import tempfile
import shutil
# 修正点：在这里加入了所有需要的函数，特别是 select_best_image_in_group
from logic import (
    ImageProcessor, ProcessLog, find_duplicate_images,
    get_exif_data, get_image_main_color,
    plot_image_histogram, ocr_image, smart_classify, remove_background,
    select_best_image_in_group, ProcessConfig
)
from PIL import Image
from utils_i18n import get_translator

# ---------- 全局会话临时目录管理 ----------
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
TEMP_DIR = st.session_state.temp_dir

# ---------- 全局UI美化 ----------
custom_css = """
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
.stButton>button[kind="secondary"] { border-color: #F63366; color: #F63366; }
.stButton>button[kind="secondary"]:hover { background-color: #F63366; color: #fff; border-color: #F63366; }
.stButton>button[kind="primary"]:hover { filter: brightness(1.1); }
.stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div { border-radius: var(--border-radius-sm); background-color: #f8f9fa; }
.res-card { background: linear-gradient(100deg, #e9f2fe 0%, #e8fcff 100%); border-radius: var(--border-radius-lg); padding: 1.5rem; margin: 1.3rem 0; }
.footer { text-align: center; color: #99a1b3; padding: 1.5rem 0; }
.footer a { color: var(--primary-color); text-decoration: none; font-weight: 600; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------- 语言切换与设置 ----------
selected_lang = st.sidebar.selectbox("Language / 语言", ["English", "中文"])
_ = get_translator(selected_lang)
st.sidebar.title(_("⚙️ 设置"))

# ---------- 顶部Banner ----------
st.markdown(f"""
<div class="header-banner">
    <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 3H4C2.897 3 2 3.897 2 5v14c0 1.103.897 2 2 2h16c1.103 0 2-.897 2-1V5c0-1.103-.897-2-2-2zM4 19V5h16l.002 14H4z"></path>
      <path d="M10.293 14.293 8.464 12.464 6 15h12l-3.536-4.42-2.171 2.713z"></path>
      <path d="m19.207 2.207-1.414 1.414L19.207 5.035l1.414-1.414L22.035 2.207l-1.414-1.414zm-2.828 4.243L15 8.464l1.414 1.414 1.414-1.414L19.243 7.05l-1.414-1.414zM15 2.207l1.414-1.414L17.828 2.207l-1.414 1.414z"></path>
    </svg>
    <h1>SnapForge</h1>
    <div class="subtitle">{_("高效、专业、美观的批量图片处理平台")}</div>
</div>
<div class="header-actions">
    <a href="https://github.com/riceshowerX/SnapForge" target="_blank" title="{_('前往GitHub仓库')}">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="vertical-align: -2px; margin-right: 6px;">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
        </svg>
        GitHub
    </a>
    <a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" title="{_('反馈建议/提Issue')}">{_("反馈建议")}</a>
</div>
""", unsafe_allow_html=True)

# ---------- 主体 ----------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
tab_titles = [
    _("批量处理"), _("信息查看"), _("图片去重"),
    _("OCR分类"), _("智能去背景"), _("处理记录")
]
tabs = st.tabs(tab_titles)

# ---------- 通用函数 ----------
def save_uploaded_files(files, output_dir):
    file_paths = []
    for f in files:
        f.seek(0)
        file_name = os.path.basename(f.name)
        file_name = "".join(x for x in file_name if x.isalnum() or x in "._-")
        temp_path = os.path.join(output_dir, file_name)
        with open(temp_path, "wb") as out:
            out.write(f.read())
        file_paths.append(temp_path)
    return file_paths

def pack_files_to_zip(file_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            if os.path.exists(file):
                zipf.write(file, arcname=os.path.basename(file))
    zip_buffer.seek(0)
    return zip_buffer

# ---------- Tab 0: 批量处理 ----------
with tabs[0]:
    processor = ImageProcessor()
    st.markdown(f'<h3>{_("📂 上传与处理模式")}</h3>', unsafe_allow_html=True)
    upload_mode = st.radio(_("处理模式"), [_("批量处理（多文件上传）"), _("单文件处理")], horizontal=True, key="process_mode")
    files = []
    if upload_mode == _("批量处理（多文件上传）"):
        files = st.file_uploader(_("上传图片文件（可混合格式）"), type=["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"], accept_multiple_files=True, key="batch_upload")
        process_filter_mode = st.radio(
            _("文件筛选"),
            (_("处理所有上传的图片格式"), _("仅处理指定格式的图片")),
            index=0, horizontal=True, help=_("“处理所有”会对上传的各种格式图片进行处理；“仅处理指定”则只处理下拉框中选定的类型。")
        )
        extension_to_filter = None
        if process_filter_mode == _("仅处理指定格式的图片"):
            extension_to_filter = st.selectbox(_("选择要处理的格式"), [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"], index=0, key="filter_ext_select")
    else:
        one_file = st.file_uploader(_("上传一个图片文件"), type=["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"], accept_multiple_files=False, key="single_upload")
        if one_file:
            files = [one_file]
        extension_to_filter = None

    st.markdown(f'<h3 style="margin-top: 2rem;">{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        enable_rename = st.checkbox(_("启用重命名"), value=True)
        naming_template = st.text_input(_("高级命名模板"), value="{prefix}_{counter:04d}", help=_("可用占位符: {prefix}, {counter}, {original_filename}, {width}, {height}"), disabled=not enable_rename)
        prefix = st.text_input(_("文件名前缀"), "image", disabled=not enable_rename)
        start_num = st.number_input(_("起始编号"), min_value=1, value=1, disabled=not enable_rename)
        enable_convert = st.checkbox(_("启用格式转换"))
        target_ext = st.selectbox(_("目标格式"), [".jpg",".jpeg",".png",".bmp",".gif",".tiff",".webp"], index=2, disabled=not enable_convert)
        enable_compress = st.checkbox(_("启用质量压缩"))
        quality = st.slider(_("压缩质量 (1-100)"), 1, 100, 85, disabled=not enable_compress)
        st.caption(_("💡 JPEG/WEBP用质量，PNG为压缩等级"))

    with st.expander(_("尺寸调整与高级选项"), expanded=False):
        enable_resize = st.checkbox(_("启用尺寸调整"))
        resize_width = st.number_input(_("目标宽度(px)"), min_value=1, value=800, disabled=not enable_resize)
        resize_height = st.number_input(_("目标高度(px)"), min_value=1, value=600, disabled=not enable_resize)
        resize_mode_options = {
            _("等比缩放（fit）"): "fit", _("拉伸填充（fill）"): "fill",
            _("填充白边（pad）"): "pad", _("中心裁剪（crop）"): "crop"
        }
        resize_mode_display = st.selectbox(_("缩放模式"), options=list(resize_mode_options.keys()), disabled=not enable_resize)
        resize_mode = resize_mode_options[resize_mode_display]
        resize_only_shrink = st.checkbox(_("仅缩小不放大"), value=True, disabled=not enable_resize)
        preserve_metadata = st.checkbox(_("保留元数据 (EXIF)"), value=True)
        enable_watermark = st.checkbox(_("启用批量水印"))
        watermark = None
        if enable_watermark:
            wm_text = st.text_input(_("水印内容"), "SnapForge")
            wm_pos = st.selectbox(_("水印位置"), ["bottom-right","bottom-left","top-right","top-left","center"])
            wm_size = st.slider(_("水印字号"), 10, 120, 32)
            watermark = {"text": wm_text, "size": wm_size, "pos": wm_pos, "color": (255,255,255,128)}
        enable_crop = st.checkbox(_("启用批量裁剪"))
        crop_params = None
        if enable_crop:
            crop_x, crop_y = st.number_input(_("裁剪X"), 0), st.number_input(_("裁剪Y"), 0)
            crop_w, crop_h = st.number_input(_("裁剪宽"), 0), st.number_input(_("裁剪高"), 0)
            crop_params = {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}
        rotate = st.number_input(_("批量旋转角度"), -360, 360, 0)
        filter_type = st.selectbox(_("批量滤镜"), ["", "grayscale", "sharpen", "blur", "contour", "emboss", "edge", "enhance"])

    run_btn = st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not files)
    
    if run_btn:
        if "result_file_paths" in st.session_state: del st.session_state["result_file_paths"]
        st.session_state["result_file_paths"] = []
        st.markdown('<div class="res-card">', unsafe_allow_html=True)
        log_area, progress_bar, result_area, download_area = st.empty(), st.empty(), st.empty(), st.empty()
        
        def streamlit_progress_callback(pct, filename=None):
            msg = _("正在处理: {}").format(filename) if filename else _("处理中...")
            progress_bar.progress(pct, msg)

        if not files:
            result_area.warning(_("请先上传图片文件！"), icon="⚠️")
        else:
            try:
                config = ProcessConfig(
                    rename_enabled=enable_rename, prefix=prefix, start_number=start_num, naming_template=naming_template,
                    convert_format=target_ext if enable_convert else None,
                    quality=quality if enable_compress else None,
                    resize_enabled=enable_resize, resize_width=resize_width, resize_height=resize_height,
                    resize_mode=resize_mode, resize_only_shrink=resize_only_shrink,
                    preserve_metadata=preserve_metadata, watermark_params=watermark,
                    crop_params=crop_params, rotate_angle=rotate,
                    filter_type=filter_type if filter_type else None
                )
                
                file_paths = save_uploaded_files(files, TEMP_DIR)
                log = ProcessLog()
                
                files_to_process = file_paths
                if extension_to_filter:
                    normalized_filter = extension_to_filter.lower()
                    files_to_process = [f for f in file_paths if f.lower().endswith(normalized_filter)]
                
                with st.spinner(_("图片并行处理中，请稍候...")):
                    result_area.info(_("正在使用多核心加速处理..."), icon="⏳")
                    processed, total_input, result_paths = processor.batch_process(
                        files=files_to_process, config=config, process_log=log, progress_callback=streamlit_progress_callback
                    )
                    progress_bar.progress(1.0, _("处理完成！"))
                    log_area.text_area(_("处理日志"), log.get_text(), height=200)
                    
                    if processed == 0 and total_input > 0:
                        result_area.error(_("❌ 未成功处理任何图片，请检查日志。"))
                    elif processed < total_input:
                        result_area.warning(_("⚠️ 部分成功：处理了 {} / {} 张符合条件的图片。").format(processed, total_input))
                    else:
                        result_area.success(_("✅ 处理完成：{} / {}").format(processed, total_input))
                    
                    if result_paths:
                        zip_buffer = pack_files_to_zip(result_paths)
                        download_area.download_button(_("⬇️ 下载全部结果"), zip_buffer, "processed_images.zip", "application/zip", use_container_width=True)
                        st.session_state["result_file_paths"] = result_paths
            except Exception as e:
                st.error(_("处理中发生严重错误: {}").format(e), icon="❗")
                if 'log' in locals(): log_area.text_area(_("错误日志"), log.get_text(), height=200)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 1: 信息查看 ----------
with tabs[1]:
    st.markdown(f'<h3>{_("🖼️ 图片信息查看")}</h3>', unsafe_allow_html=True)
    uploaded_info = st.file_uploader(_("上传图片以查看详细信息"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], key="info_upload")
    if uploaded_info:
        try:
            img = Image.open(uploaded_info)
            st.image(img, caption=_("图片预览"), use_container_width=True)
            temp_path_info = os.path.join(TEMP_DIR, uploaded_info.name)
            uploaded_info.seek(0)
            with open(temp_path_info, "wb") as out: out.write(uploaded_info.read())
            c1, c2 = st.columns(2)
            c1.info(f"**{_('尺寸')}:** {img.size[0]} x {img.size[1]} px")
            c2.info(f"**{_('文件大小')}:** {uploaded_info.size // 1024} KB")
            with st.expander(_("🎨 色彩与格式信息")):
                st.write(f"**{_('模式')}:** {img.mode} | **{_('格式')}:** {img.format}")
                if img.info.get("dpi"): st.write(f"**DPI:** {img.info.get('dpi')}")
                if getattr(img, "is_animated", False): st.write(f"**{_('帧数')}:** {img.n_frames}")
                dom_color, palette = get_image_main_color(temp_path_info)
                if dom_color:
                    st.write(f"**{_('主色调')}:**")
                    st.markdown(f'<div style="width:100%;height:30px;background:rgb{dom_color};border-radius:4px;border:1px solid #ccc"></div>', unsafe_allow_html=True)
                buf = plot_image_histogram(temp_path_info)
                if buf: st.image(buf, caption=_("RGB直方图"))
            exif_data = get_exif_data(temp_path_info)
            if exif_data:
                with st.expander(_("📷 EXIF 元数据")):
                    st.json(exif_data, expanded=False)
        except Exception as e:
            st.error(_("分析图片时出错: {}").format(e))

# ---------- Tab 2: 图片去重 ----------
with tabs[2]:
    st.markdown(f'<h3>{_("👯‍♀️ 交互式图片去重")}</h3>', unsafe_allow_html=True)
    st.info(_("上传图片后，系统将自动预选要保留的最佳图片。您可以审查并修改选择，然后直接下载结果。"))
    files_dedup = st.file_uploader(_("上传需要去重的图片(至少2张)"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True, key="dedup_upload")
    run_dedup_btn = st.button(_("查找重复图片"), use_container_width=True, disabled=len(files_dedup)<2, type="primary")
    if run_dedup_btn:
        st.session_state.duplicate_groups = []
        file_paths_dedup = save_uploaded_files(files_dedup, TEMP_DIR)
        with st.spinner(_("正在查找重复图片...")):
            st.session_state.duplicate_groups = find_duplicate_images(file_paths_dedup, 8)
    
    if "duplicate_groups" in st.session_state and st.session_state.duplicate_groups:
        st.markdown("---")
        st.warning(_("检测到 {} 组重复图片：请检查下面的选择，然后下载您需要的结果。").format(len(st.session_state.duplicate_groups)))
        
        kept_files_paths = []
        to_delete_files_paths = []
        with st.form(key="dedup_form"):
            for i, group in enumerate(st.session_state.duplicate_groups):
                best_image_path = select_best_image_in_group(group)
                def format_label(path):
                    try:
                        with Image.open(path) as img:
                            return f"{os.path.basename(path)} ({img.width}x{img.height}, {os.path.getsize(path)//1024} KB)"
                    except Exception:
                        return f"{os.path.basename(path)} ({_('无法读取')})"
                kept_image_path = st.radio(
                    f"**{_('第')} {i+1}{_('组') if selected_lang == '中文' else ''} - {_('选择要保留的图片：')}**",
                    options=group, format_func=format_label,
                    index=group.index(best_image_path) if best_image_path in group else 0,
                    key=f"dedup_group_{i}"
                )
                kept_files_paths.append(kept_image_path)
                to_delete_files_paths.extend([p for p in group if p != kept_image_path])
            submitted = st.form_submit_button(_("准备下载包"), use_container_width=True)
        if submitted:
            st.markdown("---")
            st.markdown(f"<h4>{_('下载您的文件')}</h4>", unsafe_allow_html=True)
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                if kept_files_paths:
                    zip_buffer_kept = pack_files_to_zip(kept_files_paths)
                    st.download_button(label=_("⬇️ 下载保留的图片 ({})").format(len(kept_files_paths)), data=zip_buffer_kept, file_name="kept_images.zip", mime="application/zip", use_container_width=True, type="primary")
            with col_dl2:
                if to_delete_files_paths:
                    zip_buffer_deleted = pack_files_to_zip(to_delete_files_paths)
                    st.download_button(label=_("⬇️ 下载多余的副本 ({})").format(len(to_delete_files_paths)), data=zip_buffer_deleted, file_name="redundant_images.zip", mime="application/zip", use_container_width=True, type="secondary")
    elif run_dedup_btn:
        st.success(_("✅ 经过扫描，未在您的上传中检测到重复图片。"))

# ---------- Tab 3: OCR/智能分类 ----------
with tabs[3]:
    st.markdown(f'<h3>{_("🔍 OCR & 智能分类")}</h3>', unsafe_allow_html=True)
    st.info(_("此选项卡提供两种独立的智能工具。"))
    st.markdown(f"**1. {_('批量OCR文字识别')}**")
    files_ocr = st.file_uploader(_("上传图片进行OCR"), accept_multiple_files=True, key="ocr_upload")
    if st.button(_("开始OCR识别"), disabled=not files_ocr):
        file_paths_ocr = save_uploaded_files(files_ocr, TEMP_DIR)
        for idx, p in enumerate(file_paths_ocr):
            c1, c2 = st.columns([1,2])
            c1.image(p, use_container_width=True)
            text = ocr_image(p)
            c2.text_area(_("识别结果"), text, height=150, key=f"ocr_{idx}")
    st.markdown(f"<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"**2. {_('智能图片分类')}**")
    files_classify = st.file_uploader(_("上传图片进行分类"), accept_multiple_files=True, key="classify_upload")
    if st.button(_("开始智能分类"), disabled=not files_classify):
        file_paths_classify = save_uploaded_files(files_classify, TEMP_DIR)
        for p in file_paths_classify:
            st.image(p, width=120)
            st.write(f"{_('分类结果: ')}{', '.join(smart_classify(p))}")

# ---------- Tab 4: 智能去背景 ----------
with tabs[4]:
    st.markdown(f'<h3>{_("🪄 智能去背景")}</h3>', unsafe_allow_html=True)
    files_bg = st.file_uploader(_("上传图片去除背景(推荐PNG)"), accept_multiple_files=True, key="bg_upload")
    if st.button(_("开始去背景"), use_container_width=True, disabled=not files_bg):
        input_paths_bg = save_uploaded_files(files_bg, TEMP_DIR)
        result_paths_bg = []
        progress_bar_bg = st.progress(0)
        with st.spinner(_("正在去除背景...")):
            for i, in_path in enumerate(input_paths_bg):
                out_path = os.path.splitext(in_path)[0] + "_nobg.png"
                try:
                    remove_background(in_path, output_path=out_path)
                    result_paths_bg.append(out_path)
                except Exception as e:
                    st.error(f"{os.path.basename(in_path)} {_('去背景失败')}: {e}")
                progress_bar_bg.progress((i + 1) / len(input_paths_bg))
        if result_paths_bg:
            st.success(_("处理完成！"))
            cols = st.columns(3)
            for i, p in enumerate(result_paths_bg):
                cols[i % 3].image(p, caption=os.path.basename(p), use_container_width=True)
            zip_buffer_bg = pack_files_to_zip(result_paths_bg)
            st.download_button(_("⬇️ 下载全部结果"), zip_buffer_bg, "background_removed.zip", "application/zip", use_container_width=True)

# ---------- Tab 5: 处理记录/结果预览 ----------
with tabs[5]:
    st.markdown(f'<h3>{_("🗂️ 最近处理结果预览")}</h3>', unsafe_allow_html=True)
    rfp = st.session_state.get("result_file_paths", [])
    if rfp:
        st.info(_("这里将展示“批量处理”选项卡最近一次成功运行的结果。"))
        cols = st.columns(4)
        for i, p in enumerate(rfp[:12]):
            if os.path.exists(p):
                with cols[i % 4]:
                    st.image(p, caption=os.path.basename(p), use_container_width=True)
            else:
                with cols[i % 4]:
                    st.warning(f"{os.path.basename(p)} {_('不存在')}")
    else:
        st.info(_("暂无最近处理结果。请先在“批量处理”中运行一次任务。"))

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="footer">
    <span>© 2025 <b>SnapForge</b> | {_('由')} <a href="https://github.com/riceshowerX" target="_blank">riceshowerX</a> {_('设计与开发')}</span>
</div>
""", unsafe_allow_html=True)