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
body { background: #f5f7fb; }
.header-banner { margin-top: -2.5rem; margin-bottom: 2.5rem; padding: 36px 0 28px 0;
background: linear-gradient(90deg, #406aff 0%, #5cc6fa 100%);
border-radius: 1.2rem; box-shadow: 0 4px 24px 0 #406aff22;
color: #fff; text-align: center; position: relative;}
.header-banner .logo { font-size: 3.6rem; line-height: 1; margin-bottom: 6px;
filter: drop-shadow(0 4px 8px #406aff44);}
.header-banner h1 { font-size: 2.6rem; font-weight: 900; letter-spacing: 1.2px; margin-bottom: 8px;
font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;}
.header-banner .subtitle { font-size: 1.15rem; font-weight: 500; letter-spacing: 0.2px; margin-bottom: 0;}
.gh-btn-area { margin: 1.3rem auto 0.7rem auto; display: flex; justify-content: center; align-items: center; gap: 1.2em;}
.gh-btn-area a { background: #fff; color: #406aff; font-weight: 700; padding: 0.5em 1.7em;
border-radius: 2em; box-shadow: 0 2px 14px #406aff25; font-size: 1.08rem;
text-decoration: none; transition: background 0.15s, color 0.15s; border: 2px solid #5cc6fa;}
.gh-btn-area a:hover { background: #406aff; color: #fff; border: 2px solid #406aff;}
.gh-author { display: flex; flex-direction: row; align-items: center; justify-content: center;
margin-bottom: 0.6rem; gap: 0.6em; font-size: 1.05rem;}
.gh-author img { border-radius: 50%; border: 2px solid #fff; width: 34px; height: 34px;
box-shadow: 0 2px 10px #406aff22; margin-right: 0.4em;}
.main-card { background: #fff; border-radius: 1.2rem; padding: 2.2rem 2rem 1.5rem 2rem; margin: 0 auto 2rem auto;
box-shadow: 0 2px 16px 0 #406aff10; max-width: 900px;}
.card { background: #f8fbff; border-radius: 1rem; padding: 1.1rem 1.2rem 1.2rem 1.2rem; margin-bottom: 1.4rem;
box-shadow: 0 2px 10px 0 #406aff10;}
.card h3 { font-size: 1.28rem; font-weight: 700; margin-bottom: 1.1rem; color: #406aff;
letter-spacing: 0.5px;}
.stButton>button, .stDownloadButton>button { border-radius: 2rem; font-weight: 700; font-size: 1.07rem; min-height: 2.75rem;
box-shadow: 0 2px 12px 0 #406aff22; transition: 0.15s;}
.stButton>button:hover, .stDownloadButton>button:hover { background: #406aff; color: #fff;}
.stSlider { padding-bottom: 0.8rem; }
.stProgress > div > div { border-radius: 1rem; }
.stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div { border-radius: 0.7rem; min-height: 2.2rem;}
.stAlert { border-radius: 1rem; }
.stTextArea>div>textarea { border-radius: 0.7rem; min-height: 8rem; font-size: 1.03rem; }
.res-card { background:linear-gradient(100deg,#e9f2fe 0%,#e8fcff 100%);
border-radius: 1.2rem; padding: 1.5rem 1.5rem 1.3rem 1.5rem; margin: 1.3rem 0;
box-shadow: 0 2px 14px 0 #406aff14;}
.section-title { font-size: 1.12rem; font-weight: 600; color: #406aff; margin-bottom: 0.5rem;
letter-spacing: 0.5px; border-left: 4px solid #5cc6fa; padding-left: 0.7em;}
.stTabs [data-baseweb="tab"] { font-size: 1.08rem; font-weight: 600; letter-spacing: 0.2px;}
.stTabs [data-baseweb="tab"]:hover { color: #406aff !important;}
.footer { margin-top: 2.5rem; padding: 0.8rem 0; color: #b1b4bb; text-align: center; font-size: 1.02rem;}
@media (max-width: 900px) {.header-banner { font-size: 1.8rem; padding: 26px 0 13px 0; }
.main-card { padding: 1.1rem 0.7rem 1rem 0.7rem; }.res-card { padding: 1.0rem 0.4rem 1.0rem 0.4rem; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------- 顶部Banner ----------
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 26px 12px 26px;background:linear-gradient(90deg,#406aff 0%,#5cc6fa 100%);border-radius:0 0 1.1rem 1.1rem;box-shadow:0 2px 16px #406aff10;margin-bottom:1.2rem;">
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-size:2.1rem;">🖼️</span>
    <span style="font-size:1.5rem;font-weight:700;color:#fff;letter-spacing:1.2px;">SnapForge</span>
    <small style="font-size:.92rem;color:#e3eaff;opacity:.8;margin-left:.7em;">高效图片批处理工具</small>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <a href="https://github.com/riceshowerX/SnapForge" target="_blank" style="color:#fff;font-weight:600;padding:0.4em 1.2em;background:#406aff;border-radius:1.7em;text-decoration:none;border:1.5px solid #fff1;">GitHub</a>
    <a href="https://github.com/riceshowerX/SnapForge/issues/new/choose" target="_blank" style="color:#406aff;background:#fff;font-weight:600;padding:0.4em 1.2em;border-radius:1.7em;text-decoration:none;border:1.5px solid #5cc6fa;">反馈</a>
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

# ---------- Tab 0: 批量/单文件图片处理（分步引导） ----------
with tabs[0]:
    if "batch_step" not in st.session_state:
        st.session_state["batch_step"] = 1

    def goto_step(n):
        st.session_state["batch_step"] = n
        st.rerun()

    steps = [
        _("上传图片"), _("设置处理参数"), _("确认与执行"), _("下载与预览")
    ]
    stepper_html = '<div style="margin:1.5rem 0"><b>'
    for idx, title in enumerate(steps):
        if idx+1 == st.session_state["batch_step"]:
            stepper_html += f'<span style="color:#406aff">[{idx+1}] {title}</span>'
        else:
            stepper_html += f'<span style="color:#8aa8ff">[{idx+1}] {title}</span>'
        if idx < len(steps)-1:
            stepper_html += ' <span style="color:#ccc;font-size:1.1em;">→</span> '
    stepper_html += '</b></div>'
    st.markdown(stepper_html, unsafe_allow_html=True)

    processor = ImageProcessor()
    output_dir = "output"
    if not os.path.exists(output_dir): os.makedirs(output_dir, exist_ok=True)

    # Step 1: 上传图片并立即保存
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
                file_name = os.path.basename(f.name)
                file_name = "".join(x for x in file_name if x.isalnum() or x in "._-")
                temp_path = os.path.join(output_dir, file_name)
                with open(temp_path, "wb") as out:
                    out.write(f.read())
                file_paths.append(temp_path)
            st.session_state["uploaded_image_paths"] = file_paths
            st.session_state["uploaded_image_ext"] = extension if mode==_("批量处理（多文件上传）") else None

            st.markdown("##### " + _("图片缩略图预览"))
            img_cols = st.columns(min(len(file_paths), 4))
            for idx, path in enumerate(file_paths[:8]):
                img_cols[idx % 4].image(path, caption=os.path.basename(path), width=120)
            if st.button(_("下一步"), use_container_width=True, key="to_step2"):
                st.session_state["batch_step"] = 2
                st.rerun()
        else:
            st.info(_("请上传图片后点击下一步"), icon="ℹ️")

    # Step 2: 设置处理参数（动态显隐，参数入 session_state）
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
            # 保存全部参数到 session_state
            st.session_state["watermark"] = watermark
            st.session_state["crop_params"] = crop_params

            next_step = st.form_submit_button(_("下一步"), use_container_width=True)
            prev_step = st.form_submit_button(_("上一步"), use_container_width=True)
            if next_step:
                st.session_state["batch_step"] = 3
                st.rerun()
            if prev_step:
                st.session_state["batch_step"] = 1
                st.rerun()

    # Step 3: 确认参数
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
            st.session_state["batch_step"] = 2
            st.rerun()
        if col2.button(_("🚀 确认无误，开始处理图片！"), use_container_width=True, key="to_step4"):
            st.session_state["batch_step"] = 4
            st.rerun()

    # Step 4: 处理状态与结果
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
                log_area.text_area(_("处理日志"), log.get_text(), height=200)
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
                    st.markdown("##### " + _("处理结果缩略图预览"))
                    cols = st.columns(4)
                    for idx, p in enumerate(result_file_paths[:8]):
                        if os.path.exists(p):
                            cols[idx % 4].image(p, caption=os.path.basename(p), width=120)
                if st.button(_("返回首页"), use_container_width=True, key="to_home4"):
                    st.session_state["batch_step"] = 1
                    st.rerun()
        else:
            st.warning(_("未找到上传图片，请返回首页重新上传。"))
            if st.button(_("返回首页"), use_container_width=True, key="to_home_noimg"):
                st.session_state["batch_step"] = 1
                st.rerun()

# ---------- Tab 1: 图片信息查看（无变化） ----------
with tabs[1]:
    st.markdown(f'<div class="section-title">{_("图片信息查看")}</div>', unsafe_allow_html=True)
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

# ---------- Tab 2: 图片去重（缩略图分组横向展示） ----------
with tabs[2]:
    st.markdown(f'<div class="section-title">{_("图片去重")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="section-title">{_("AI识别 - 云端图片内容标签")}</div>', unsafe_allow_html=True)
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

# ---------- Tab 4: OCR/智能分类 ----------
with tabs[4]:
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

# ---------- Tab 5: 图片去背景 ----------
with tabs[5]:
    st.markdown(f'<div class="section-title">{_("图片去背景")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="section-title">{_("最近一次处理结果预览")}</div>', unsafe_allow_html=True)
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

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span>© 2025 <b>SnapForge</b> | 
    <a href="https://github.com/riceshowerX/SnapForge" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">GitHub开源项目</a> | 
    设计&开发：<a href="https://github.com/riceshowerX" target="_blank" style="color:#406aff;text-decoration:none;font-weight:500;">riceshowerX</a>
    </span>
</div>
""", unsafe_allow_html=True)