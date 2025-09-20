import os
import io
import sys
import logging
import multiprocessing
import importlib.resources
import time
import functools
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import StrEnum, auto
from typing import (
    Optional, Dict, Any, Tuple, List, Set, Callable, Sequence, 
    TypeVar, Generic, Union, cast
)

# Pillow and external libraries
from PIL import (
    Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, 
    ImageOps, UnidentifiedImageError, ImageChops, ImageStat
)
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt
import numpy as np

# 定义Pillow库的常量
Resampling = getattr(Image, "Resampling", Image)
Transpose = getattr(Image, "Transpose", Image)
BICUBIC = getattr(Resampling, "BICUBIC", Image.BICUBIC)
LANCZOS = getattr(Resampling, "LANCZOS", Image.LANCZOS)
ROTATE_90 = getattr(Transpose, "ROTATE_90", Image.ROTATE_90)

# 兼容旧版Pillow的别名
_Resampling = Resampling
_Transpose = Transpose
_BICUBIC = BICUBIC
_LANCZOS = LANCZOS

# =====================
# 0. 性能监控与缓存装饰器
# =====================

T = TypeVar('T')

def timed(func):
    """性能监控装饰器，记录函数执行时间"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger = logging.getLogger(__name__)
        logger.debug(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to run")
        return result
    return wrapper

def memoize(func):
    """简单的内存缓存装饰器，适用于纯函数"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 创建可哈希的键
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # 添加清除缓存的方法
    setattr(wrapper, 'clear_cache', lambda: cache.clear())
    return wrapper

# =====================
# 1. 类型与配置 (已升级)
# =====================

class ResizeMode(StrEnum):
    CONTAIN = auto()
    COVER = auto()
    STRETCH = auto()

class FilterType(StrEnum):
    """滤镜类型枚举"""
    GRAYSCALE = auto()  # 灰度
    SHARPEN = auto()    # 锐化
    BLUR = auto()       # 模糊
    CONTOUR = auto()    # 轮廓
    EMBOSS = auto()     # 浮雕
    EDGE = auto()       # 边缘检测
    ENHANCE = auto()    # 增强对比度
    SEPIA = auto()      # 棕褐色调
    INVERT = auto()     # 反色
    POSTERIZE = auto()  # 色调分离

# --- 分解后的配置类，职责更单一 ---

@dataclass(slots=True)
class RenameConfig:
    """重命名相关配置"""
    prefix: str = "image"
    start_number: int = 1
    naming_template: str = "{prefix}_{counter:04d}"

    def __post_init__(self):
        if self.start_number < 0:
            raise ValueError("start_number must be non-negative")

@dataclass(slots=True)
class ConvertConfig:
    """格式转换相关配置
    
    属性:
        format: 目标格式 (jpg, png, webp等)
        quality: 质量参数 (1-100)
        progressive: 是否使用渐进式JPEG
        optimize: 是否优化文件大小
    """
    format: str
    quality: int = 85
    progressive: bool = False
    optimize: bool = True

    def __post_init__(self):
        self.format = self.format.lower().lstrip('.')
        if not (0 <= self.quality <= 100):
            raise ValueError("quality must be between 0 and 100")

@dataclass(slots=True)
class ResizeConfig:
    """缩放相关配置
    
    属性:
        width: 目标宽度
        height: 目标高度
        mode: 缩放模式 (CONTAIN, COVER, STRETCH)
        only_shrink: 是否只缩小不放大
        resampling: 重采样方法 (默认为LANCZOS)
    """
    width: int = 800
    height: int = 600
    mode: ResizeMode = ResizeMode.CONTAIN
    only_shrink: bool = True
    resampling: int = getattr(Image, "Resampling", Image).LANCZOS
    
    def __post_init__(self):
        """验证输入参数的有效性"""
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")
        # 验证模式是否为有效的ResizeMode
        if not isinstance(self.mode, ResizeMode):
            raise ValueError(f"Invalid resize mode: {self.mode}")

@dataclass(slots=True)
class CropConfig:
    """裁剪相关配置
    
    属性:
        x: 左上角X坐标
        y: 左上角Y坐标
        w: 裁剪宽度
        h: 裁剪高度
        smart_crop: 是否使用智能裁剪(基于图像内容)
    """
    x: int
    y: int
    w: int
    h: int
    smart_crop: bool = False

    def __post_init__(self):
        if self.w <= 0 or self.h <= 0:
            raise ValueError("Crop dimensions must be positive")
        if self.x < 0 or self.y < 0:
            raise ValueError("Crop coordinates cannot be negative")

@dataclass(slots=True)
class RotateConfig:
    """旋转相关配置
    
    属性:
        angle: 旋转角度(度)
        expand: 是否扩展画布以适应旋转后的图像
        fill_color: 填充颜色(None表示透明)
    """
    angle: int = 0
    expand: bool = True
    fill_color: Optional[Tuple[int, int, int]] = None

@dataclass(slots=True)
class FilterConfig:
    """滤镜相关配置
    
    属性:
        type: 滤镜类型
        enhance_factor: 增强因子(用于某些滤镜)
        blur_radius: 模糊半径(用于模糊滤镜)
        posterize_bits: 色调分离位数(用于posterize滤镜)
    """
    type: FilterType
    enhance_factor: float = 1.5
    blur_radius: float = 2.0
    posterize_bits: int = 2

    def __post_init__(self):
        if self.enhance_factor <= 0:
            raise ValueError("enhance_factor must be positive")
        if self.blur_radius <= 0:
            raise ValueError("blur_radius must be positive")
        if not (1 <= self.posterize_bits <= 8):
            raise ValueError("posterize_bits must be between 1 and 8")

@dataclass(slots=True)
class WatermarkConfig:
    """水印相关配置
    
    属性:
        text: 水印文本
        font_path: 字体路径(None表示使用默认字体)
        size: 字体大小
        color: 颜色(RGBA)
        position: 位置("bottom-right", "center", "top-left"等)
        margin: 边距
        rotation: 水印旋转角度
        opacity: 水印不透明度(0-1)
        image_path: 图片水印路径(优先于文本水印)
    """
    text: str
    font_path: Optional[str] = None
    size: int = 32
    color: Tuple[int, int, int, int] = (255, 255, 255, 128)
    position: str = "bottom-right"
    margin: int = 20
    rotation: float = 0.0
    opacity: float = 0.5
    image_path: Optional[str] = None

@dataclass(slots=True)
class BorderConfig:
    """边框相关配置
    
    属性:
        width: 边框宽度
        color: 边框颜色(RGB)
        radius: 圆角半径(0表示无圆角)
    """
    width: int = 5
    color: Tuple[int, int, int] = (255, 255, 255)
    radius: int = 0

    def __post_init__(self):
        if self.width < 0:
            raise ValueError("Border width must be non-negative")
        if self.radius < 0:
            raise ValueError("Border radius must be non-negative")

@dataclass(slots=True)
class EffectsConfig:
    """特效相关配置
    
    属性:
        brightness: 亮度调整因子(1.0表示不变)
        contrast: 对比度调整因子(1.0表示不变)
        saturation: 饱和度调整因子(1.0表示不变)
        sharpness: 锐度调整因子(1.0表示不变)
    """
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0
    sharpness: float = 1.0

    def __post_init__(self):
        for attr, value in asdict(self).items():
            if value <= 0:
                raise ValueError(f"{attr} must be positive")

# --- 主配置类 (通过组合构建) ---
@dataclass(kw_only=True, slots=True)
class ProcessConfig:
    """处理配置主类，组合了所有处理选项
    
    属性:
        rename_config: 重命名配置
        convert_config: 格式转换配置
        resize_config: 尺寸调整配置
        crop_config: 裁剪配置
        rotate_config: 旋转配置
        filter_config: 滤镜配置
        watermark_config: 水印配置
        border_config: 边框配置
        effects_config: 特效配置
        preserve_metadata: 是否保留元数据
        num_processes: 处理进程数
    """
    rename_config: Optional[RenameConfig] = None
    convert_config: Optional[ConvertConfig] = None
    resize_config: Optional[ResizeConfig] = None
    crop_config: Optional[CropConfig] = None
    rotate_config: Optional[RotateConfig] = None
    filter_config: Optional[FilterConfig] = None
    watermark_config: Optional[WatermarkConfig] = None
    border_config: Optional[BorderConfig] = None
    effects_config: Optional[EffectsConfig] = None

    preserve_metadata: bool = True
    num_processes: int = field(default_factory=lambda: max(2, os.cpu_count() or 2))

    def __post_init__(self):
        if self.num_processes < 1:
            raise ValueError("num_processes must be >= 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典，用于序列化"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if hasattr(value, '__dataclass_fields__'):
                    result[key] = asdict(value)
                else:
                    result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessConfig':
        """从字典创建配置，用于反序列化"""
        config_map = {
            'rename_config': RenameConfig,
            'convert_config': ConvertConfig,
            'resize_config': ResizeConfig,
            'crop_config': CropConfig,
            'rotate_config': RotateConfig,
            'filter_config': FilterConfig,
            'watermark_config': WatermarkConfig,
            'border_config': BorderConfig,
            'effects_config': EffectsConfig
        }
        
        kwargs = {}
        for key, value in data.items():
            if key in config_map and value is not None:
                if isinstance(value, dict):
                    # 处理枚举类型
                    if key == 'resize_config' and 'mode' in value:
                        value['mode'] = ResizeMode(value['mode'])
                    elif key == 'filter_config' and 'type' in value:
                        value['type'] = FilterType(value['type'])
                    kwargs[key] = config_map[key](**value)
                else:
                    kwargs[key] = value
            else:
                kwargs[key] = value
                
        return cls(**kwargs)


# =====================
# 2. 日志与常量 (已升级)
# =====================
FORMAT_MAPPING = {
    "jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "bmp": "BMP",
    "gif": "GIF", "tiff": "TIFF", "webp": "WEBP", "heic": "HEIF",
    "avif": "AVIF"
}

# 支持的输入格式
SUPPORTED_INPUT_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp", ".heic"}

# 支持的输出格式
SUPPORTED_OUTPUT_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

def get_logger(name: str = "image_processor"):
    """
    获取一个logger实例。库代码不应配置处理器(handler)，这应由应用层代码负责。
    """
    return logging.getLogger(name)

logger = get_logger(__name__)

class ProcessingError(Exception):
    """图片处理错误基类"""
    pass

class UnsupportedFormatError(ProcessingError):
    """不支持的格式错误"""
    pass

class ProcessingTimeoutError(ProcessingError):
    """处理超时错误"""
    pass


# =====================
# 3. 核心处理逻辑 (已重构)
# =====================

@timed
def process_image(
    src_path: Path, dest_dir: Path, config: ProcessConfig, *, counter: int
) -> Tuple[str, str, Optional[str]]:
    """单张图片处理函数，处理流程由ProcessConfig驱动
    
    Args:
        src_path: 源图片路径
        dest_dir: 目标目录路径
        config: 处理配置
        counter: 计数器(用于命名)
        
    Returns:
        Tuple[str, str, Optional[str]]: (原文件名, 状态, 结果路径或错误信息)
    """
    try:
        # 检查文件格式是否支持
        original_ext = src_path.suffix.lower()
        if original_ext not in SUPPORTED_INPUT_FORMATS:
            raise UnsupportedFormatError(f"Unsupported input format: {original_ext}")
            
        # 获取图片基本信息
        with Image.open(src_path) as temp_img:
            width, height = temp_img.size
            format_name = temp_img.format or "Unknown"

        # --- 文件名处理 ---
        original_stem = src_path.stem
        
        if config.rename_config:
            rc = config.rename_config
            # 扩展命名上下文，增加日期和时间
            from datetime import datetime
            now = datetime.now()
            naming_context = {
                "prefix": rc.prefix, 
                "counter": counter + rc.start_number - 1,
                "original_filename": original_stem, 
                "width": width, 
                "height": height,
                "date": now.strftime("%Y%m%d"),
                "time": now.strftime("%H%M%S"),
                "format": format_name.lower()
            }
            base_name = rc.naming_template.format(**naming_context)
        else:
            base_name = original_stem
        
        # 确定输出格式
        final_ext = f".{config.convert_config.format}" if config.convert_config else original_ext
        if final_ext not in SUPPORTED_OUTPUT_FORMATS:
            raise UnsupportedFormatError(f"Unsupported output format: {final_ext}")
            
        dest_path = dest_dir / f"{base_name}{final_ext}"
        
        # 确保目标目录存在
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理图片
        _process_image_logic(src_path, dest_path, final_ext, config)
        return src_path.name, "success", str(dest_path)
    except UnsupportedFormatError as e:
        logger.warning(f"Format error for {src_path.name}: {e}")
        return src_path.name, "format_error", str(e)
    except Exception as e:
        logger.error(f"Failed to process {src_path.name}: {e}", exc_info=True)
        return src_path.name, "error", f"{type(e).__name__}: {e}"

def _process_image_logic(src_path: Path, dest_path: Path, target_ext: str, config: ProcessConfig):
    """图片处理的核心逻辑，按顺序应用各种处理操作"""
    with Image.open(src_path) as img:
        # 保留原始模式，仅在必要时转换
        original_mode = img.mode
        has_alpha = 'A' in img.getbands()
        
        # 保存元数据
        metadata = {}
        if config.preserve_metadata:
            for key in img.info:
                if key in ('exif', 'icc_profile', 'xmp'):
                    metadata[key] = img.info[key]
        
        # 转换CMYK和索引模式为RGB(A)
        if original_mode in ('CMYK', 'P'):
            img = img.convert("RGBA" if has_alpha else "RGB")
        
        # 按顺序应用各种处理，传递更精确的配置对象
        if config.crop_config and config.crop_config.w > 0:
            img = _apply_crop_logic(img, config.crop_config)
        if config.rotate_config and config.rotate_config.angle != 0:
            img = _apply_rotate_logic(img, config.rotate_config)
        if config.resize_config:
            img = _resize_image_logic(img, config.resize_config)
        if config.effects_config:
            img = _apply_effects_logic(img, config.effects_config)
        if config.filter_config:
            img = _apply_filter_logic(img, config.filter_config)
        if config.border_config and config.border_config.width > 0:
            img = _apply_border_logic(img, config.border_config)
        if config.watermark_config:
            img = _apply_watermark_logic(img, config.watermark_config)
        
        # 保存图片
        save_params = {}
        if config.convert_config:
            save_params["quality"] = config.convert_config.quality
            save_params["progressive"] = config.convert_config.progressive
            save_params["optimize"] = config.convert_config.optimize
        
        _save_image_logic(img, dest_path, target_ext, metadata, save_params)

def _save_image_logic(img: Image.Image, dest_path: Path, target_ext: str, 
                     metadata: Dict[str, Any], save_params: Dict[str, Any]):
    """保存图片逻辑，处理不同格式的特殊需求"""
    ext = target_ext.lower().lstrip('.')
    
    # 设置基本保存参数
    format_name = FORMAT_MAPPING.get(ext, "JPEG")
    params = {"format": format_name}
    
    # 合并用户提供的保存参数
    params.update(save_params)
    
    # 根据格式设置特定参数
    quality = params.get("quality", 85)
    quality = int(max(1, min(100, quality)))
    
    if ext in ("jpg", "jpeg", "webp"):
        params["quality"] = quality
    elif ext == "png":
        params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
        if "quality" in params:
            del params["quality"]  # PNG不使用quality参数
    
    # 添加元数据
    for key, value in metadata.items():
        params[key] = value
    
    # 处理颜色模式兼容性
    if ext in ["jpg", "jpeg", "bmp"] and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
        
    # 确保目标目录存在
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存图片
    try:
        img.save(dest_path, **params)
    except (ValueError, OSError, Exception) as e:
        # 扩展异常捕获范围，捕获所有可能的异常
        logger.warning(f"Failed to save with advanced parameters: {e}. Trying with basic parameters.")
        try:
            basic_params = {"format": format_name}
            if ext in ("jpg", "jpeg", "webp"):
                basic_params["quality"] = quality
            img.save(dest_path, **basic_params)
        except Exception as e2:
            # 如果基本参数也失败，记录错误并抛出异常
            logger.error(f"Failed to save image even with basic parameters: {e2}")
            raise ProcessingError(f"Cannot save image: {e2}") from e2

def _apply_crop_logic(img: Image.Image, config: CropConfig) -> Image.Image:
    """应用裁剪效果，支持智能裁剪"""
    if config.smart_crop and config.w > 0 and config.h > 0:
        return _smart_crop(img, config.w, config.h)
    else:
        # 确保裁剪区域在图像范围内
        width, height = img.size
        x = min(config.x, width - 1)
        y = min(config.y, height - 1)
        w = min(config.w, width - x)
        h = min(config.h, height - y)
        return img.crop((x, y, x + w, y + h))

def _smart_crop(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """智能裁剪，保留图像中最重要的部分"""
    width, height = img.size
    
    # 如果目标尺寸大于原图，直接返回原图
    if target_width >= width and target_height >= height:
        return img
    
    # 获取正确的Resampling常量
    Resampling = getattr(Image, "Resampling", Image)
    Transpose = getattr(Image, "Transpose", Image)
    
    # 计算裁剪区域
    if width / height > target_width / target_height:
        # 原图更宽，需要裁剪宽度
        new_width = int(height * target_width / target_height)
        offset = _find_best_offset(img, new_width)
        crop_box = (offset, 0, offset + new_width, height)
    else:
        # 原图更高，需要裁剪高度
        new_height = int(width * target_height / target_width)
        offset = _find_best_offset(img.transpose(_ROTATE_90), new_height)
        crop_box = (0, offset, width, offset + new_height)
    
    # 裁剪并调整大小
    cropped = img.crop(crop_box)
    return cropped.resize((target_width, target_height), _LANCZOS)

def _find_best_offset(img: Image.Image, target_size: int) -> int:
    """找到最佳裁剪偏移量，基于图像内容分析"""
    # 转换为灰度图进行分析
    gray = img.convert("L")
    width, height = gray.size
    
    # 如果目标尺寸大于等于原图尺寸，不需要裁剪
    if target_size >= width:
        return 0
    
    # 计算每个可能的裁剪窗口的熵值
    entropies: List[float] = []
    for i in range(width - target_size + 1):
        window = gray.crop((i, 0, i + target_size, height))
        stat = ImageStat.Stat(window)
        # 使用标准差作为熵的近似值
        entropies.append(stat.stddev[0])
    
    # 返回熵值最高的窗口的起始位置
    return entropies.index(max(entropies))

def _apply_rotate_logic(img: Image.Image, config: RotateConfig) -> Image.Image:
    """应用旋转效果，支持填充颜色
    Args:
        img: 要旋转的图片对象
        config: 旋转配置
        
    Returns:
        旋转后的图片对象
    """
    # 处理填充颜色
    fill_color = config.fill_color
    if fill_color is None and 'A' in img.getbands():
        # 对于带透明通道的图像，默认使用透明填充
        fill_color = (0, 0, 0, 0)
    
    return img.rotate(
        config.angle, 
        expand=config.expand, 
        fillcolor=fill_color,
        resample=BICUBIC  # 使用已定义的常量
    )

def _resize_image_logic(img: Image.Image, config: ResizeConfig) -> Image.Image:
    """调整图片尺寸逻辑
    Args:
        img: 要调整的图片对象
        config: 调整配置
        
    Returns:
        调整后的图片对象
    """
    orig_w, orig_h = img.size
    if config.only_shrink and orig_w <= config.width and orig_h <= config.height:
        return img

    size = (config.width, config.height)
    resample_filter = LANCZOS  # 使用已定义的常量
    match config.mode:
        case ResizeMode.CONTAIN: 
            img.thumbnail(size, resample_filter)
            return img
        case ResizeMode.COVER: 
            return ImageOps.fit(img, size, resample_filter, bleed=0.0)
        case ResizeMode.STRETCH: 
            return img.resize(size, resample_filter)
    return img

def _apply_watermark_logic(img: Image.Image, config: WatermarkConfig) -> Image.Image:
    if not config.text: return img
    base = img.convert("RGBA") if img.mode != "RGBA" else img.copy()
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_path = config.font_path or _get_bundled_font_path()
    try:
        font = ImageFont.truetype(font_path, config.size) if font_path else ImageFont.load_default()
    except (IOError, OSError):
        logger.warning(f"Could not load font '{font_path}'. Using Pillow's default font.")
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), config.text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    positions = {
        "bottom-right": (base.width - tw - config.margin, base.height - th - config.margin),
        "bottom-left": (config.margin, base.height - th - config.margin),
        "top-right": (base.width - tw - config.margin, config.margin),
        "top-left": (config.margin, config.margin),
        "center": ((base.width - tw) // 2, (base.height - th) // 2),
    }
    x, y = positions.get(config.position, positions["bottom-right"])
    draw.text((x, y), config.text, font=font, fill=config.color)
    return Image.alpha_composite(base, overlay)

def _apply_effects_logic(img: Image.Image, config: EffectsConfig) -> Image.Image:
    """应用图像特效（亮度、对比度、饱和度、锐度）"""
    if not config:
        return img
        
    # 保存透明通道
    has_alpha = 'A' in img.getbands()
    alpha: Optional[Image.Image] = img.getchannel('A') if has_alpha else None
    
    # 转换为RGB处理
    rgb_img = img.convert("RGB") if has_alpha else img
    
    # 应用各种增强效果
    if config.brightness != 1.0:
        enhancer = ImageEnhance.Brightness(rgb_img)
        rgb_img = enhancer.enhance(config.brightness)
        
    if config.contrast != 1.0:
        enhancer = ImageEnhance.Contrast(rgb_img)
        rgb_img = enhancer.enhance(config.contrast)
        
    if config.saturation != 1.0:
        enhancer = ImageEnhance.Color(rgb_img)
        rgb_img = enhancer.enhance(config.saturation)
        
    if config.sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(rgb_img)
        rgb_img = enhancer.enhance(config.sharpness)
    
    # 恢复透明通道
    if has_alpha and alpha is not None:
        rgb_img.putalpha(alpha)
        
    return rgb_img

def _apply_border_logic(img: Image.Image, config: BorderConfig) -> Image.Image:
    """应用边框效果"""
    if not config or config.width <= 0:
        return img
        
    # 创建带边框的新图像
    width, height = img.size
    new_width = width + 2 * config.width
    new_height = height + 2 * config.width
    
    # 确定模式和背景色
    mode = img.mode
    if mode == 'P':
        mode = 'RGBA' if 'transparency' in img.info else 'RGB'
    
    # 创建带边框的新图像
    if mode == 'RGBA':
        # 对于透明图像，创建带透明边框的图像
        border_color = config.color + (255,)  # 添加完全不透明的alpha通道
        bordered = Image.new(mode, (new_width, new_height), (0, 0, 0, 0))
    else:
        border_color = config.color
        bordered = Image.new(mode, (new_width, new_height), border_color)
    
    # 粘贴原图到中心
    bordered.paste(img, (config.width, config.width))
    
    # 如果需要圆角
    if config.radius > 0:
        # 创建圆角蒙版
        mask = Image.new('L', (new_width, new_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (new_width-1, new_height-1)], 
                              radius=config.radius, fill=255)
        
        # 应用圆角蒙版
        if mode == 'RGBA':
            # 对于RGBA模式，我们需要分别处理RGB和A通道
            r, g, b, a = bordered.split()
            a = ImageChops.multiply(a, mask)
            bordered = Image.merge('RGBA', (r, g, b, a))
        else:
            # 对于RGB模式，创建一个新的透明图像
            result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
            result.paste(bordered, mask=mask)
            bordered = result
    
    return bordered

def _apply_filter_logic(img: Image.Image, config: FilterConfig) -> Image.Image:
    """应用滤镜效果"""
    if not config:
        return img
        
    # 灰度滤镜直接处理
    if config.type == FilterType.GRAYSCALE: 
        return img.convert("L")
    
    # 保存透明通道
    has_alpha = 'A' in img.getbands()
    alpha: Optional[Image.Image] = img.getchannel('A') if has_alpha else None
    
    # 转换为RGB处理
    rgb_img = img.convert("RGB") if has_alpha else img
    
    # 应用标准滤镜
    filter_map = {
        FilterType.SHARPEN: ImageFilter.SHARPEN, 
        FilterType.BLUR: ImageFilter.GaussianBlur(radius=config.blur_radius),
        FilterType.CONTOUR: ImageFilter.CONTOUR, 
        FilterType.EMBOSS: ImageFilter.EMBOSS,
        FilterType.EDGE: ImageFilter.FIND_EDGES
    }
    
    if config.type in filter_map:
        filtered = rgb_img.filter(filter_map[config.type])
    elif config.type == FilterType.ENHANCE:
        enhancer = ImageEnhance.Contrast(rgb_img)
        filtered = enhancer.enhance(config.enhance_factor)
    elif config.type == FilterType.SEPIA:
        # 棕褐色调滤镜
        sepia_data = np.array([
            [ 0.393, 0.769, 0.189],
            [ 0.349, 0.686, 0.168],
            [ 0.272, 0.534, 0.131]
        ])
        # 转换为numpy数组处理
        rgb_array = np.array(rgb_img)
        sepia_array = np.dot(rgb_array, sepia_data.T)
        # 裁剪值到0-255范围
        sepia_array = np.clip(sepia_array, 0, 255).astype(np.uint8)
        filtered = Image.fromarray(sepia_array)
    elif config.type == FilterType.INVERT:
        # 反色滤镜
        filtered = ImageOps.invert(rgb_img)
    elif config.type == FilterType.POSTERIZE:
        # 色调分离滤镜
        filtered = ImageOps.posterize(rgb_img, config.posterize_bits)
    else:
        return img
    
    # 恢复透明通道
    if has_alpha and alpha is not None:
        filtered.putalpha(alpha)
        
    return filtered


# =====================
# 4. 主调度器 (已重构)
# =====================

class ImageProcessor:
    def __init__(self):
        self.logger = get_logger("ImageProcessor")

    def batch_process(
        self, files: Sequence[str], output_dir: str, config: ProcessConfig,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[int, int, List[str]]:
        if not files:
            self.logger.info("No files to process.")
            if progress_callback: progress_callback(1.0, "No files to process")
            return 0, 0, []
        output_path = Path(output_dir); output_path.mkdir(parents=True, exist_ok=True)
        start_num = config.rename_config.start_number if config.rename_config else 1
        tasks = [(Path(file), output_path, config, start_num + i) for i, file in enumerate(files)]
        total = len(tasks); results: List[str] = []
        use_mp = (config.num_processes > 1 and total > 1)
        processor = self._process_multiprocess if use_mp else self._process_serial
        try:
            processor(tasks, results, config, total, progress_callback)
        except Exception as e:
            self.logger.error(f"Processing failed: {e}, falling back to serial mode.", exc_info=True)
            results.clear()
            self._process_serial(tasks, results, config, total, progress_callback)
        return len(results), total, sorted(results)

    def _process_multiprocess(self, tasks, results, config, total, progress_callback):
        self.logger.info(f"Using multiprocessing with {config.num_processes} processes.")
        # 限制进程数，避免内存溢出
        max_processes = min(config.num_processes, os.cpu_count() or 2, 8)
        # 根据操作系统选择合适的多进程上下文
        if sys.platform == 'win32':
            ctx = multiprocessing.get_context("spawn")
        else:
            ctx = multiprocessing.get_context("fork")
            
        # 添加内存监控
        try:
            import psutil
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024
            self.logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
            # 如果内存使用超过系统内存的70%，减少进程数
            if process.memory_percent() > 70:
                max_processes = max(1, max_processes // 2)
                self.logger.warning(f"High memory usage detected. Reducing processes to {max_processes}")
        except ImportError:
            self.logger.debug("psutil not available, skipping memory monitoring")
            
        with ctx.Pool(processes=max_processes) as pool:
            # 使用chunksize参数优化大量小任务的处理
            chunksize = max(1, len(tasks) // (max_processes * 4))
            # 先收集所有结果，再在主进程中统一处理，避免并发问题
            process_results = list(pool.imap_unordered(_mp_worker, tasks, chunksize=chunksize))
            for i, result in enumerate(process_results):
                self._handle_result(result, results)
                if progress_callback: 
                    progress_callback((i + 1) / total, result[0])

    def _process_serial(self, tasks, results, config, total, progress_callback):
        self.logger.info(f"Using single-threaded serial processing for {total} files.")
        for i, task in enumerate(tasks):
            result = _mp_worker(task)
            self._handle_result(result, results)
            if progress_callback: progress_callback((i + 1) / total, task[0].name)

    def _handle_result(self, result: Tuple[str, str, Optional[str]], results: list):
        orig, status, data = result
        if status == "success" and data:
            self.logger.info(f"✅ Success: {orig} -> {Path(data).name}")
            results.append(data)
        else:
            self.logger.error(f"❌ Failed: {orig}, Reason: {data}")

def _mp_worker(args: Tuple[Path, Path, ProcessConfig, int]) -> Tuple[str, str, Optional[str]]:
    src, out_dir, cfg, ctr = args
    return process_image(src, out_dir, cfg, counter=ctr)

# =====================
# 5. 工具函数 (重大改进)
# =====================

class _BKTreeNode:
    def __init__(self, item: Tuple[str, imagehash.ImageHash]):
        self.item = item
        self.children: Dict[int, _BKTreeNode] = {}

class _BKTree:
    """A BK-Tree for efficient approximate searching of perceptual hashes."""
    def __init__(self, dist_fn: Callable[[Any, Any], int]):
        self.dist_fn = dist_fn
        self.root: Optional[_BKTreeNode] = None

    def add(self, item: Tuple[str, imagehash.ImageHash]):
        if not self.root: self.root = _BKTreeNode(item); return
        node = self.root
        while True:
            dist = self.dist_fn(item[1], node.item[1])
            if dist not in node.children: node.children[dist] = _BKTreeNode(item); break
            node = node.children[dist]
            
    def search(self, item: Tuple[str, imagehash.ImageHash], threshold: int) -> List[Tuple[str, imagehash.ImageHash]]:
        if not self.root: return []
        candidates, found = [self.root], []
        while candidates:
            node = candidates.pop()
            dist = self.dist_fn(item[1], node.item[1])
            if dist <= threshold: found.append(node.item)
            low, high = dist - threshold, dist + threshold
            candidates.extend(child for d, child in node.children.items() if low <= d <= high)
        return found

def find_duplicate_images(file_paths: List[str], threshold: int = 8) -> List[List[str]]:
    """使用BK-Tree高效查找相似图片，避免O(n^2)的暴力比较。"""
    # 验证阈值参数
    if threshold < 0:
        logger.warning(f"Invalid threshold value: {threshold}, using default value 8")
        threshold = 8
    elif threshold > 64:  # 哈希通常是64位，所以最大距离是64
        logger.warning(f"Threshold too large: {threshold}, using maximum value 64")
        threshold = 64
        
    logger.info("Hashing images for duplicate search...")
    hashes: List[Tuple[str, imagehash.ImageHash]] = []
    for path in file_paths:
        try:
            with Image.open(path) as img: 
                # 转换为灰度图像以提高哈希一致性
                gray_img = img.convert('L')
                hashes.append((path, imagehash.phash(gray_img)))
        except (FileNotFoundError, UnidentifiedImageError) as e:
            logger.warning(f"Cannot hash {path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error hashing {path}: {e}")
            
    if not hashes: return []
    logger.info(f"Building BK-Tree and searching with {len(hashes)} hashes...")
    tree = _BKTree(dist_fn=lambda h1, h2: h1 - h2)
    for h in hashes: tree.add(h)
    groups: List[List[str]] = []
    visited: Set[str] = set()
    for path, d_hash in hashes:
        if path in visited: continue
        matches = tree.search((path, d_hash), threshold)
        if len(matches) > 1:
            group_paths = sorted([m[0] for m in matches])
            groups.append(group_paths)
            visited.update(group_paths)
    return groups

def get_exif_data(image_path: str) -> Dict[str, Any]:
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd in ("0th", "Exif", "GPS", "1st", "thumbnail"):
            ifd_data = exif_dict.get(ifd)
            if not isinstance(ifd_data, dict): continue
            for tag, value in ifd_data.items():
                tag_info = piexif.TAGS.get(ifd, {}).get(tag, {"name": f"Unknown_{hex(tag)}"})
                tag_name = tag_info.get("name")
                if isinstance(value, bytes):
                    try: value = value.strip(b'\x00').decode('utf-8', errors='ignore')
                    except UnicodeDecodeError: value = repr(value)
                exif_data[f"{ifd}:{tag_name}"] = str(value)
        return exif_data
    except (FileNotFoundError, piexif.InvalidImageDataError, ValueError) as e:
        logger.warning(f"Could not read EXIF from {image_path}: {e}"); return {}

def get_image_main_color(image_path: str) -> Tuple[Optional[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
    try:
        ct = ColorThief(image_path)
        return ct.get_color(quality=1), ct.get_palette(color_count=6, quality=1)
    except (FileNotFoundError, IOError, ValueError, OSError) as e:
        # 只捕获预期的异常类型，避免隐藏未知错误
        logger.warning(f"Color analysis failed for {image_path}: {e}")
        return None, []
    except Exception as e:
        logger.error(f"Unexpected error in color analysis for {image_path}: {e}", exc_info=True)
        return None, []

def plot_image_histogram(image_path: str) -> Optional[io.BytesIO]:
    """生成图像的RGB直方图
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        包含直方图PNG图像的BytesIO对象，如果失败则返回None
    """
    fig = None
    buf = None
    rgb_img = None
    
    try:
        # 使用上下文管理器确保图像文件被正确关闭
        with Image.open(image_path) as img:
            # 转换为RGB并复制到内存中，避免文件句柄依赖
            rgb_img = img.convert('RGB').copy()
            
        # 设置matplotlib样式
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        colors, names = ('r', 'g', 'b'), ('Red', 'Green', 'Blue')
        
        # 绘制每个通道的直方图
        for i, color in enumerate(colors):
            histogram = rgb_img.getchannel(i).histogram()
            ax.plot(histogram, color=color, alpha=0.8, label=names[i])
            
        # 设置图表属性
        ax.set_title("RGB Histogram", fontsize=10)
        ax.set_xlim((0, 256))
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")
        ax.legend(fontsize='small')
        ax.grid(True)
        fig.tight_layout()
        
        # 保存到内存缓冲区
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        
        # 返回缓冲区，调用者负责关闭
        return buf
        
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.warning(f"Histogram creation failed for {image_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating histogram for {image_path}: {e}", exc_info=True)
        return None
    finally:
        # 确保所有资源被正确释放
        if fig is not None: 
            plt.close(fig)
        
        # 如果出现异常且buf已创建但未返回，关闭它
        if buf is not None and sys.exc_info()[0] is not None:
            try:
                buf.close()
            except Exception:
                pass
                
        # 确保清理任何matplotlib资源
        plt.clf()
        
        # 显式删除大型对象以帮助垃圾回收
        if rgb_img is not None:
            del rgb_img



def select_best_image_in_group(group_paths: List[str]) -> Optional[str]:
    best_path, max_res, max_size = None, -1, -1
    for path_str in group_paths:
        try:
            path = Path(path_str); img = Image.open(path); res = img.width * img.height
            size = path.stat().st_size
            if res > max_res or (res == max_res and size > max_size):
                max_res, max_size, best_path = res, size, path_str
        except (FileNotFoundError, UnidentifiedImageError):
            logger.warning(f"Could not read image for best selection: {path_str}")
    return best_path

def _get_bundled_font_path(font_name: str = "DejaVuSans.ttf") -> Optional[str]:
    """重大改进：使用 importlib.resources 来安全、可移植地加载项目内的字体文件。"""
    try:
        font_ref = importlib.resources.files('assets.fonts').joinpath(font_name)
        with importlib.resources.as_file(font_ref) as font_path:
            if font_path.exists():
                return str(font_path)
            else:
                logger.warning(f"Bundled font '{font_name}' not found. Searching system fonts.")
                return _find_system_font()
    except (ModuleNotFoundError, FileNotFoundError):
        logger.warning(f"Bundled font package 'assets.fonts' not found. Searching system fonts.")
        return _find_system_font()

def _find_system_font() -> Optional[str]:
    """尝试在系统中查找可用的字体"""
    # 常见系统字体路径
    common_fonts = [
        # Windows 字体
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        # macOS 字体
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Geneva.ttf",
        # Linux 字体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    # 尝试找到一个可用的字体
    for font_path in common_fonts:
        if os.path.exists(font_path):
            logger.info(f"Found system font: {font_path}")
            return font_path
            
    logger.warning("No system fonts found. Pillow's default font will be used.")
    return None

# =====================
# 6. 示例用法 (作为脚本运行时)
# =====================
if __name__ == '__main__':
    # 1. 配置日志记录 (这是应用程序的责任，而不是库的责任)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    logger.info("Image Processor V2 - Example Usage")
    INPUT_DIR, OUTPUT_DIR = Path("demo_input"), Path("demo_output")
    INPUT_DIR.mkdir(exist_ok=True); OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 2. 创建演示文件
    dummy_files = []
    for i in range(5):
        try:
            f = INPUT_DIR / f"test_{i}.png"; dummy_files.append(str(f))
            Image.new('RGB', (200 + i*20, 150 + i*20), (i*10, i*20, i*30)).save(f)
        except Exception as e: logger.error(f"Failed to create dummy file: {e}")

    # 3. 使用新的分层配置
    if dummy_files:
        p_config = ProcessConfig(
            rename_config=RenameConfig(prefix="demo", start_number=1),
            convert_config=ConvertConfig(format="jpeg", quality=80),
            resize_config=ResizeConfig(width=150, height=150, mode=ResizeMode.CONTAIN),
            watermark_config=WatermarkConfig(text="© Upgraded", size=16),
            filter_config=FilterConfig(type=FilterType.SHARPEN)
        )
        
        # 4. 运行批处理
        processor = ImageProcessor()
        s, t, res = processor.batch_process(dummy_files, str(OUTPUT_DIR), p_config)
        logger.info(f"Batch processing complete. {s}/{t} files processed into {OUTPUT_DIR.resolve()}")

        # 5. 演示高效的重复查找
        dummy_files.append(dummy_files[0]) # 添加一个重复项
        logger.info("\n--- Demonstrating efficient duplicate search ---")
        groups = find_duplicate_images(dummy_files, threshold=2)
        logger.info(f"Found {len(groups)} duplicate group(s): {groups}")