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