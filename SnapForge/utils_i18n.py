# utils_i18n.py - Enhanced for SnapForge UI

from typing import Dict, Callable

class I18NManager:
    """多语言管理器，支持动态翻译和UI一致性"""
    
    def __init__(self):
        self.translations = self._build_translation_dict()
        # 添加缺失的翻译项日志跟踪
        self._validate_translations()
        
    def _build_translation_dict(self) -> Dict[str, Dict[str, str]]:
        """构建完整的翻译字典"""
        return {
            "zh": self._chinese_translations(),
            "en": self._english_translations()
        }
    
    def _validate_translations(self):
        """验证中英文翻译的完整性，确保键值对匹配"""
        zh_keys = set(self.translations["zh"].keys())
        en_keys = set(self.translations["en"].keys())
        
        # 检查是否有缺失的翻译键
        if zh_keys != en_keys:
            missing_in_zh = en_keys - zh_keys
            missing_in_en = zh_keys - en_keys
            
            if missing_in_zh:
                print(f"警告: 中文翻译中缺少以下键: {missing_in_zh}")
            if missing_in_en:
                print(f"警告: 英文翻译中缺少以下键: {missing_in_en}")
    
    def _chinese_translations(self) -> Dict[str, str]:
        """中文翻译"""
        return {
            # 核心描述
            "高效、专业、美观的批量图片处理平台": "高效、专业、美观的批量图片处理平台",
            
            # 侧边栏与页脚
            "⚙️ 设置": "⚙️ 设置",
            "清理会话状态": "清理会话状态",
            "会话已重置！页面将刷新。": "会话已重置！页面将刷新。",
            "由": "由", 
            "设计与开发": "设计与开发",
            
            # 顶部横幅与链接
            "前往GitHub仓库": "前往GitHub仓库", 
            "反馈建议/提Issue": "反馈建议/提Issue",
            "反馈建议": "反馈建议",

            # 主标签页标题
            "批量处理": "批量处理", 
            "信息查看": "信息查看", 
            "图片去重": "图片去重",
            "处理记录": "处理记录",

            # 批量处理选项卡
            "📂 上传文件": "📂 上传文件",
            "上传图片": "上传图片",
            "🛠️ 图片处理参数": "🛠️ 图片处理参数",
            "重命名、格式转换与压缩": "重命名、格式转换与压缩",
            "启用重命名": "启用重命名",
            "前缀": "前缀", 
            "起始编号": "起始编号",
            "命名模板": "命名模板",
            "启用格式转换": "启用格式转换", 
            "目标格式": "目标格式",
            "启用质量压缩": "启用质量压缩", 
            "压缩质量": "压缩质量",
            "优化文件大小": "优化文件大小",
            "渐进式JPEG": "渐进式JPEG",
            
            # 高级参数
            "尺寸、水印与高级调整": "尺寸、水印与高级调整",
            "启用尺寸调整": "启用尺寸调整",
            "宽": "宽", 
            "高": "高",
            "模式": "模式",
            "适应边界": "适应边界",
            "裁剪填充": "裁剪填充",
            "拉伸": "拉伸",
            "仅缩小": "仅缩小", 
            "保留EXIF": "保留EXIF",
            "核心数": "核心数",
            "启用水印": "启用水印", 
            "内容": "内容", 
            "位置": "位置", 
            "字号": "字号",
            "字体颜色": "字体颜色",
            "透明度": "透明度",
            "水印边距": "水印边距",
            "启用裁剪": "启用裁剪", 
            "X": "X", "Y": "Y", "裁剪宽": "裁剪宽", "裁剪高": "裁剪高",
            "旋转角度": "旋转角度", 
            "滤镜": "滤镜",
            "启用边框": "启用边框",
            "边框宽度": "边框宽度",
            "边框颜色": "边框颜色",
            "边框圆角": "边框圆角",
            "亮度": "亮度",
            "对比度": "对比度",
            "饱和度": "饱和度",
            "锐度": "锐度",
            "启用特效调整": "启用特效调整",
            
            # 动作与状态
            "🚀 开始处理图片": "🚀 开始处理图片",
            "正在处理": "正在处理",
            "准备中...": "准备中...",
            "正在处理: {}": "正在处理: {}", 
            "处理中...": "处理中...",
            "图片并行处理中...": "图片并行处理中...",
            "使用 {} 核心加速...": "使用 {} 核心加速...",
            "处理完成！": "处理完成！",
            "❌ 未成功处理任何图片。": "❌ 未成功处理任何图片。",
            "✅ 处理完成：{} / {}": "✅ 处理完成：{} / {}", 
            "⬇️ 下载全部结果": "⬇️ 下载全部结果",
            "处理中发生严重错误: {}": "处理中发生严重错误: {}",
            "可能是内存不足。尝试减少处理的图片数量或降低图片分辨率。": "可能是内存不足。尝试减少处理的图片数量或降低图片分辨率。",
            "可能是磁盘空间不足。请清理磁盘空间后重试。": "可能是磁盘空间不足。请清理磁盘空间后重试。",
            "可能是文件权限问题。请检查应用程序是否有足够的权限。": "可能是文件权限问题。请检查应用程序是否有足够的权限。",
            "请尝试重新上传图片或刷新页面。如果问题持续存在，请联系支持团队。": "请尝试重新上传图片或刷新页面。如果问题持续存在，请联系支持团队。",
            
            # 信息查看选项卡
            "上传图片以查看信息": "上传图片以查看信息",
            "尺寸": "尺寸", "大小": "大小",
            "文件格式": "文件格式",
            "颜色模式": "颜色模式",
            "分辨率": "分辨率",
            "EXIF数据": "EXIF数据",
            "主要颜色": "主要颜色",
            "颜色分布": "颜色分布",
            "无EXIF数据": "无EXIF数据",
            "旋转信息": "旋转信息",
            "相机型号": "相机型号",
            "镜头型号": "镜头型号",
            "拍摄时间": "拍摄时间",
            "焦距": "焦距",
            "光圈": "光圈",
            "快门速度": "快门速度",
            "ISO": "ISO",

            # 图片去重选项卡
            "👯‍♀️ 图片去重": "👯‍♀️ 图片去重",
            "上传需要去重的图片(至少2张)": "上传需要去重的图片(至少2张)",
            "相似度阈值 (值越小越严格)": "相似度阈值 (值越小越严格)",
            "查找重复图片": "查找重复图片", 
            "正在查找...": "正在查找...",
            "✅ 未检测到重复图片。": "✅ 未检测到重复图片。",
            "检测到 {} 组重复图片。": "检测到 {} 组重复图片。",
            "第{}组重复图片 ({}张):": "第{}组重复图片 ({}张):",
            "选择保留图片": "选择保留图片",
            "仅查看缩略图": "仅查看缩略图",
            "快速预览模式": "快速预览模式",
            
            # 处理记录选项卡
            "结果预览": "结果预览",
            "文件不存在": "文件不存在",
            "暂无最近处理结果。": "暂无最近处理结果。",
            "上次处理时间": "上次处理时间",
            "处理数量": "处理数量",
            "成功数量": "成功数量",
            "处理参数": "处理参数",
            
            # 配置预设功能
            "配置预设": "配置预设",
            "保存当前配置": "保存当前配置",
            "预设名称": "预设名称",
            "加载预设": "加载预设",
            "删除预设": "删除预设",
            "预设已保存": "预设已保存",
            "预设不存在": "预设不存在",
            "预设已删除": "预设已删除",
            "请输入预设名称": "请输入预设名称",
            
            # 错误处理
            "跳过非图像文件: {}": "跳过非图像文件: {}",
            "跳过无效图像文件: {}": "跳过无效图像文件: {}",
            "处理文件 {} 时出错: {}": "处理文件 {} 时出错: {}",
            "请上传至少一张图片": "请上传至少一张图片",
            "请上传至少两张图片": "请上传至少两张图片",
            
            # 新增UI元素翻译
            "选择预设": "选择预设",
            "保存为新预设": "保存为新预设",
            "保存预设": "保存预设",
            "删除预设": "删除预设",
            "删除": "删除",
            "所有图片已处理完成，您可以查看处理结果或下载文件。": "所有图片已处理完成，您可以查看处理结果或下载文件。",
            "📸 处理结果": "📸 处理结果",
            "📦 下载处理结果": "📦 下载处理结果",
            "图片信息查看": "图片信息查看",
            "EXIF信息": "EXIF信息",
            "设备制造商": "设备制造商",
            "设备型号": "设备型号",
            "拍摄时间": "拍摄时间",
            "曝光时间": "曝光时间",
            "光圈值": "光圈值",
            "ISO": "ISO",
            "焦距": "焦距",
            "EXIF数据": "EXIF数据",
            "存在但无法解析详细内容": "存在但无法解析详细内容",
            "未能提取出可解析的EXIF标签": "未能提取出可解析的EXIF标签",
            "该图片不包含EXIF信息": "该图片不包含EXIF信息",
            "读取EXIF信息时出错": "读取EXIF信息时出错",
            "提示：某些图片格式或被处理过的图片可能没有EXIF信息": "提示：某些图片格式或被处理过的图片可能没有EXIF信息",
            "颜色统计": "颜色统计",
            "找到{}组重复图片": "找到{}组重复图片",
            "未发现重复图片": "未发现重复图片",
            "选择操作": "选择操作",
            "每组保留第一张，选择其余": "每组保留第一张，选择其余",
            "每组保留最大文件，选择其余": "每组保留最大文件，选择其余",
            "本组已选择": "本组已选择",
            "张图片": "张图片",
            "批量操作": "批量操作",
            "🗑️ 模拟删除所选": "🗑️ 模拟删除所选",
            "状态": "状态",
            "文件数量": "文件数量",
            "详情": "详情",
            "查看详情": "查看详情",
            "重新应用": "重新应用",
            "查看系统信息": "查看系统信息",
            "性能优化建议": "性能优化建议",
            "系统性能良好，暂无优化建议。": "系统性能良好，暂无优化建议。",
            "⚙️ 设置": "⚙️ 设置",
            
            # 批量图片处理相关
            "🖼️ 批量图片处理": "🖼️ 批量图片处理",
            "支持批量上传JPG、PNG、BMP、WebP格式图片，提供重命名、格式转换、尺寸调整、水印添加等丰富功能。大文件处理可能需要更长时间。": "支持批量上传JPG、PNG、BMP、WebP格式图片，提供重命名、格式转换、尺寸调整、水印添加等丰富功能。大文件处理可能需要更长时间。",
            "上传图片文件，查看详细的图片信息、EXIF数据和颜色统计。": "上传图片文件，查看详细的图片信息、EXIF数据和颜色统计。",
            
            # 性能监控页面
            "性能监控": "性能监控",
            "实时监控系统性能指标，包括内存使用、处理时间和系统资源。": "实时监控系统性能指标，包括内存使用、处理时间和系统资源。",
            "性能监控控制": "性能监控控制",
            "开始监控": "开始监控",
            "性能监控已启动": "性能监控已启动",
            "停止监控": "停止监控",
            "性能监控已停止": "性能监控已停止",
            "重置数据": "重置数据",
            "监控数据已重置": "监控数据已重置",
            "实时性能指标": "实时性能指标",
            "内存使用率": "内存使用率",
            "系统内存": "系统内存",
            "CPU使用率": "CPU使用率",
            "系统CPU": "系统CPU",
            "磁盘使用率": "磁盘使用率",
            "临时目录": "临时目录",
            "处理时间": "处理时间",
            "最近操作": "最近操作",
            "性能趋势": "性能趋势",
            "时间": "时间",
            "内存使用率%": "内存使用率%",
            "CPU使用率%": "CPU使用率%",
            "性能阈值设置": "性能阈值设置",
            "内存使用阈值 (%):": "内存使用阈值 (%):",
            "当内存使用超过此阈值时发出警告": "当内存使用超过此阈值时发出警告",
            "CPU使用阈值 (%):": "CPU使用阈值 (%):",
            "当CPU使用超过此阈值时发出警告": "当CPU使用超过此阈值时发出警告",
            "⚠️ 内存使用率过高！建议优化内存使用或增加系统内存。": "⚠️ 内存使用率过高！建议优化内存使用或增加系统内存。",
            "⚠️ CPU使用率过高！建议优化处理逻辑或减少并发任务。": "⚠️ CPU使用率过高！建议优化处理逻辑或减少并发任务。",
            "性能监控未启动，请点击'开始监控'按钮启动性能监控。": "性能监控未启动，请点击'开始监控'按钮启动性能监控。",
            "调试工具": "调试工具",
            "内存快照": "内存快照",
            "内存快照已创建": "内存快照已创建",
            "查看内存快照": "查看内存快照",
            "系统信息": "系统信息",
            "系统信息已获取": "系统信息已获取",
            "查看系统信息": "查看系统信息",
            
            # Missing translations from user feedback
            "批量图片处理图片去重检测": "批量图片处理图片去重检测",
            "上传多张图片，系统将自动检测相似或重复的图片。支持JPG、PNG、BMP、WebP格式。": "上传多张图片，系统将自动检测相似或重复的图片。支持JPG、PNG、BMP、WebP格式。",
            "查看历史处理记录，包括批量处理和图片去重的详细信息。": "查看历史处理记录，包括批量处理和图片去重的详细信息。",
            "暂无记录": "暂无记录",
            "完成图片处理或去重后，记录将显示在这里。": "完成图片处理或去重后，记录将显示在这里。",
            "完成图片处理后，记录将显示在这里。": "完成图片处理后，记录将显示在这里。",
        }
    
    def _english_translations(self) -> Dict[str, str]:
        """英文翻译 - 优化后的更自然、一致的英文表达"""
        return {
            # Core description
            "高效、专业、美观的批量图片处理平台": "Efficient, Professional & Beautiful Batch Image Processing Platform",
            
            # Sidebar & footer
            "⚙️ 设置": "⚙️ Settings",
            "清理会话状态": "Clear Session State",
            "会话已重置！页面将刷新。": "Session reset! Page will refresh.",
            "由": "by", 
            "设计与开发": "Designed & Developed",
            
            # Header banner & links
            "前往GitHub仓库": "Visit GitHub Repository", 
            "反馈建议/提Issue": "Feedback & Issues",
            "反馈建议": "Feedback",

            # Main tab titles
            "批量处理": "Batch Process", 
            "信息查看": "Image Info", 
            "图片去重": "Find Duplicates",
            "处理记录": "Processing History",

            # Batch processing tab
            "📂 上传文件": "📂 Upload Files",
            "上传图片": "Upload Images",
            "🛠️ 图片处理参数": "🛠️ Processing Parameters",
            "重命名、格式转换与压缩": "Rename, Convert & Compress",
            "启用重命名": "Enable Renaming",
            "前缀": "Prefix", 
            "起始编号": "Start Number",
            "命名模板": "Naming Template",
            "启用格式转换": "Enable Format Conversion", 
            "目标格式": "Target Format",
            "启用质量压缩": "Enable Quality Compression", 
            "压缩质量": "Quality",
            "优化文件大小": "Optimize File Size",
            "渐进式JPEG": "Progressive JPEG",
            
            # Advanced parameters
            "尺寸、水印与高级调整": "Resize, Watermark & Advanced",
            "启用尺寸调整": "Enable Resizing",
            "宽": "Width", 
            "高": "Height",
            "模式": "Mode",
            "适应边界": "Contain",
            "裁剪填充": "Cover",
            "拉伸": "Stretch",
            "仅缩小": "Downscale Only", 
            "保留EXIF": "Preserve EXIF",
            "核心数": "Processing Cores",
            "启用水印": "Enable Watermark", 
            "内容": "Watermark Text", 
            "位置": "Position", 
            "字号": "Font Size",
            "字体颜色": "Font Color",
            "透明度": "Opacity",
            "水印边距": "Margin",
            "启用裁剪": "Enable Cropping", 
            "X": "X", "Y": "Y", "裁剪宽": "Crop Width", "裁剪高": "Crop Height",
            "旋转角度": "Rotation Angle", 
            "滤镜": "Filter",
            "启用边框": "Enable Border",
            "边框宽度": "Border Width",
            "边框颜色": "Border Color",
            "边框圆角": "Border Radius",
            "亮度": "Brightness",
            "对比度": "Contrast",
            "饱和度": "Saturation",
            "锐度": "Sharpness",
            "启用特效调整": "Enable Effects",
            
            # Actions & status
            "🚀 开始处理图片": "🚀 Process Images",
            "正在处理": "Processing",
            "准备中...": "Preparing...",
            "正在处理: {}": "Processing: {}", 
            "处理中...": "Processing...",
            "图片并行处理中...": "Processing images in parallel...",
            "使用 {} 核心加速...": "Accelerating with {} cores...",
            "处理完成！": "Processing Complete!",
            "❌ 未成功处理任何图片。": "❌ No images processed successfully.",
            "✅ 处理完成：{} / {}": "✅ Completed: {} / {}", 
            "⬇️ 下载全部结果": "⬇️ Download All Results",
            "处理中发生严重错误: {}": "Critical error occurred: {}",
            "可能是内存不足。尝试减少处理的图片数量或降低图片分辨率。": "Memory shortage possible. Try reducing image count or resolution.",
            "可能是磁盘空间不足。请清理磁盘空间后重试。": "Insufficient disk space possible. Please free up space and try again.",
            "可能是文件权限问题。请检查应用程序是否有足够的权限。": "Permission issues possible. Please verify application permissions.",
            "请尝试重新上传图片或刷新页面。如果问题持续存在，请联系支持团队。": "Please try re-uploading images or refreshing the page. If the issue persists, contact support.",
            
            # Image info tab
            "上传图片以查看信息": "Upload image to view information",
            "尺寸": "Dimensions", "大小": "Size",
            "文件格式": "File Format",
            "颜色模式": "Color Mode",
            "分辨率": "Resolution",
            "EXIF数据": "EXIF Data",
            "主要颜色": "Dominant Colors",
            "颜色分布": "Color Distribution",
            "无EXIF数据": "No EXIF Data",
            "旋转信息": "Rotation Information",
            "相机型号": "Camera Model",
            "镜头型号": "Lens Model",
            "拍摄时间": "Capture Time",
            "焦距": "Focal Length",
            "光圈": "Aperture",
            "快门速度": "Shutter Speed",
            "ISO": "ISO",

            # Duplicate finder tab
            "👯‍♀️ 图片去重": "👯‍♀️ Find Duplicates",
            "上传需要去重的图片(至少2张)": "Upload images to find duplicates (min. 2 images)",
            "相似度阈值 (值越小越严格)": "Similarity Threshold (lower = stricter matching)",
            "查找重复图片": "Find Duplicates", 
            "正在查找...": "Searching...",
            "✅ 未检测到重复图片。": "✅ No duplicate images detected.",
            "检测到 {} 组重复图片。": "Found {} duplicate groups.",
            "第{}组重复图片 ({}张):": "Group {} ({} images):",
            "选择保留图片": "Select images to keep",
            "仅查看缩略图": "Thumbnails Only",
            "快速预览模式": "Quick Preview Mode",
            
            # Processing history tab
            "结果预览": "Result Preview",
            "文件不存在": "File not found",
            "暂无最近处理结果。": "No recent processing results.",
            "上次处理时间": "Last Processing Time",
            "处理数量": "Total Images",
            "成功数量": "Successfully Processed",
            "处理参数": "Processing Parameters",
            
            # Preset configuration
            "配置预设": "Configuration Presets",
            "保存当前配置": "Save Current Configuration",
            "预设名称": "Preset Name",
            "加载预设": "Load Preset",
            "删除预设": "Delete Preset",
            "预设已保存": "Preset Saved",
            "预设不存在": "Preset Does Not Exist",
            "预设已删除": "Preset Deleted",
            "请输入预设名称": "Please Enter Preset Name",
            
            # Error handling
            "跳过非图像文件: {}": "Skipping non-image file: {}",
            "跳过无效图像文件: {}": "Skipping invalid image file: {}",
            "处理文件 {} 时出错: {}": "Error processing file {}: {}",
            "请上传至少一张图片": "Please upload at least one image",
            "请上传至少两张图片": "Please upload at least two images",
            
            # New UI elements translations
            "选择预设": "Select Preset",
            "保存为新预设": "Save as New Preset",
            "保存预设": "Save Preset",
            "删除预设": "Delete Preset",
            "删除": "Delete",
            "所有图片已处理完成，您可以查看处理结果或下载文件。": "All images have been processed. You can view the results or download files.",
            "📸 处理结果": "📸 Processing Results",
            "📦 下载处理结果": "📦 Download Results",
            "图片信息查看": "Image Information",
            "EXIF信息": "EXIF Information",
            "设备制造商": "Manufacturer",
            "设备型号": "Model",
            "拍摄时间": "Capture Time",
            "曝光时间": "Exposure Time",
            "光圈值": "Aperture",
            "ISO": "ISO",
            "焦距": "Focal Length",
            "EXIF数据": "EXIF Data",
            "存在但无法解析详细内容": "Present but cannot parse details",
            "未能提取出可解析的EXIF标签": "Failed to extract parseable EXIF tags",
            "该图片不包含EXIF信息": "This image contains no EXIF information",
            "读取EXIF信息时出错": "Error reading EXIF information",
            "提示：某些图片格式或被处理过的图片可能没有EXIF信息": "Note: Some image formats or processed images may not have EXIF information",
            "颜色统计": "Color Statistics",
            "找到{}组重复图片": "Found {} duplicate groups",
            "未发现重复图片": "No duplicate images found",
            "选择操作": "Select Action",
            "每组保留第一张，选择其余": "Keep first in each group, select others",
            "每组保留最大文件，选择其余": "Keep largest file in each group, select others",
            "本组已选择": "Selected in this group",
            "张图片": "images",
            "批量操作": "Batch Operations",
            "🗑️ 模拟删除所选": "🗑️ Simulate Delete Selected",
            "状态": "Status",
            "文件数量": "File Count",
            "详情": "Details",
            "查看详情": "View Details",
            "重新应用": "Reapply",
            "查看系统信息": "View System Information",
            "性能优化建议": "Performance Optimization Suggestions",
            "系统性能良好，暂无优化建议。": "System performance is good, no optimization suggestions at this time.",
            "⚙️ 设置": "⚙️ Settings",
            
            # Batch image processing related
            "🖼️ 批量图片处理": "🖼️ Batch Image Processing",
            "支持批量上传JPG、PNG、BMP、WebP格式图片，提供重命名、格式转换、尺寸调整、水印添加等丰富功能。大文件处理可能需要更长时间。": "Supports batch upload of JPG, PNG, BMP, WebP format images with rich features including renaming, format conversion, size adjustment, watermark addition, etc. Large file processing may take longer.",
            "上传图片文件，查看详细的图片信息、EXIF数据和颜色统计。": "Upload image files to view detailed image information, EXIF data, and color statistics.",
            
            # Performance monitoring page
            "性能监控": "Performance Monitoring",
            "实时监控系统性能指标，包括内存使用、处理时间和系统资源。": "Real-time monitoring of system performance metrics including memory usage, processing time, and system resources.",
            "性能监控控制": "Performance Monitoring Control",
            "开始监控": "Start Monitoring",
            "性能监控已启动": "Performance monitoring started",
            "停止监控": "Stop Monitoring",
            "性能监控已停止": "Performance monitoring stopped",
            "重置数据": "Reset Data",
            "监控数据已重置": "Monitoring data reset",
            "实时性能指标": "Real-time Performance Metrics",
            "内存使用率": "Memory Usage",
            "系统内存": "System Memory",
            "CPU使用率": "CPU Usage",
            "系统CPU": "System CPU",
            "磁盘使用率": "Disk Usage",
            "临时目录": "Temporary Directory",
            "处理时间": "Processing Time",
            "最近操作": "Recent Operations",
            "性能趋势": "Performance Trends",
            "时间": "Time",
            "内存使用率%": "Memory Usage %",
            "CPU使用率%": "CPU Usage %",
            "性能阈值设置": "Performance Threshold Settings",
            "内存使用阈值 (%):": "Memory Usage Threshold (%):",
            "当内存使用超过此阈值时发出警告": "Issue warning when memory usage exceeds this threshold",
            "CPU使用阈值 (%):": "CPU Usage Threshold (%):",
            "当CPU使用超过此阈值时发出警告": "Issue warning when CPU usage exceeds this threshold",
            "⚠️ 内存使用率过高！建议优化内存使用或增加系统内存。": "⚠️ Memory usage too high! Consider optimizing memory usage or increasing system memory.",
            "⚠️ CPU使用率过高！建议优化处理逻辑或减少并发任务。": "⚠️ CPU usage too high! Consider optimizing processing logic or reducing concurrent tasks.",
            "性能监控未启动，请点击'开始监控'按钮启动性能监控。": "Performance monitoring not started. Click 'Start Monitoring' to begin.",
            "调试工具": "Debug Tools",
            "内存快照": "Memory Snapshot",
            "内存快照已创建": "Memory snapshot created",
            "查看内存快照": "View Memory Snapshot",
            "系统信息": "System Information",
            "系统信息已获取": "System information retrieved",
            "查看系统信息": "View System Information",
            
            # Missing translations from user feedback
            "批量图片处理图片去重检测": "Batch Image Processing & Duplicate Detection",
            "上传多张图片，系统将自动检测相似或重复的图片。支持JPG、PNG、BMP、WebP格式。": "Upload multiple images, the system will automatically detect similar or duplicate images. Supports JPG, PNG, BMP, WebP formats.",
            "查看历史处理记录，包括批量处理和图片去重的详细信息。": "View processing history, including detailed information about batch processing and duplicate detection.",
            "暂无记录": "No records yet",
            "完成图片处理或去重后，记录将显示在这里。": "Records will appear here after image processing or duplicate detection is completed.",
            "完成图片处理后，记录将显示在这里。": "Records will appear here after image processing is completed.",
        }
    
    def get_translator(self, lang: str = "中文") -> Callable[[str], str]:
        """获取翻译函数 - 优化的语言检测逻辑"""
        # 健壮的语言代码映射
        lang = lang.lower() if isinstance(lang, str) else lang
        lang_code = "zh" if lang in ["中文", "chinese", "zh", "zh-cn", "zh-hans"] else "en"
        
        def translator(text_key: str) -> str:
            """翻译函数 - 支持格式化字符串"""
            try:
                translated = self.translations[lang_code].get(text_key, text_key)
                return translated
            except Exception as e:
                # 错误处理：返回原始文本以确保应用不会崩溃
                print(f"Translation error for '{text_key}': {e}")
                return text_key
        
        return translator

# 全局实例
_i18n_manager = I18NManager()

def get_translator(lang: str = "中文") -> Callable[[str], str]:
    """获取翻译函数（兼容旧接口）"""
    # 直接传递语言参数，内部已处理语言代码映射
    return _i18n_manager.get_translator(lang)