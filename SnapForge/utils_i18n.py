# utils_i18n.py

"""
SnapForge Internationalization (i18n) Module.
This file contains the translation dictionary and the function to get the translator.
(Version with AI Recognition feature removed)
"""

lang_dict = {
    # ===================================================================
    # 应用程序全局文本
    # ===================================================================
    "高效、专业、美观的批量图片处理平台": "An efficient, professional, and beautiful platform for image processing.",
    "⚙️ 设置": "⚙️ Settings",
    "前往GitHub仓库": "Go to GitHub Repository",
    "反馈建议/提Issue": "Feedback & Issues",
    "由": "by",
    "设计与开发": "Designed & Developed",
    
    # ===================================================================
    # Tab 标题
    # ===================================================================
    "批量处理": "Batch Process",
    "信息查看": "Image Info",
    "图片去重": "Find Duplicates",
    "OCR分类": "OCR & Classify",
    "智能去背景": "AI Background Remover",
    "处理记录": "History & Results",

    # ===================================================================
    # Tab 0: 批量处理
    # ===================================================================
    "📂 上传与处理模式": "1. Upload & Mode",
    "处理模式": "Processing Mode",
    "批量处理（多文件上传）": "Batch Upload (Multiple Files)",
    "单文件处理": "Single File",
    "上传图片文件（可混合格式）": "Upload Image Files (Mixed Formats Supported)",
    "文件筛选": "File Filtering",
    "处理所有上传的图片格式": "Process All Uploaded Formats",
    "仅处理指定格式的图片": "Process Only a Specific Format",
    "“处理所有”会对上传的各种格式图片进行处理；“仅处理指定”则只处理下拉框中选定的类型。": "Process All: Handles all uploaded image formats. Process Specific: Only handles the format selected in the dropdown.",
    "选择要处理的格式": "Select format to process",
    "上传一个图片文件": "Upload a Single Image File",
    "🛠️ 图片处理参数": "2. Configure Parameters",
    "重命名、格式转换与压缩": "Rename, Convert & Compress",
    "启用重命名": "Enable Renaming", "文件名前缀": "Filename Prefix", "起始编号": "Start Number",
    "启用格式转换": "Enable Format Conversion", "目标格式": "Target Format",
    "启用质量压缩": "Enable Quality Compression", "压缩质量 (1-100)": "Quality (1-100)",
    "💡 JPEG/WEBP用质量，PNG为压缩等级": "Tip: 'Quality' for JPEG/WEBP, 'Compression Level' for PNG.",
    "尺寸调整与高级选项": "Resize & Advanced Options",
    "启用尺寸调整": "Enable Resizing", "目标宽度(px)": "Target Width (px)", "目标高度(px)": "Target Height (px)",
    "缩放模式": "Resizing Mode", "等比缩放（fit）": "Fit (Keep Aspect Ratio)", "拉伸填充（fill）": "Fill (Stretch)",
    "填充白边（pad）": "Pad (Add Borders)", "中心裁剪（crop）": "Crop from Center",
    "仅缩小不放大": "Downscale Only (No Enlarge)", "保留元数据 (EXIF)": "Keep EXIF Metadata",
    "启用批量水印": "Enable Watermark", "水印内容": "Watermark Text", "水印位置": "Position", "水印字号": "Font Size",
    "启用批量裁剪": "Enable Cropping", "裁剪X": "Crop X", "裁剪Y": "Crop Y", "裁剪宽": "Crop Width", "裁剪高": "Crop Height",
    "批量旋转角度": "Rotation Angle", "批量滤镜": "Filter",
    "🚀 开始处理图片": "🚀 Process Images",
    
    # --- 批量处理中的动态消息和日志 ---
    "正在处理: {}": "Processing: {}", "处理中...": "Processing...",
    "请先上传图片文件！": "Please upload image files first!",
    "图片处理中，请耐心等待...": "Processing images, please wait...", "正在处理图片...": "Processing images...",
    "处理完成！": "Processing Complete!", "处理日志": "Processing Log", "错误日志": "Error Log",
    "❌ 未成功处理任何图片，请检查日志。": "❌ Failed to process any images. Please check the log.",
    "⚠️ 部分成功：处理了 {} / {} 张符合条件的图片。": "⚠️ Partial Success: Processed {} out of {} eligible images.",
    "✅ 处理完成：{} / {}": "✅ Success: Processed {} / {} images.",
    "⬇️ 下载全部结果": "⬇️ Download All Results",
    "处理中发生严重错误: {}": "A critical error occurred during processing: {}",

    # ===================================================================
    # Tab 1: 信息查看
    # ===================================================================
    "🖼️ 图片信息查看": "🖼️ View Image Information",
    "上传图片以查看详细信息": "Upload an image to view its details",
    "图片预览": "Preview", "尺寸": "Dimensions", "文件大小": "File Size",
    "🎨 色彩与格式信息": "🎨 Color & Format Information", "模式": "Mode", "格式": "Format", "帧数": "Frame Count",
    "主色调": "Dominant Color", "RGB直方图": "RGB Histogram",
    "📷 EXIF 元数据": "📷 EXIF Metadata", "分析图片时出错: {}": "Error analyzing image: {}",

    # ===================================================================
    # Tab 2: 图片去重
    # ===================================================================
    "👯‍♀️ 图片去重": "👯‍♀️ Find Duplicates",
    "上传需要去重的图片(至少2张)": "Upload images to find duplicates (min. 2)",
    "相似度阈值 (越低越严格)": "Similarity Threshold (Lower is stricter)",
    "开始去重": "Find Duplicates", "正在查找重复图片...": "Searching for duplicate images...",
    "✅ 未检测到重复图片。": "✅ No duplicate images were detected.",
    "检测到 {} 组重复图片：": "Found {} groups of duplicate images:",
    "第": "Group", "组": "",

    # ===================================================================
    # Tab 3 (原Tab 4): OCR & 分类
    # ===================================================================
    "🔍 OCR & 智能分类": "🔍 OCR & Smart Classification",
    "此选项卡提供两种独立的智能工具。": "This tab provides two independent smart tools.",
    "批量OCR文字识别": "Batch OCR",
    "上传图片进行OCR": "Upload images for OCR", "开始OCR识别": "Start OCR",
    "识别结果": "Recognition Result",
    "智能图片分类": "Smart Classification",
    "上传图片进行分类": "Upload images for classification", "开始智能分类": "Start Classification",
    "分类结果: ": "Classification Result: ",

    # ===================================================================
    # Tab 4 (原Tab 5): 智能去背景
    # ===================================================================
    "🪄 智能去背景": "🪄 AI Background Remover",
    "上传图片去除背景(推荐PNG)": "Upload images to remove background (PNG recommended)",
    "开始去背景": "Remove Background", "正在去除背景...": "Removing backgrounds...",
    "去背景失败": "failed to remove background",
    
    # ===================================================================
    # Tab 5 (原Tab 6): 处理记录
    # ===================================================================
    "🗂️ 最近处理结果预览": "🗂️ Preview of Last Results",
    "这里将展示“批量处理”选项卡最近一次成功运行的结果。": "This area shows the results from the last successful run in the 'Batch Process' tab.",
    "不存在": "does not exist",
    "暂无最近处理结果。请先在“批量处理”中运行一次任务。": "No recent results. Please run a task in the 'Batch Process' tab first.",
}

def get_translator(lang="中文"):
    """
    根据所选语言返回一个翻译函数。
    """
    def _(text_key):
        if lang == "中文":
            return text_key
        return lang_dict.get(text_key, text_key)
    return _