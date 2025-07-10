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

# ---------- 全局UI美化 ----------
custom_css = """
<style>
body { background: #f3f6fa; }
.header-banner {margin-top: -2.5rem;margin-bottom: 2.5rem;padding: 36px 0 28px 0;background: linear-gradient(90deg, #406aff 0%, #5cc6fa 100%);border-radius: 1.2rem;box-shadow: 0 4px 24px 0 #406aff22;color: #fff;text-align: center;position: relative;}
.header-banner .logo {font-size: 3.6rem;line-height: 1;margin-bottom: 6px;}
.header-banner h1 {font-size: 2.6rem;font-weight: 850;letter-spacing: 1.2px;margin-bottom: 8px;font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;}
.header-banner .subtitle {font-size: 1.15rem;font-weight: 500;letter-spacing: 0.2px;margin-bottom: 0;}
.gh-btn-area {margin: 1.3rem auto 0.7rem auto;display: flex;justify-content: center;align-items: center;gap: 1.2em;}
.gh-btn-area a {background: #fff;color: #406aff;font-weight: 700;padding: 0.5em 1.7em;border-radius: 2em;box-shadow: 0 2px 14px #406aff25;font-size: 1.08rem;text-decoration: none;transition: background 0.15s, color 0.15s;border: 2px solid #5cc6fa;}
.gh-btn-area a:hover {background: #406aff;color: #fff;border: 2px solid #406aff;}
.gh-author {display: flex;flex-direction: row;align-items: center;justify-content: center;margin-bottom: 0.6rem;gap: 0.6em;font-size: 1.05rem;}
.gh-author img {border-radius: 50%;border: 2px solid #fff;width: 34px;height: 34px;box-shadow: 0 2px 10px #406aff22;margin-right: 0.4em;}
.main-card {background: #fff;border-radius: 1.2rem;padding: 2.2rem 2rem 1.5rem 2rem;margin: 0 auto 2rem auto;box-shadow: 0 2px 16px 0 #406aff10;max-width: 820px;}
.card h3 {font-size: 1.35rem;font-weight: 700;margin-bottom: 1.25rem;color: #406aff;}
.stButton>button, .stDownloadButton>button {border-radius: 1.8rem;font-weight: 700;font-size: 1.1rem;min-height: 2.7rem;box-shadow: 0 2px 12px 0 #406aff22;transition: 0.2s;}
.stButton>button:hover, .stDownloadButton>button:hover {background: #406aff;color: #fff;}
.stSlider {padding-bottom: 1.0rem;}
.stProgress > div > div {border-radius: 1rem;}
.stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div {border-radius: 0.7rem;min-height: 2.3rem;}
.stAlert {border-radius: 1rem;}
.stTextArea>div>textarea {border-radius: 0.7rem;min-height: 8rem;font-size: 1.03rem;}
.res-card {background:linear-gradient(100deg,#e9f2fe 0%,#e8fcff 100%);border-radius: 1.2rem;padding: 1.5rem 1.5rem 1.3rem 1.5rem;margin: 1.3rem 0;box-shadow: 0 2px 14px 0 #406aff14;}
.footer {margin-top: 2.5rem;padding: 0.8rem 0;color: #b1b4bb;text-align: center;font-size: 1.02rem;}
@media (max-width: 800px) {.header-banner { font-size: 1.8rem; padding: 28px 0 18px 0; }.main-card { padding: 1.1rem 0.7rem 1rem 0.7rem; }.res-card { padding: 1.0rem 0.4rem 1.0rem 0.4rem; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------- 顶部Banner ----------
st.markdown("""
<div class="header-banner">
    <div class="logo">🖼️⚒️</div>
    <h1>SnapForge</h1>
    <div class="subtitle">
        <b>高效、专业、美观的批量/单文件图片处理平台</b><br>
        <span style="opacity:.85">完全开源，支持批量处理、去重、AI识别、去背景、智能分析等高级功能</span>
    </div>
    <div class="gh-btn-area">
        <a href="https://github.com/riceshowerX/SnapForge" target="_blank" title="前往GitHub仓库">GitHub仓库主页</a>
        <a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" title="反馈建议/提Issue">反馈建议</a>
    </div>
    <div class="gh-author">
        <img src="https://avatars.githubusercontent.com/u/138862916?v=4">
        <span>
            由 <a href="https://github.com/riceshowerX" target="_blank" style="color:#fff;text-decoration:underline;font-weight:600;">riceshowerX</a> 开发 &nbsp;|&nbsp; <a href="https://github.com/riceshowerX/SnapForge" target="_blank" style="color:#fff;text-decoration:underline;">@SnapForge</a>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- 语言切换 ----------
st.sidebar.title("🌐")
lang = st.sidebar.selectbox("界面语言 / Language", ["中文", "English"])
_ = get_translator(lang)

# ---------- 主体 ----------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
tab_titles = [
    _("批量/单文件图片处理"), _("图片信息查看"), _("图片去重"),
    _("AI识别"), _("OCR/智能分类"), _("图片去背景"), _("处理记录")
]
tabs = st.tabs(tab_titles)

# ---------- Tab 0: 批量/单文件图片处理 ----------
with tabs[0]:
    processor = ImageProcessor()
    def save_uploaded_files(files, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        file_paths = []
        for f in files:
            file_name = os.path.basename(f.name)
            file_name = "".join(x for x in file_name if x.isalnum() or x in "._-")
            temp_path = os.path.join(output_dir, file_name)
            with open(temp_path, "wb") as out:
                out.write(f.read())
            file_paths.append(temp_path)
        return file_paths
    def pack_files_to_zip(file_paths):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file in file_paths:
                if os.path.exists(file):
                    zipf.write(file, arcname=os.path.basename(file))
        zip_buffer.seek(0)
        return zip_buffer

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h3>{_("📂 上传图片 & 选择模式")}</h3>', unsafe_allow_html=True)
    mode = st.radio(_("处理模式"), [ _("批量处理（多文件上传）"), _("单文件处理") ], horizontal=True)
    files = []
    extension = None
    if mode == _("批量处理（多文件上传）"):
        files = st.file_uploader(_("上传图片文件"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=True)
        extension = st.selectbox(_("仅处理指定类型"), [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"], index=0)
    else:
        one_file = st.file_uploader(_("上传一个图片文件"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"], accept_multiple_files=False)
        if one_file:
            files = [one_file]
        extension = None
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h3>{_("🛠️ 图片处理参数")}</h3>', unsafe_allow_html=True)
    with st.expander(_("重命名、格式转换与压缩"), expanded=True):
        enable_rename = st.checkbox(_("启用重命名"), value=True)
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
        resize_mode = st.selectbox(
            _("缩放模式"),
            [_("等比缩放（fit）"), _("拉伸填充（fill）"), _("填充白边（pad）"), _("中心裁剪（crop）")],
            disabled=not enable_resize
        )
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
            crop_x = st.number_input(_("裁剪X"), 0)
            crop_y = st.number_input(_("裁剪Y"), 0)
            crop_w = st.number_input(_("裁剪宽"), 0)
            crop_h = st.number_input(_("裁剪高"), 0)
            crop_params = {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}
        rotate = st.number_input(_("批量旋转角度"), -360, 360, 0)
        filter_type = st.selectbox(_("批量滤镜"), ["", "grayscale", "sharpen", "blur", "contour", "emboss", "edge", "enhance"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card res-card">', unsafe_allow_html=True)
    st.markdown(f'<h3>{_("📄 处理进度与结果")}</h3>', unsafe_allow_html=True)
    log_area = st.empty()
    progress_bar = st.empty()
    result_area = st.empty()
    download_area = st.empty()
    def streamlit_progress_callback(pct, filename=None):
        if filename:
            progress_bar.progress(pct, f"{_('正在处理')}: {filename}")
        else:
            progress_bar.progress(pct)
    run_btn = st.button(_("🚀 开始处理图片"), type="primary", use_container_width=True, disabled=not files)
    output_dir = "output"
    if run_btn:
        if not files or (mode == _("批量处理（多文件上传）") and len(files) == 0):
            result_area.warning(_("请先上传图片文件！"), icon="⚠️")
        else:
            if enable_resize and (resize_width < 1 or resize_height < 1):
                result_area.error(_("目标宽或高必须为正整数！"), icon="❌")
                st.stop()
            os.makedirs(output_dir, exist_ok=True)
            try:
                file_paths = save_uploaded_files(files, output_dir)
                if mode == _("批量处理（多文件上传）") and extension:
                    selected_paths = [f for f in file_paths if os.path.splitext(f)[1].lower() == extension]
                    if not selected_paths:
                        result_area.error(_(f"没有找到扩展名为{extension}的文件。"), icon="❌")
                        st.stop()
                    file_paths = selected_paths
                resize_modes = {
                    0: "fit",
                    1: "fill",
                    2: "pad",
                    3: "crop"
                }
                log = ProcessLog()
                args = {
                    'files': file_paths,
                    'prefix': prefix if enable_rename else '',
                    'start_number': start_num if enable_rename else 1,
                    'extension': extension if extension else os.path.splitext(file_paths[0])[1].lower(),
                    'convert_format': target_ext if enable_convert else '',
                    'quality': quality if enable_compress else None,
                    'progress_callback': streamlit_progress_callback,
                    'preserve_metadata': preserve_metadata,
                    'resize_enabled': enable_resize,
                    'resize_width': resize_width if enable_resize else None,
                    'resize_height': resize_height if enable_resize else None,
                    'resize_mode': resize_modes[[_("等比缩放（fit）"),_("拉伸填充（fill）"),_("填充白边（pad）"),_("中心裁剪（crop）")].index(resize_mode)] if enable_resize else "fit",
                    'resize_only_shrink': resize_only_shrink if enable_resize else True,
                    'watermark': watermark,
                    'crop_params': crop_params,
                    'rotate': rotate,
                    'filter_type': filter_type if filter_type else None,
                    'process_log': log,
                }
                with st.spinner(_("图片处理中，请耐心等待...")):
                    result_area.info(_("正在处理图片，请耐心等待..."), icon="⏳")
                    processed, total_files, result_file_paths = processor.batch_process(**args)
                    progress_bar.progress(100)
                    log_area.text_area(_("处理日志"), log.get_text(), height=200)
                    if processed == 0:
                        result_area.error(_("❌ 未成功处理任何图片，请检查日志与参数。"))
                    elif processed < total_files:
                        result_area.warning(_(f"⚠️ 有部分图片未处理成功：{processed}/{total_files}"))
                    else:
                        result_area.success(_(f"✅ 处理完成：{processed}/{total_files} 个文件"))
                    if result_file_paths:
                        zip_buffer = pack_files_to_zip(result_file_paths)
                        download_area.download_button(
                            label=_("⬇️ 下载全部处理结果（zip包）"),
                            data=zip_buffer,
                            file_name="处理结果.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    st.session_state["result_file_paths"] = result_file_paths
            except Exception as e:
                result_area.error(_(f"处理过程中发生错误: {e}"), icon="❗")
                log_area.text_area(_("日志"), log.get_text() if 'log' in locals() else str(e), height=200)
    else:
        result_area.info(_("请上传图片并设置参数后，点击【开始处理图片】"), icon="ℹ️")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 1: 图片信息查看 ----------
with tabs[1]:
    st.subheader(_("图片信息查看"))
    uploaded = st.file_uploader(_("请上传图片查看信息"), type=["jpg","jpeg","png","bmp","gif","tiff","webp"])
    if uploaded:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        temp_path = os.path.join(output_dir, uploaded.name)
        with open(temp_path, "wb") as out:
            out.write(uploaded.read())
        img = Image.open(temp_path)
        st.image(img, caption=_("图片预览"))
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

# ---------- Tab 2: 图片去重 ----------
with tabs[2]:
    st.subheader(_("图片去重"))
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

# ---------- Tab 3: AI识别 ----------
with tabs[3]:
    st.subheader(_("AI识别 - 云端图片内容标签"))
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
        from urllib.parse import urlparse, urlunparse
        allowed_endpoints = ["https://api.deepseek.com/v1/vision/detect"]
        parsed_endpoint = urlparse(user_endpoint)
        sanitized_endpoint = urlunparse((parsed_endpoint.scheme, parsed_endpoint.netloc, parsed_endpoint.path, '', '', ''))
        api_params["endpoint"] = sanitized_endpoint if sanitized_endpoint in allowed_endpoints else "https://api.deepseek.com/v1/vision/detect"
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

# ---------- Tab 4: OCR/智能分类 ----------
with tabs[4]:
    st.subheader(_("批量OCR文字识别"))
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

    st.subheader(_("智能图片分类（尺寸/主色调）"))
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

# ---------- Tab 5: 图片去背景 ----------
with tabs[5]:
    st.subheader(_("图片去背景"))
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

# ---------- Tab 6: 处理记录/结果预览 ----------
with tabs[6]:
    st.subheader(_("最近一次处理结果预览"))
    rfp = st.session_state.get("result_file_paths", [])
    if rfp:
        for p in rfp[:6]:
            if os.path.exists(p):
                st.image(p, caption=os.path.basename(p), width=160)
            else:
                st.warning(f"{p} 文件不存在，可能已被删除")
    else:
        st.info(_("暂无最近处理结果"))

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span>© 2025 <b>SnapForge</b> | <a href="https://github.com/riceshowerX/SnapForge" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">GitHub开源项目</a> | 设计&开发：<a href="https://github.com/riceshowerX" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">riceshowerX</a>
    </span>
</div>
""", unsafe_allow_html=True)
