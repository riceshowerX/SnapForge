# utils_i18n.py (Updated and Synced with the latest app.py)

lang_dict = {
    # 核心描述
    "高效、专业、美观的批量图片处理平台": "An efficient, professional, and beautiful platform for image processing.",
    
    # 侧边栏与页脚
    "⚙️ 设置": "⚙️ Settings",
    "清理缓存和重置状态": "Clear Cache & Reset State",
    "缓存已清理！页面将刷新。": "Cache cleared! The page will now refresh.",
    "由": "by", 
    "设计与开发": "Designed & Developed",
    
    # 顶部横幅与链接
    "前往GitHub仓库": "Go to GitHub Repository", 
    "反馈建议/提Issue": "Feedback & Issues",
    "反馈建议": "Feedback",

    # 主标签页标题
    "批量处理": "Batch Process", 
    "信息查看": "Image Info", 
    "图片去重": "Find Duplicates",
    "智能工具": "Smart Tools", # 更新：合并了OCR和去背景
    "处理记录": "History",

    # --- 批量处理选项卡 ---
    # 上传区
    "📂 上传文件": "1. Upload Files",
    "上传图片文件（可混合格式）": "Upload Image Files (Mixed Formats Supported)",
    
    # 参数配置区
    "🛠️ 图片处理参数": "2. Configure Parameters",
    "重命名、格式转换与压缩": "Rename, Convert & Compress",
    "启用重命名": "Enable Renaming",
    "文件名前缀": "Filename Prefix", 
    "起始编号": "Start Number",
    "高级命名模板": "Advanced Naming Template",
    "可用占位符: {prefix}, {counter}, {original_filename}, {width}, {height}": "Placeholders: {prefix}, {counter}, {original_filename}, {width}, {height}",
    "启用格式转换": "Enable Format Conversion", 
    "目标格式": "Target Format",
    "启用质量压缩": "Enable Quality Compression", 
    "压缩质量": "Quality",
    "对JPG/WEBP生效，PNG会转换为压缩等级。": "For JPG/WEBP. For PNG, this is converted to compression level.",

    # 高级参数
    "尺寸、水印与高级调整": "Resize, Watermark & Advanced", # 更新
    "启用尺寸调整": "Enable Resizing",
    "目标宽度(px)": "Target Width (px)", 
    "目标高度(px)": "Target Height (px)",
    "缩放模式": "Resizing Mode",
    "保持比例适应边界 (Contain)": "Keep Ratio & Fit (Contain)", # 更新
    "保持比例裁剪填充 (Cover)": "Keep Ratio & Crop (Cover)", # 更新
    "拉伸至指定尺寸 (Stretch)": "Stretch to Fill", # 更新
    "仅缩小不放大": "Downscale Only (No Enlarge)", 
    "保留元数据 (EXIF)": "Keep EXIF Metadata",
    "并行处理核心数": "Parallel Processing Cores", # 新增
    "启用批量水印": "Enable Watermark", 
    "水印内容": "Watermark Text", 
    "水印位置": "Position", 
    "水印字号": "Font Size",
    "启用批量裁剪": "Enable Cropping", 
    "从左上角(x,y)开始裁剪一个(w,h)大小的区域": "Crops a (w,h) area starting from the top-left (x,y) corner.", # 新增
    "裁剪X": "Crop X", "裁剪Y": "Crop Y", "裁剪宽 W": "Width W", "裁剪高 H": "Height H",
    "批量旋转角度": "Rotation Angle", 
    "批量滤镜": "Filter", 
    
    # 动作与状态
    "🚀 开始处理图片": "🚀 Process Images",
    "正在处理": "Processing", # 新增
    "准备中...": "Preparing...", # 新增
    "正在处理: {}": "Processing: {}", 
    "处理中...": "Processing...",
    "请先上传图片文件！": "Please upload image files first!",
    "图片并行处理中，请稍候...": "Parallel processing images, please wait...",
    "正在使用 {} 核心加速处理...": "Processing with {} cores...", # 更新
    "处理完成！": "Processing Complete!", 
    "处理日志": "Processing Log",
    "❌ 未成功处理任何图片，请检查日志。": "❌ Failed to process any images. Please check the log.",
    "✅ 处理完成：{} / {}": "✅ Success: Processed {} / {} images.", 
    "⬇️ 下载全部结果": "⬇️ Download All Results",
    "处理中发生严重错误: {}": "A critical error occurred during processing: {}",

    # --- 信息查看选项卡 ---
    "🖼️ 图片信息查看": "🖼️ View Image Information",
    "上传图片以查看详细信息": "Upload an image to view its details",
    "图片预览": "Preview", "尺寸": "Dimensions", "文件大小": "File Size",
    "🎨 色彩与格式信息": "🎨 Color & Format Information",
    "模式": "Mode", "格式": "Format", "帧数": "Frame Count",
    "主色调": "Dominant Color", "RGB直方图": "RGB Histogram", 
    "📷 EXIF 元数据": "📷 EXIF Metadata",
    "分析图片时出错: {}": "Error analyzing image: {}",

    # --- 图片去重选项卡 ---
    "👯‍♀️ 交互式图片去重": "👯‍♀️ Interactive Duplicate Finder",
    "上传需要去重的图片(至少2张)": "Upload images to find duplicates (min. 2)",
    "查找重复图片": "Find Duplicates", 
    "正在查找重复图片...": "Searching for duplicate images...",
    "检测到 {} 组重复图片：请检查下面的选择，然后下载您需要的结果。": "Found {} groups of duplicate images. Please review the selections below and download your desired files.",
    "第": "Group", "组": "", 
    "选择要保留的图片": "Select image to keep", # 更新
    "无法读取": "Cannot Read",
    "准备下载包": "Prepare Download Packages",
    "⬇️ 下载保留的图片 ({})": "⬇️ Download Kept Images ({})",
    "⬇️ 下载多余的副本 ({})": "⬇️ Download Redundant Copies ({})",
    "✅ 经过扫描，未在您的上传中检测到重复图片。": "✅ Scan complete. No duplicate images were detected in your upload.",

    # --- 智能工具选项卡 ---
    "🔍 智能工具": "🔍 Smart Tools", # 新增
    "🪄 智能去背景 (Smart Background Removal)": "🪄 Smart Background Removal", # 新增
    "上传图片去除背景": "Upload images to remove background", # 更新
    "开始去背景": "Remove Background", 
    "正在去除背景...": "Removing backgrounds...",
    "去背景失败": "failed to remove background",
    "⬇️ 下载去背景结果": "⬇️ Download BG-Removed Results", # 新增
    "✍️ 批量OCR文字识别 (Batch OCR)": "✍️ Batch OCR", # 新增
    "上传图片进行OCR": "Upload images for OCR", 
    "开始OCR识别": "Start OCR",
    "识别结果": "Recognition Result", 

    # --- 处理记录选项卡 ---
    "🗂️ 最近处理结果预览": "🗂️ Preview of Last Results",
    "这里将展示“批量处理”选项卡最近一次成功运行的结果。": "This area shows the results from the last successful run in the 'Batch Process' tab.",
    "文件不存在": "File does not exist", # 新增
    "暂无最近处理结果。请先在“批量处理”中运行一次任务。": "No recent results. Please run a task in the 'Batch Process' tab first.",
}

def get_translator(lang="中文"):
    """
    Returns a translation function based on the selected language.
    """
    # Fallback for empty lang or other issues
    if lang != "English":
        return lambda text_key: text_key
    
    # Return the translator function for English
    return lambda text_key: lang_dict.get(text_key, text_key)