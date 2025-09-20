# utils_i18n.py - Enhanced for SnapForge UI

from typing import Dict, Callable, Optional

class I18NManager:
    """多语言管理器，支持动态翻译和UI一致性"""
    
    def __init__(self):
        self.translations = self._build_translation_dict()
        
    def _build_translation_dict(self) -> Dict[str, Dict[str, str]]:
        """构建完整的翻译字典"""
        return {
            "zh": self._chinese_translations(),
            "en": self._english_translations()
        }
    
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
            "批量极速处理": "批量处理", 
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
            "启用裁剪": "启用裁剪", 
            "X": "X", "Y": "Y", "裁剪宽": "裁剪宽", "裁剪高": "裁剪高",
            "旋转角度": "旋转角度", 
            "滤镜": "滤镜",
            
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

            # 信息查看选项卡
            "上传图片以查看信息": "上传图片以查看信息",
            "尺寸": "尺寸", "大小": "大小",

            # 图片去重选项卡
            "👯‍♀️ 图片去重": "👯‍♀️ 图片去重",
            "上传需要去重的图片(至少2张)": "上传需要去重的图片(至少2张)",
            "相似度阈值 (值越小越严格)": "相似度阈值 (值越小越严格)",
            "查找重复图片": "查找重复图片", 
            "正在查找...": "正在查找...",
            "✅ 未检测到重复图片。": "✅ 未检测到重复图片。",
            "检测到 {} 组重复图片。": "检测到 {} 组重复图片。",



            # 处理记录选项卡
            "结果预览": "结果预览",
            "文件不存在": "文件不存在",
            "暂无最近处理结果。": "暂无最近处理结果。",
        }
    
    def _english_translations(self) -> Dict[str, str]:
        """英文翻译"""
        return {
            # Core description
            "高效、专业、美观的批量图片处理平台": "An efficient, professional, and beautiful platform for image processing.",
            
            # Sidebar & footer
            "⚙️ 设置": "⚙️ Settings",
            "清理会话状态": "Clear Session State",
            "会话已重置！页面将刷新。": "Session reset! Page will refresh.",
            "由": "by", 
            "设计与开发": "Designed & Developed",
            
            # Header banner & links
            "前往GitHub仓库": "Go to GitHub Repository", 
            "反馈建议/提Issue": "Feedback & Issues",
            "反馈建议": "Feedback",

            # Main tab titles
            "批量处理": "Batch Process", 
            "信息查看": "Image Info", 
            "图片去重": "Find Duplicates",
            "处理记录": "History",

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
            "保留EXIF": "Keep EXIF",
            "核心数": "Cores",
            "启用水印": "Enable Watermark", 
            "内容": "Text", 
            "位置": "Position", 
            "字号": "Font Size",
            "启用裁剪": "Enable Cropping", 
            "X": "X", "Y": "Y", "裁剪宽": "Crop Width", "裁剪高": "Crop Height",
            "旋转角度": "Rotation Angle", 
            "滤镜": "Filter",
            
            # Actions & status
            "🚀 开始处理图片": "🚀 Process Images",
            "正在处理": "Processing",
            "准备中...": "Preparing...",
            "正在处理: {}": "Processing: {}", 
            "处理中...": "Processing...",
            "图片并行处理中...": "Parallel processing images...",
            "使用 {} 核心加速...": "Using {} cores...",
            "处理完成！": "Processing Complete!",
            "❌ 未成功处理任何图片。": "❌ Failed to process any images.",
            "✅ 处理完成：{} / {}": "✅ Processed {} / {}", 
            "⬇️ 下载全部结果": "⬇️ Download All Results",
            "处理中发生严重错误: {}": "Critical error: {}",

            # Image info tab
            "上传图片以查看信息": "Upload image to view info",
            "尺寸": "Dimensions", "大小": "Size",

            # Duplicate finder tab
            "👯‍♀️ 图片去重": "👯‍♀️ Find Duplicates",
            "上传需要去重的图片(至少2张)": "Upload images to find duplicates (min 2)",
            "相似度阈值 (值越小越严格)": "Similarity Threshold (lower = stricter)",
            "查找重复图片": "Find Duplicates", 
            "正在查找...": "Searching...",
            "✅ 未检测到重复图片。": "✅ No duplicates found.",
            "检测到 {} 组重复图片。": "Found {} duplicate groups.",



            # History tab
            "结果预览": "Result Preview",
            "文件不存在": "File not found",
            "暂无最近处理结果。": "No recent results.",
        }
    
    def get_translator(self, lang: str = "中文") -> Callable[[str], str]:
        """获取翻译函数"""
        # 修复语言选择逻辑，确保正确处理"English"和"中文"
        lang_code = "zh" if lang in ["中文", "Chinese"] else "en"
        
        def translator(text_key: str) -> str:
            return self.translations[lang_code].get(text_key, text_key)
        
        return translator

# 全局实例
_i18n_manager = I18NManager()

def get_translator(lang: str = "中文") -> Callable[[str], str]:
    """获取翻译函数（兼容旧接口）"""
    # 处理app.py中传入的"English"或"中文"
    if lang == "English":
        return _i18n_manager.get_translator("English")
    return _i18n_manager.get_translator(lang)