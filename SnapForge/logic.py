# logic_upgraded.py
import os
import io
import logging
import multiprocessing
from pathlib import Path
from dataclasses import dataclass, field, InitVar
from enum import Enum
from typing import Optional, Dict, Any, Tuple, List, TypedDict, Set

# Pillow and related imaging libraries
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, UnidentifiedImageError
import imagehash
import piexif

# Analysis and other utility libraries
from colorthief import ColorThief
import matplotlib.pyplot as plt
import pytesseract
from rembg import remove

# ==========================================================
# 1. 类型定义与枚举 (Type Definitions & Enums)
# ==========================================================

class ResizeMode(str, Enum):
    CONTAIN = "contain"
    COVER = "cover"
    STRETCH = "stretch"

class FilterType(str, Enum):
    GRAYSCALE = "grayscale"
    SHARPEN = "sharpen"
    BLUR = "blur"
    CONTOUR = "contour"
    EMBOSS = "emboss"
    EDGE = "edge"
    ENHANCE = "enhance"

class CropParams(TypedDict):
    x: int
    y: int
    w: int
    h: int

class WatermarkParams(TypedDict):
    text: str
    font: Optional[str]
    size: int
    color: Tuple[int, int, int, int]
    pos: str
    margin: Optional[int]

# ==========================================================
# 2. 全局常量与日志 (Constants & Logging)
# ==========================================================

FORMAT_MAPPING = {
    ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP",
    ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP"
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==========================================================
# 3. 配置数据类 (Upgraded Dataclass)
# ==========================================================
@dataclass
class ProcessConfig:
    """
    封装所有图像处理参数的数据类，并通过初始化后验证保证配置的有效性。

    Attributes:
        rename_enabled: 是否启用重命名。
        prefix: 重命名后的文件名前缀。
        start_number: 重命名计数器的起始数字。
        naming_template: 文件名格式化模板。
        convert_format: 目标转换格式，如 'png' 或 '.jpg'。
        quality: 图像保存质量 (0-100)。
        resize_enabled: 是否启用缩放。
        resize_width: 目标宽度。
        resize_height: 目标高度。
        resize_mode: 缩放模式。
        resize_only_shrink: 是否仅在图像大于目标尺寸时才缩小。
        crop_params: 裁剪参数。
        rotate_angle: 旋转角度。
        filter_type: 滤镜类型。
        watermark_params: 水印参数。
        watermark_margin: 全局默认水印边距。
        enhance_factor: 'enhance' 滤镜的对比度增强因子。
        preserve_metadata: 是否保留EXIF元数据。
        num_processes: 使用的CPU进程数。
        tesseract_cmd: Tesseract可执行文件的路径。
    """
    # --- Renaming & Naming Template ---
    rename_enabled: bool = False
    prefix: Optional[str] = "image"
    start_number: int = 1
    naming_template: str = "{prefix}_{counter:04d}"

    # --- Conversion & Compression ---
    convert_format: Optional[str] = None
    quality: Optional[int] = 85

    # --- Resizing ---
    resize_enabled: bool = False
    resize_width: int = 800
    resize_height: int = 600
    resize_mode: ResizeMode = ResizeMode.CONTAIN
    resize_only_shrink: bool = True

    # --- Transformations & Effects ---
    crop_params: Optional[CropParams] = None
    rotate_angle: int = 0
    filter_type: Optional[FilterType] = None
    watermark_params: Optional[WatermarkParams] = None
    
    watermark_margin: int = 20
    enhance_factor: float = 1.5

    # --- Advanced & Metadata ---
    preserve_metadata: bool = True
    num_processes: Optional[int] = field(default_factory=lambda: max(1, os.cpu_count() - 1 if os.cpu_count() else 1))
    tesseract_cmd: Optional[str] = None

    def __post_init__(self):
        """在初始化后验证配置参数的有效性。"""
        if self.quality is not None and not (0 <= self.quality <= 100):
            raise ValueError("Config Error: 'quality' must be between 0 and 100.")
        if self.num_processes < 1:
            raise ValueError("Config Error: 'num_processes' must be at least 1.")
        if self.start_number < 0:
            raise ValueError("Config Error: 'start_number' cannot be negative.")
        if self.enhance_factor <= 0:
            raise ValueError("Config Error: 'enhance_factor' must be positive.")
        if self.convert_format:
            self.convert_format = self.convert_format.lower().lstrip('.')

# ==========================================================
# 4. 核心处理工作流 (Core Processing Workflow)
# ==========================================================
def _process_single_image_worker(args: Tuple[str, str, int, ProcessConfig]) -> Tuple[str, str, Optional[str]]:
    """
    为多进程设计的独立工作函数。处理单个图像并返回结果。
    
    Args:
        args: 包含 (源路径, 输出目录, 计数器, 配置对象) 的元组。

    Returns:
        一个元组 (原始文件名, 状态, 结果路径或错误信息)。
    """
    src_path_str, out_dir_str, counter, config = args
    src_path = Path(src_path_str)
    original_filename = src_path.name
    
    try:
        # Pre-flight check to get dimensions for naming without fully decoding
        with Image.open(src_path) as temp_img:
            width, height = temp_img.size

        naming_context = {
            "prefix": config.prefix,
            "counter": counter,
            "original_filename": src_path.stem,
            "width": width,
            "height": height,
        }
        
        base_name = config.naming_template.format(**naming_context) if config.rename_enabled else src_path.stem
        original_ext = src_path.suffix.lower()
        final_ext = f".{config.convert_format}" if config.convert_format else original_ext
        
        new_filename = f"{base_name}{final_ext}"
        dest_path = Path(out_dir_str) / new_filename

        _process_image_logic(src_path, dest_path, final_ext, config)
        
        return (original_filename, "success", str(dest_path))

    except Exception as e:
        logger.error(f"Failed to process {original_filename}: {e}", exc_info=True)
        return (original_filename, "error", f"{type(e).__name__}: {e}")

def _process_image_logic(src_path: Path, dest_path: Path, target_ext: str, config: ProcessConfig):
    """核心的、单一图像处理逻辑。"""
    with Image.open(src_path) as img:
        # Ensure image is in a processable mode (e.g., convert CMYK to RGB)
        if img.mode == 'CMYK':
            img = img.convert('RGB')
        
        exif_data = img.info.get("exif") if config.preserve_metadata and "exif" in img.info else None

        if config.crop_params and config.crop_params.get('w', 0) > 0:
            cp = config.crop_params
            img = img.crop((cp["x"], cp["y"], cp["x"] + cp["w"], cp["y"] + cp["h"]))

        if config.rotate_angle != 0:
            img = img.rotate(config.rotate_angle, expand=True, resample=Image.Resampling.BICUBIC)

        if config.resize_enabled:
            img = _resize_image_logic(img, config)
        
        if config.filter_type:
            img = _apply_filter_logic(img, config)

        if config.watermark_params:
            img = _apply_watermark_logic(img, config)
        
        _save_image_logic(img, dest_path, target_ext, exif_data, config.quality)

def _save_image_logic(img: Image.Image, dest_path: Path, target_ext: str, exif_data: Optional[bytes], quality: Optional[int]):
    """保存图像，根据格式应用正确的压缩参数。"""
    save_params = {"format": FORMAT_MAPPING.get(target_ext, "JPEG")}
    if quality is not None:
        quality = int(max(1, min(100, quality)))
        if target_ext in (".jpg", ".jpeg", ".webp"):
            save_params["quality"] = quality
        elif target_ext == ".png":
            # Convert 0-100 quality to 0-9 compress_level (higher quality = lower compression)
            save_params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
    
    if exif_data:
        save_params["exif"] = exif_data
    
    # Ensure mode is compatible with target format
    if target_ext in [".jpg", ".jpeg", ".bmp"] and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, **save_params)

def _resize_image_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    """根据配置对图像进行缩放。"""
    orig_w, orig_h = img.size
    if config.resize_only_shrink and orig_w <= config.resize_width and orig_h <= config.resize_height:
        return img

    size = (config.resize_width, config.resize_height)
    resample_filter = Image.Resampling.LANCZOS

    if config.resize_mode is ResizeMode.CONTAIN:
        img.thumbnail(size, resample_filter)
        return img
    elif config.resize_mode is ResizeMode.COVER:
        return ImageOps.fit(img, size, resample_filter, bleed=0.0)
    elif config.resize_mode is ResizeMode.STRETCH:
        return img.resize(size, resample_filter)
    return img

def _apply_watermark_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    """在图像上应用文本水印。"""
    wp = config.watermark_params
    if not wp or not wp.get("text"): 
        return img

    # Use a copy to avoid modifying the original image object in the pipeline
    base_image = img.convert("RGBA") if img.mode != "RGBA" else img.copy()
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_path = wp.get("font")
    font_size = wp.get("size", 32)
    color = wp.get("color", (255, 255, 255, 128))
    pos = wp.get("pos", "bottom-right")
    margin = wp.get("margin", config.watermark_margin)
    text = wp["text"]
    
    font_to_try = font_path or _get_bundled_font_path()
    try:
        font = ImageFont.truetype(font_to_try, font_size) if font_to_try else ImageFont.load_default(size=font_size)
    except (IOError, TypeError):
        logger.warning(f"Could not load font '{font_to_try}'. Falling back to default.")
        font = ImageFont.load_default(size=font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    positions = {
        "bottom-right": (base_image.width - text_width - margin, base_image.height - text_height - margin),
        "bottom-left": (margin, base_image.height - text_height - margin),
        "top-right": (base_image.width - text_width - margin, margin),
        "top-left": (margin, margin),
        "center": ((base_image.width - text_width) // 2, (base_image.height - text_height) // 2)
    }
    x, y = positions.get(pos, positions["bottom-right"])
    draw.text((x, y), text, font=font, fill=color)
    return Image.alpha_composite(base_image, overlay)

def _apply_filter_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    """对图像应用指定的滤镜效果。"""
    filter_type = config.filter_type
    if not filter_type: return img
    if filter_type is FilterType.GRAYSCALE: return img.convert("L")

    # Preserve alpha channel if it exists
    has_alpha = 'A' in img.getbands()
    if has_alpha:
        alpha = img.getchannel('A')
        rgb_img = img.convert("RGB")
    else:
        rgb_img = img

    filter_map = {
        FilterType.SHARPEN: ImageFilter.SHARPEN, FilterType.BLUR: ImageFilter.BLUR,
        FilterType.CONTOUR: ImageFilter.CONTOUR, FilterType.EMBOSS: ImageFilter.EMBOSS,
        FilterType.EDGE: ImageFilter.FIND_EDGES
    }
    
    if filter_type in filter_map:
        filtered_img = rgb_img.filter(filter_map[filter_type])
    elif filter_type is FilterType.ENHANCE:
        enhancer = ImageEnhance.Contrast(rgb_img)
        filtered_img = enhancer.enhance(config.enhance_factor)
    else:
        return img # Should not happen if FilterType enum is used
    
    if has_alpha:
        filtered_img.putalpha(alpha)
        
    return filtered_img

# ==========================================================
# 5. 主调度器类 (Main Processor Class)
# ==========================================================
class ImageProcessor:
    """
    主图像处理器，负责调度批处理任务。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def batch_process(self,
                      files: List[str],
                      output_dir: str,
                      config: ProcessConfig,
                      progress_callback=None) -> Tuple[int, int, List[str]]:
        """
        对一组图像文件进行批处理。

        Args:
            files: 要处理的文件路径列表。
            output_dir: 保存结果的目录。
            config: 包含所有处理参数的ProcessConfig对象。
            progress_callback: 一个可选的回调函数，用于报告进度。
                它将被调用，参数为 (进度百分比(0.0-1.0), 当前处理的文件名)。

        Returns:
            一个元组 (成功处理的数量, 文件总数, 成功处理的文件路径列表)。
        """
        if not files:
            self.logger.info("No files to process.")
            if progress_callback: progress_callback(1.0, "No files to process")
            return 0, 0, []

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        tasks = [(file_path, output_dir, config.start_number + i, config) for i, file_path in enumerate(files)]
        
        total_files = len(tasks)
        successful_paths = []
        
        use_multiprocessing = (config.num_processes > 1 and total_files > 1)

        if use_multiprocessing:
            self.logger.info(f"Starting multiprocessing mode ({config.num_processes} processes) for {total_files} files...")
            try:
                # Use "spawn" context for better cross-platform compatibility
                ctx = multiprocessing.get_context("spawn")
                with ctx.Pool(processes=config.num_processes) as pool:
                    results_iterator = pool.imap_unordered(_process_single_image_worker, tasks)
                    for i, result in enumerate(results_iterator):
                        self._handle_result(result, successful_paths)
                        if progress_callback: progress_callback((i + 1) / total_files, result[0])
            except Exception as e:
                self.logger.error(f"Multiprocessing pool failed: {e}. Falling back to single-threaded mode.", exc_info=True)
                successful_paths.clear() # Clear partial results
                self._process_serially(tasks, successful_paths, progress_callback)
        else:
            self.logger.info(f"Starting single-threaded mode for {total_files} files...")
            self._process_serially(tasks, successful_paths, progress_callback)
        
        return len(successful_paths), total_files, sorted(successful_paths)

    def _process_serially(self, tasks: List[Tuple], successful_paths: List[str], progress_callback=None):
        total_files = len(tasks)
        for i, task in enumerate(tasks):
            result = _process_single_image_worker(task)
            self._handle_result(result, successful_paths)
            if progress_callback: progress_callback((i + 1) / total_files, task[0])

    def _handle_result(self, result: Tuple[str, str, Optional[str]], paths: List[str]):
        original_filename, status, data = result
        if status == "success":
            self.logger.info(f"✅ Success: {original_filename} -> {Path(data).name}")
            paths.append(data)
        else:
            self.logger.error(f"❌ Failed: {original_filename}, Reason: {data}")

# ==========================================================
# 6. 独立的工具函数 (Standalone Utility Functions)
# ==========================================================

def find_duplicate_images(file_paths: List[str], threshold: int = 8) -> List[List[str]]:
    """
    查找列表中的重复或高度相似的图像。

    使用感知哈希 (phash) 算法。此算法复杂度为 O(N^2)，适用于中等规模的集合。
    对于非常大的数据集（>10,000张图片），可能需要更高级的数据结构（如VP-Tree）。

    Args:
        file_paths: 图像文件路径列表。
        threshold: 哈希差异阈值。值越小，要求图片越相似。默认为8。

    Returns:
        一个列表，其中每个子列表包含一组重复或相似的图片路径。
    """
    path_to_hashes: Dict[str, imagehash.ImageHash] = {}
    for path in file_paths:
        try:
            with Image.open(path) as img:
                path_to_hashes[path] = imagehash.phash(img)
        except (FileNotFoundError, UnidentifiedImageError) as e:
            logger.warning(f"Cannot calculate hash for {path}: {e}")
            continue

    paths = list(path_to_hashes.keys())
    groups = []
    visited_indices: Set[int] = set()

    for i in range(len(paths)):
        if i in visited_indices:
            continue

        current_group = {paths[i]}
        for j in range(i + 1, len(paths)):
            if j in visited_indices:
                continue
            
            hash_diff = path_to_hashes[paths[i]] - path_to_hashes[paths[j]]
            if hash_diff <= threshold:
                current_group.add(paths[j])
        
        if len(current_group) > 1:
            groups.append(sorted(list(current_group)))
            # Mark all members of the found group as visited
            for path_in_group in current_group:
                try:
                    # Find index and mark as visited to avoid redundant checks
                    idx = paths.index(path_in_group)
                    visited_indices.add(idx)
                except ValueError:
                    continue # Should not happen

    return groups


def get_exif_data(image_path: str) -> Dict[str, Any]:
    """
    从图像文件中提取并解析EXIF元数据。

    Args:
        image_path: 图像文件路径。

    Returns:
        一个包含可读EXIF标签和值的字典。
    """
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd_name in ("0th", "Exif", "GPS", "1st", "thumbnail"):
            ifd_data = exif_dict.get(ifd_name)
            if not isinstance(ifd_data, dict): continue
            for tag, value in ifd_data.items():
                tag_info = piexif.TAGS.get(ifd_name, {}).get(tag, {"name": f"UnknownTag_{hex(tag)}"})
                tag_name = tag_info.get("name")
                
                if isinstance(value, bytes):
                    try:
                        # Attempt to decode, falling back to more robust encodings or repr
                        value = value.strip(b'\x00').decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            value = value.strip(b'\x00').decode('latin-1')
                        except UnicodeDecodeError:
                            value = repr(value)
                
                exif_data[f"{ifd_name}:{tag_name}"] = value
        return exif_data
    except (FileNotFoundError, piexif.InvalidImageDataError, ValueError) as e:
        logger.warning(f"Could not read EXIF data from {image_path}: {e}")
        return {}

def get_image_main_color(image_path: str) -> Tuple[Optional[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
    """
    获取图像的主色调和调色板。

    Args:
        image_path: 图像文件路径。

    Returns:
        一个元组 (主色调RGB, 调色板颜色列表)。
    """
    try:
        ct = ColorThief(image_path)
        dominant_color = ct.get_color(quality=1)
        palette = ct.get_palette(color_count=6, quality=1)
        return dominant_color, palette
    except Exception as e:
        logger.warning(f"Could not get main color from {image_path}: {e}")
        return None, []

def plot_image_histogram(image_path: str) -> Optional[io.BytesIO]:
    """
    为图像生成RGB颜色直方图并返回其内存中的PNG数据。

    Args:
        image_path: 图像文件路径。

    Returns:
        一个包含PNG图像数据的BytesIO对象，或在失败时返回None。
    """
    fig = None
    try:
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
        
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        colors = ('r', 'g', 'b')
        channel_names = ('Red', 'Green', 'Blue')

        for i, color in enumerate(colors):
            histogram_data = rgb_img.getchannel(i).histogram()
            ax.plot(histogram_data, color=color, alpha=0.8, label=channel_names[i])
            
        ax.set_title("RGB Histogram", fontsize=10)
        ax.set_xlim([0, 256])
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")
        ax.legend(fontsize='small')
        ax.grid(True)
        fig.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return buf
    except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
        logger.warning(f"Could not create histogram for {image_path}: {e}")
        return None
    finally:
        # Crucial step: ensure matplotlib figure is closed to free memory
        if fig:
            plt.close(fig)

def ocr_image(image_path: str, lang: str = "chi_sim+eng", tesseract_cmd: Optional[str] = None) -> str:
    """
    对图片进行OCR文字识别。

    Args:
        image_path: 图像文件路径。
        lang: Tesseract使用的语言模型，如 'eng', 'chi_sim', 'eng+chi_sim'。
        tesseract_cmd: Tesseract可执行文件的可选路径。

    Returns:
        识别出的文本字符串，或一条错误信息。
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img, lang=lang).strip()
    except pytesseract.TesseractNotFoundError:
        msg = "Tesseract is not installed or not in your PATH, and no path was specified via tesseract_cmd."
        logger.error(msg)
        return f"OCR Configuration Error: {msg}"
    except Exception as e:
        logger.error(f"An unknown error occurred during OCR for {image_path}: {e}", exc_info=True)
        return f"OCR Error: {e}"

def remove_background(image_path: str, output_path: Optional[str] = None) -> Optional[Image.Image]:
    """
    使用rembg库移除图像背景。

    Args:
        image_path: 输入图像路径。
        output_path: 可选的输出文件路径。如果提供，结果将保存到此。

    Returns:
        一个包含移除背景后图像的Pillow Image对象，或在失败时返回None。
    """
    try:
        with open(image_path, 'rb') as i:
            input_data = i.read()
        output_data = remove(input_data)
        
        output_image = Image.open(io.BytesIO(output_data))
        
        if output_path:
            # Saving from the Image object is safer than writing raw bytes
            # as it handles format conversion correctly.
            output_image.save(output_path)
            
        return output_image
    except FileNotFoundError:
        logger.error(f"Background removal failed: File not found at {image_path}")
        return None
    except Exception as e:
        logger.error(f"Background removal failed for {image_path}: {e}", exc_info=True)
        return None

def select_best_image_in_group(group_paths: List[str]) -> Optional[str]:
    """
    从一组相似的图片中，根据分辨率和文件大小选出最佳的一张。

    Args:
        group_paths: 一组图片的文件路径列表。

    Returns:
        最佳图片的文件路径，如果所有图片都无法读取则返回None。
    """
    if not group_paths:
        return None

    best_path, max_res, max_size = None, -1, -1
    for path_str in group_paths:
        try:
            path = Path(path_str)
            with Image.open(path) as img:
                res = img.width * img.height
                size = path.stat().st_size
                if res > max_res or (res == max_res and size > max_size):
                    max_res, max_size, best_path = res, size, path_str
        except (FileNotFoundError, UnidentifiedImageError):
            logger.warning(f"Could not read image for best selection: {path_str}")
            continue
            
    if not best_path:
        logger.error(f"Could not read any valid image from the group: {group_paths}")
        return None
        
    return best_path

# ==========================================================
# 7. 辅助工具 (Utility & Helpers)
# ==========================================================
def _get_bundled_font_path(font_name: str = "DejaVuSans.ttf") -> Optional[str]:
    """
    尝试查找一个捆绑的或系统级的字体文件，以增强跨平台一致性。

    Args:
        font_name: 期望的字体文件名。

    Returns:
        找到的字体文件的路径字符串，或None。
    """
    # Search order: local 'fonts' dir, common OS paths
    possible_paths = [
        Path(__file__).parent / "assets/fonts" / font_name, # Preferred: local assets folder
        Path.cwd() / "fonts" / font_name,
        f"/usr/share/fonts/truetype/dejavu/{font_name}",      # Linux (Debian/Ubuntu)
        "/System/Library/Fonts/Supplemental/Arial.ttf",      # macOS (using a common font)
        "C:/Windows/Fonts/arial.ttf"                         # Windows
    ]
    for path in possible_paths:
        if Path(path).exists():
            return str(path)
    logger.debug("No bundled or system font found, will use Pillow's default.")
    return None