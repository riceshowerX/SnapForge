import os
import streamlit as st
import zipfile
import io
from logic import (
    ImageProcessor, ProcessLog, find_duplicate_images,
    ai_image_recognition_cloud, get_exif_data, get_image_main_color,
    plot_image_histogram, ocr_image, smart_classify, remove_background
)
from PIL import Image
from utils_i18n import get_translator

# ----------- 全局升级美化 CSS -----------
def inject_css():
    st.markdown("""
    <style>
    body { background: linear-gradient(120deg, #f3f6fc 0%, #f7faff 100%); }
    .app-container { background: #fff; border-radius: 1.5rem; box-shadow: 0 6px 44px #406aff18;
        max-width: 1080px; margin: 0 auto 2.2rem auto; padding: 2.8rem 2.8rem 2.4rem 2.8rem;}
    .sf-sidebar-brand { text-align: center; padding: 30px 0 16px 0; margin-bottom: 1.1em;}
    .sf-sidebar-brand .logo { font-size: 2.9rem; line-height:1; color:#406aff;}
    .sf-sidebar-brand .title { font-size: 1.31rem; font-weight:900; color:#406aff; margin: 0.13em 0 0.18em 0;}
    .sf-sidebar-brand .subtitle { font-size: 0.99rem; color: #6fa1f6; }
    hr.sf-sidebar-hr { border:0;border-top:1.7px solid #e0ebff; margin:1.3em 0 1.3em 0; }
    section[data-testid="stSidebar"] {background: #f4f7fd; min-width:240px; max-width:255px; border-right: 1.7px solid #e0ebff;}
    .stRadio > div {gap: 0.2em;}
    .stRadio label {font-size:1.13rem;font-weight:700;color:#406aff;padding:0.6em 1.55em;border-radius:1.3em 0 0 1.3em;margin-bottom:2.5px;display:block;transition:background .14s,color .12s;}
    .stRadio div[role="radiogroup"] > div[data-baseweb="radio"] > div {margin-bottom: 0.45em;}
    .stRadio div[role="radiogroup"] > div[data-baseweb="radio"] input:checked + div > label { background:#e4edff !important; color:#2357c7 !important;}
    .stRadio label:hover { background:#e4edff; color:#2357c7;}
    .stButton>button, .stDownloadButton>button { border-radius: 2.2rem; font-weight: 700; font-size: 1.13rem; min-height: 2.8rem; box-shadow: 0 2px 12px 0 #406aff22; transition: 0.15s;}
    .stButton>button:hover, .stDownloadButton>button:hover { background: #406aff; color: #fff;}
    .section-title { font-size: 1.18rem; font-weight: 800; color: #406aff; margin-bottom: 0.82rem; border-left: 4px solid #5cc6fa; padding-left: 0.7em; letter-spacing: 0.6px;}
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div { border-radius: 0.9rem; min-height: 2.3rem;}
    .stAlert { border-radius: 1.2rem; }
    .stTextArea>div>textarea { border-radius: 0.9rem; min-height: 8.2rem; font-size: 1.08rem; }
    .stSlider { padding-bottom: 1.1rem; }
    .stProgress > div > div { border-radius: 1.1rem; }
    .footer { margin-top: 2.8rem; padding: 1.0rem 0; color: #b1b4bb; text-align: center; font-size: 1.05rem;}
    .sf-sidebar-gh { text-align:center; margin:2.5em 0 0.8em 0;}
    .sf-sidebar-gh a { background:#406aff;color:#fff;font-weight:700;padding:0.56em 1.55em;border-radius:1.7em;box-shadow:0 2px 14px #406aff22;font-size:1.12rem;text-decoration:none;border:2px solid #5cc6fa;transition:background .13s, color .13s;}
    .sf-sidebar-gh a:hover { background:#fff; color:#406aff; border:2px solid #406aff;}
    .sf-stepper {margin:1.2rem 0 2rem 0;display:flex;align-items:center;gap:4px;}
    .sf-step {padding:0.5em 1.2em;border-radius:1.2em;font-size:1.11rem;}
    .sf-step.active {background:#406aff;color:#fff;font-weight:900;}
    .sf-step.inactive {background:#f0f5ff;color:#406aff;}
    .sf-step-arrow {color:#b4c8ff;font-size:1.35em;margin-right:4px;}
    .sf-thumb-row {display:flex;gap:1.2rem;flex-wrap:wrap;margin:0.7em 0 1.1em 0;}
    .sf-thumb {border-radius:1.1em;box-shadow:0 2px 12px #406aff11;border:1.5px solid #e4ebff;padding:0.3em;}
    .sf-section-hr {border-top:2px dashed #e0ebff;margin:2.2em 0 1.6em 0;}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ----------- 侧边栏品牌与导航 -----------
def sidebar_layout():
    with st.sidebar:
        st.markdown("""
        <div class="sf-sidebar-brand">
            <div class="logo">🖼️</div>
            <div class="title">SnapForge</div>
            <div class="subtitle">专业图片批量处理平台</div>
        </div>
        <hr class="sf-sidebar-hr">
        """, unsafe_allow_html=True)
        st.sidebar.title("🌐")
        lang = st.selectbox("界面语言 / Language", ["中文", "English"])
        _ = get_translator(lang)
        nav_items = [
            _("批量/单文件图片处理"),
            _("图片信息查看"),
            _("图片去重"),
            _("AI识别"),
            _("OCR/智能分类"),
            _("图片去背景"),
            _("处理记录"),
        ]
        nav = st.radio("功能导航", nav_items, index=0, label_visibility="collapsed")
        st.markdown('<div class="sf-sidebar-gh"><a href="https://github.com/riceshowerX/SnapForge" target="_blank">GitHub</a></div>', unsafe_allow_html=True)
        st.markdown('<div class="sf-sidebar-gh"><a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" style="background:#fff;color:#406aff;border:2px solid #406aff;">反馈</a></div>', unsafe_allow_html=True)
    return _, nav

_, nav = sidebar_layout()
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# ----------- 主体功能区 -----------

def batch_image_ui(_):
    st.header(_("批量/单文件图片处理"))
    if "batch_step" not in st.session_state:
        st.session_state["batch_step"] = 1

    def goto_step(n):
        st.session_state["batch_step"] = n
        st.rerun()

    steps = [_("上传图片"), _("设置处理参数"), _("确认与执行"), _("下载与预览")]
    st.markdown('<div class="sf-stepper">' +
        "".join(
            f"<span class='sf-step {'active' if idx+1==st.session_state['batch_step'] else 'inactive'}'>{idx+1}. {title}</span>"
            + ("<span class='sf-step-arrow'>&rarr;</span>" if idx < len(steps)-1 else "")
            for idx, title in enumerate(steps)
        ) + "</div>",
        unsafe_allow_html=True
    )

    processor = ImageProcessor()
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # ========== Step 1 ==========
    if st.session_state["batch_step"] == 1:
        mode = st.radio(_("请选择处理模式"), [ _("批量处理（多文件上传）"), _("单文件处理") ], horizontal=True)
        extension = None
        files = []
        if mode == _("批量处理（多文件上传）"):
            files = st.file_uploader(_("上传图片文件"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True, key="up_multi")
            extension = st.selectbox(_("仅处理指定类型"), [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"], index=0)
        else:
            one_file = st.file_uploader(_("上传一个图片文件"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=False, key="up_single")
            if one_file: files = [one_file]
        if files:
            file_paths = []
            for f in files:
                file_name = "".join(x for x in os.path.basename(f.name) if x.isalnum() or x in "._-")
                temp_path = os.path.join(output_dir, file_name)
                with open(temp_path, "wb") as out:
                    out.write(f.read())
                file_paths.append(temp_path)
            st.session_state["uploaded_image_paths"] = file_paths
            st.session_state["uploaded_image_ext"] = extension if mode==_("批量处理（多文件上传）") else None
            st.markdown('<div class="section-title">' + _("图片缩略图预览") + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="sf-thumb-row">', unsafe_allow_html=True)
            for path in file_paths[:8]:
                st.markdown(f'<div class="sf-thumb">', unsafe_allow_html=True)
                st.image(path, caption=os.path.basename(path), width=120)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button(_("下一步"), use_container_width=True, key="to_step2"):
                goto_step(2)
        else:
            st.info(_("请上传图片后点击下一步"), icon="ℹ️")

    # ========== Step 2 ==========
    elif st.session_state["batch_step"] == 2:
        with st.form("batch_opts"):
            st.markdown('<div class="section-title">'+_("基础参数")+'</div>', unsafe_allow_html=True)
            enable_rename = st.checkbox(_("启用重命名"), value=True, key="enable_rename")
            prefix = st.text_input(_("文件名前缀"), "image", disabled=not enable_rename, key="prefix")
            start_num = st.number_input(_("起始编号"), min_value=1, value=1, disabled=not enable_rename, key="start_num")
            enable_convert = st.checkbox(_("启用格式转换"), key="enable_convert")
            target_ext = st.selectbox(_("目标格式"), [".jpg",".jpeg",".png",".bmp",".gif",".tiff",".webp"], index=2, disabled=not enable_convert, key="target_ext")
            enable_compress = st.checkbox(_("启用质量压缩"), key="enable_compress")
            quality = st.slider(_("压缩质量 (1-100)"), 1, 100, 85, disabled=not enable_compress, key="quality")
            st.caption(_("💡 JPEG/WEBP用质量，PNG为压缩等级"))
            st.markdown('<div class="section-title">'+_("高级参数")+'</div>', unsafe_allow_html=True)
            enable_resize = st.checkbox(_("启用尺寸调整"), key="enable_resize")
            resize_width = st.number_input(_("目标宽度(px)"), min_value=1, value=800, disabled=not enable_resize, key="resize_width")
            resize_height = st.number_input(_("目标高度(px)"), min_value=1, value=600, disabled=not enable_resize, key="resize_height")
            resize_mode = st.selectbox(
                _("缩放模式"),
                [_("等比缩放（fit）"), _("拉伸填充（fill）"), _("填充白边（pad）"), _("中心裁剪（crop）")],
                disabled=not enable_resize, key="resize_mode"
            )
            resize_only_shrink = st.checkbox(_("仅缩小不放大"), value=True, disabled=not enable_resize, key="resize_only_shrink")
            preserve_metadata = st.checkbox(_("保留元数据 (EXIF)"), value=True, key="preserve_metadata")
            enable_watermark = st.checkbox(_("启用批量水印"), key="enable_watermark")
            watermark = None
            if enable_watermark:
                wm_text = st.text_input(_("水印内容"), "SnapForge", key="wm_text")
                wm_pos = st.selectbox(_("水印位置"), ["bottom-right","bottom-left","top-right","top-left","center"], key="wm_pos")
                wm_size = st.slider(_("水印字号"), 10, 120, 32, key="wm_size")
                watermark = {"text": wm_text, "size": wm_size, "pos": wm_pos, "color": (255,255,255,128)}
            enable_crop = st.checkbox(_("启用批量裁剪"), key="enable_crop")
            crop_params = None
            if enable_crop:
                crop_x = st.number_input(_("裁剪X"), 0, key="crop_x")
                crop_y = st.number_input(_("裁剪Y"), 0, key="crop_y")
                crop_w = st.number_input(_("裁剪宽"), 0, key="crop_w")
                crop_h = st.number_input(_("裁剪高"), 0, key="crop_h")
                crop_params = {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}
            rotate = st.number_input(_("批量旋转角度"), -360, 360, 0, key="rotate")
            filter_type = st.selectbox(_("批量滤镜"), ["", "grayscale", "sharpen", "blur", "contour", "emboss", "edge", "enhance"], key="filter_type")
            st.session_state["watermark"] = watermark
            st.session_state["crop_params"] = crop_params
            next_step = st.form_submit_button(_("下一步"), use_container_width=True)
            prev_step = st.form_submit_button(_("上一步"), use_container_width=True)
            if next_step: goto_step(3)
            if prev_step: goto_step(1)

    # ========== Step 3 ==========
    elif st.session_state["batch_step"] == 3:
        st.markdown('<div class="section-title">'+_("请确认以下参数")+'</div>', unsafe_allow_html=True)
        st.info(_("如果参数有误请点击上一步返回修改。"))
        st.write(_("重命名:"), st.session_state.get("enable_rename", True))
        st.write(_("格式转换:"), st.session_state.get("enable_convert", False))
        st.write(_("质量压缩:"), st.session_state.get("enable_compress", False))
        st.write(_("尺寸调整:"), st.session_state.get("enable_resize", False))
        st.write(_("批量水印:"), st.session_state.get("enable_watermark", False))
        st.write(_("批量裁剪:"), st.session_state.get("enable_crop", False))
        st.write(_("批量滤镜:"), st.session_state.get("filter_type", ""))
        col1, col2 = st.columns(2)
        if col1.button(_("上一步"), use_container_width=True, key="to_step2_from3"):
            goto_step(2)
        if col2.button(_("🚀 确认无误，开始处理图片！"), use_container_width=True, key="to_step4"):
            goto_step(4)

    # ========== Step 4 ==========
    elif st.session_state["batch_step"] == 4:
        log_area = st.empty()
        progress_bar = st.empty()
        result_area = st.empty()
        download_area = st.empty()
        def streamlit_progress_callback(pct, filename=None):
            if filename:
                progress_bar.progress(pct, f"{_('正在处理')}: {filename}")
            else:
                progress_bar.progress(pct)
        file_paths = st.session_state.get("uploaded_image_paths", [])
        extension = st.session_state.get("uploaded_image_ext", None)
        if extension:
            file_paths = [f for f in file_paths if os.path.splitext(f)[1].lower() == extension]
        if file_paths:
            resize_modes = {0: "fit", 1: "fill", 2: "pad", 3: "crop"}
            log = ProcessLog()
            args = {
                'files': file_paths,
                'prefix': st.session_state.get("prefix", "image") if st.session_state.get("enable_rename", True) else '',
                'start_number': st.session_state.get("start_num", 1),
                'extension': extension if extension else os.path.splitext(file_paths[0])[1].lower(),
                'convert_format': st.session_state.get("target_ext", "") if st.session_state.get("enable_convert", False) else "",
                'quality': st.session_state.get("quality", None) if st.session_state.get("enable_compress", False) else None,
                'progress_callback': streamlit_progress_callback,
                'preserve_metadata': st.session_state.get("preserve_metadata", True),
                'resize_enabled': st.session_state.get("enable_resize", False),
                'resize_width': st.session_state.get("resize_width", None),
                'resize_height': st.session_state.get("resize_height", None),
                'resize_mode': resize_modes.get([_("等比缩放（fit）"),_("拉伸填充（fill）"),_("填充白边（pad）"),_("中心裁剪（crop）")].index(st.session_state.get("resize_mode", _("等比缩放（fit）"))), "fit"),
                'resize_only_shrink': st.session_state.get("resize_only_shrink", True),
                'watermark': st.session_state.get("watermark", None),
                'crop_params': st.session_state.get("crop_params", None),
                'rotate': st.session_state.get("rotate", 0),
                'filter_type': st.session_state.get("filter_type", None),
                'process_log': log,
            }
            result_area.info(_("图片处理中，请耐心等待..."), icon="⏳")
            with st.spinner(_("图片处理中，请耐心等待...")):
                processed, total_files, result_file_paths = processor.batch_process(**args)
                progress_bar.progress(100)
                log_area.text_area(_("处理日志"), log.get_text(), height=220)
                if processed == 0:
                    result_area.error(_("❌ 未成功处理任何图片，请检查日志与参数。"))
                elif processed < total_files:
                    result_area.warning(_(f"⚠️ 有部分图片未处理成功：{processed}/{total_files}"))
                else:
                    result_area.success(_(f"✅ 处理完成：{processed}/{total_files} 个文件"))
                if result_file_paths:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zipf:
                        for file in result_file_paths:
                            if os.path.exists(file):
                                zipf.write(file, arcname=os.path.basename(file))
                    zip_buffer.seek(0)
                    download_area.download_button(
                        label=_("⬇️ 下载全部处理结果（zip包）"),
                        data=zip_buffer,
                        file_name="处理结果.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.session_state["result_file_paths"] = result_file_paths
                    st.markdown('<div class="section-title">' + _("处理结果缩略图预览") + '</div>', unsafe_allow_html=True)
                    st.markdown('<div class="sf-thumb-row">', unsafe_allow_html=True)
                    for p in result_file_paths[:8]:
                        if os.path.exists(p):
                            st.markdown(f'<div class="sf-thumb">', unsafe_allow_html=True)
                            st.image(p, caption=os.path.basename(p), width=120)
                            st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                if st.button(_("返回首页"), use_container_width=True, key="to_home4"):
                    goto_step(1)
        else:
            st.warning(_("未找到上传图片，请返回首页重新上传。"))
            if st.button(_("返回首页"), use_container_width=True, key="to_home_noimg"):
                goto_step(1)

def image_info_ui(_):
    st.header(_("图片信息查看"))
    uploaded = st.file_uploader(_("请上传图片查看信息"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"])
    if uploaded:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        temp_path = os.path.join(output_dir, uploaded.name)
        with open(temp_path, "wb") as out:
            out.write(uploaded.read())
        img = Image.open(temp_path)
        st.markdown('<div class="section-title">' + _("图片预览") + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="sf-thumb-row"><div class="sf-thumb">', unsafe_allow_html=True)
        st.image(img, caption=_("图片预览"), width=180)
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.write(f"{_('尺寸')}: {img.size}  |  {_('模式')}: {img.mode}  |  {_('格式')}: {img.format}")
        st.write(f"{_('文件大小')}: {os.path.getsize(temp_path)//1024} KB")
        dpi = img.info.get("dpi")
        if dpi: st.write(_(f"DPI: {dpi}"))
        exif_data = get_exif_data(temp_path)
        if exif_data:
            with st.expander(_("EXIF详细信息")):
                for k,v in exif_data.items():
                    st.write(f"`{k}`: {v}")
        else:
            st.info(_("无EXIF元数据"))
        dom_color, palette = get_image_main_color(temp_path)
        if dom_color:
            st.write(_("主色调:"))
            st.markdown(f'<div style="width:50px;height:30px;background:rgb{dom_color};display:inline-block;border-radius:3px;border:1px solid #888"></div>', unsafe_allow_html=True)
            st.write(_("色板:"))
            for col in palette:
                st.markdown(f'<div style="width:30px;height:20px;background:rgb{col};display:inline-block;border-radius:2px;border:1px solid #ccc"></div>', unsafe_allow_html=True)
        else:
            st.info(_("无法获取主色信息"))
        buf = plot_image_histogram(temp_path)
        if buf:
            st.image(buf, caption=_("RGB直方图"), use_column_width=False)
        else:
            st.info(_("无法生成直方图"))
        if getattr(img, "is_animated", False):
            st.write(f"{_('帧数')}: {img.n_frames}")

def deduplicate_ui(_):
    st.header(_("图片去重"))
    files = st.file_uploader(_("上传需去重的图片"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True)
    threshold = st.slider(_("相似度阈值(越低越严格)"), 0, 20, 8)
    run_btn = st.button(_("开始去重"), use_container_width=True, disabled=not files)
    output_dir = "output"
    if run_btn and files:
        os.makedirs(output_dir, exist_ok=True)
        file_paths = []
        for f in files:
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.read())
            file_paths.append(path)
        with st.spinner(_("正在查找重复图片...")):
            dups = find_duplicate_images(file_paths, threshold)
            if not dups:
                st.success(_("未检测到重复图片。"))
            else:
                st.warning(_(f"检测到 {len(dups)} 组重复图片："))
                for group in dups:
                    cols = st.columns(len(group))
                    for idx, path in enumerate(group):
                        if os.path.exists(path):
                            img = Image.open(path)
                            cols[idx].image(img, caption=os.path.basename(path), width=120)
                st.info(_("请手动删除或下载需要保留/去除的图片。"))

def ai_recognition_ui(_):
    st.header(_("AI识别 - 云端图片内容标签"))
    files = st.file_uploader(_("上传图片进行AI识别"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True)
    provider = st.selectbox(_("选择AI识别服务"), ["baidu", "deepseek"])
    api_params = {}
    if provider == "baidu":
        api_params["app_id"] = st.text_input("Baidu App ID")
        api_params["api_key"] = st.text_input("Baidu API Key")
        api_params["secret_key"] = st.text_input("Baidu Secret Key")
    elif provider == "deepseek":
        api_params["api_key"] = st.text_input("DeepSeek API Key")
        user_endpoint = st.text_input("DeepSeek Endpoint", value="https://api.deepseek.com/v1/vision/detect")
        allowed_endpoints = ["https://api.deepseek.com/v1/vision/detect"]
        api_params["endpoint"] = user_endpoint if user_endpoint in allowed_endpoints else "https://api.deepseek.com/v1/vision/detect"
    run_btn = st.button(_("开始AI识别"), use_container_width=True, disabled=not files)
    output_dir = "output"
    if run_btn and files:
        os.makedirs(output_dir, exist_ok=True)
        file_paths = []
        for f in files:
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.read())
            file_paths.append(path)
        with st.spinner(_("正在识别图片内容...")):
            try:
                results = ai_image_recognition_cloud(file_paths, provider=provider, **api_params)
                for path, tags in results.items():
                    if os.path.exists(path):
                        st.image(path, caption=os.path.basename(path), width=180)
                        st.write(_("识别标签："), ", ".join(tags))
            except Exception as e:
                st.error(_(f"AI识别调用失败: {e}"))

def ocr_and_classify_ui(_):
    st.header(_("OCR/智能分类"))
    st.markdown(f'<div class="section-title">{_("批量OCR文字识别")}</div>', unsafe_allow_html=True)
    files = st.file_uploader(_("上传图片进行OCR"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True)
    output_dir = "output"
    if st.button(_("开始OCR识别"), disabled=not files):
        os.makedirs(output_dir, exist_ok=True)
        file_paths = []
        for f in files:
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.read())
            file_paths.append(path)
        for idx, p in enumerate(file_paths):
            if os.path.exists(p):
                st.image(p, caption=os.path.basename(p), width=180)
                st.text_area(_("识别结果"), ocr_image(p), key=f"ocr_result_{idx}_{os.path.basename(p)}")
    st.markdown(f'<div class="section-title">{_("智能图片分类（尺寸/主色调）")}</div>', unsafe_allow_html=True)
    files2 = st.file_uploader(_("上传图片进行智能分类"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True, key="classify")
    if st.button(_("开始智能分类"), disabled=not files2):
        os.makedirs(output_dir, exist_ok=True)
        file_paths = []
        for f in files2:
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.read())
            file_paths.append(path)
        for p in file_paths:
            if os.path.exists(p):
                st.image(p, caption=os.path.basename(p), width=120)
                st.write(_("分类结果:"), ", ".join(smart_classify(p)))

def remove_bg_ui(_):
    st.header(_("图片去背景"))
    files = st.file_uploader(_("上传图片进行去背景"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True)
    output_dir = "output"
    if st.button(_("开始去背景"), disabled=not files):
        os.makedirs(output_dir, exist_ok=True)
        result_paths = []
        for f in files:
            in_path = os.path.join(output_dir, f.name)
            with open(in_path, "wb") as out:
                out.write(f.read())
            out_path = os.path.splitext(in_path)[0] + "_nobg.png"
            try:
                remove_background(in_path, output_path=out_path)
                result_paths.append(out_path)
            except Exception as e:
                st.error(f"{os.path.basename(f.name)} 去背景失败: {e}")
        for p in result_paths:
            if os.path.exists(p):
                st.image(p, caption=os.path.basename(p), width=180)
        if result_paths:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for file in result_paths:
                    zipf.write(file, arcname=os.path.basename(file))
            zip_buffer.seek(0)
            st.download_button(
                label=_("⬇️ 下载全部去背景结果（zip包）"),
                data=zip_buffer,
                file_name="去背景结果.zip",
                mime="application/zip",
                use_container_width=True
            )

def history_ui(_):
    st.header(_("最近一次处理结果预览"))
    rfp = st.session_state.get("result_file_paths", [])
    if rfp:
        cols = st.columns(4)
        for idx, p in enumerate(rfp[:8]):
            if os.path.exists(p):
                cols[idx % 4].image(p, caption=os.path.basename(p), width=160)
            else:
                st.warning(f"{p} 文件不存在，可能已被删除")
    else:
        st.info(_("暂无最近处理结果"))

# ----------- 主入口路由 -----------
if nav == _("批量/单文件图片处理"):
    batch_image_ui(_)
elif nav == _("图片信息查看"):
    image_info_ui(_)
elif nav == _("图片去重"):
    deduplicate_ui(_)
elif nav == _("AI识别"):
    ai_recognition_ui(_)
elif nav == _("OCR/智能分类"):
    ocr_and_classify_ui(_)
elif nav == _("图片去背景"):
    remove_bg_ui(_)
elif nav == _("处理记录"):
    history_ui(_)

# ----------- 页脚 -----------
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span>© 2025 <b>SnapForge</b> | 
    <a href="https://github.com/riceshowerX/SnapForge" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">GitHub开源项目</a> | 
    设计&开发：<a href="https://github.com/riceshowerX" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">riceshowerX</a>
    </span>
</div>
""", unsafe_allow_html=True)