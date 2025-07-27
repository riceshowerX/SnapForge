import os
import io
import logging
import multiprocessing
from pathlib import Path
from dataclasses import dataclass, field, InitVar
from enum import StrEnum, auto
from typing import (
    Optional, Dict, Any, Tuple, List, TypedDict, Set, Callable, Sequence, Self
)

from PIL import (
    Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, UnidentifiedImageError
)
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt
import pytesseract
from rembg import remove

# =====================
# 1. 类型与配置
# =====================

class ResizeMode(StrEnum):
    CONTAIN = auto()
    COVER = auto()
    STRETCH = auto()

class FilterType(StrEnum):
    GRAYSCALE = auto()
    SHARPEN = auto()
    BLUR = auto()
    CONTOUR = auto()
    EMBOSS = auto()
    EDGE = auto()
    ENHANCE = auto()

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

# =====================
# 2. 日志与常量
# =====================
FORMAT_MAPPING = {
    ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP",
    ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP"
}

def get_logger(name:str="image_processor"):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = get_logger(__name__)

# =====================
# 3. 配置数据类
# =====================
@dataclass(kw_only=True, slots=True, frozen=False)
class ProcessConfig:
    rename_enabled: bool = False
    prefix: Optional[str] = "image"
    start_number: int = 1
    naming_template: str = "{prefix}_{counter:04d}"

    convert_format: Optional[str] = None
    quality: Optional[int] = 85

    resize_enabled: bool = False
    resize_width: int = 800
    resize_height: int = 600
    resize_mode: ResizeMode = ResizeMode.CONTAIN
    resize_only_shrink: bool = True

    crop_params: Optional[CropParams] = None
    rotate_angle: int = 0
    filter_type: Optional[FilterType] = None
    watermark_params: Optional[WatermarkParams] = None
    watermark_margin: int = 20
    enhance_factor: float = 1.5

    preserve_metadata: bool = True
    num_processes: int = field(default_factory=lambda: max(1, (os.cpu_count() or 2) - 1))
    tesseract_cmd: Optional[str] = None

    def __post_init__(self):
        if self.quality is not None and not (0 <= self.quality <= 100):
            raise ValueError("quality must be 0-100")
        if self.num_processes < 1:
            raise ValueError("num_processes >= 1")
        if self.start_number < 0:
            raise ValueError("start_number >= 0")
        if self.enhance_factor <= 0:
            raise ValueError("enhance_factor > 0")
        if self.convert_format:
            object.__setattr__(self, "convert_format", self.convert_format.lower().lstrip('.'))

# =====================
# 4. 核心处理逻辑
# =====================

def process_image(
    src_path: Path, dest_path: Path, config: ProcessConfig, *, counter: int
) -> Tuple[str, str, Optional[str]]:
    """单张图片处理"""
    try:
        with Image.open(src_path) as temp_img:
            width, height = temp_img.size

        naming_context = {
            "prefix": config.prefix,
            "counter": counter,
            "original_filename": src_path.stem,
            "width": width,
            "height": height,
        }
        base_name = (
            config.naming_template.format(**naming_context)
            if config.rename_enabled else src_path.stem
        )
        original_ext = src_path.suffix.lower()
        final_ext = f".{config.convert_format}" if config.convert_format else original_ext
        new_filename = f"{base_name}{final_ext}"
        dest_path = dest_path / new_filename

        _process_image_logic(src_path, dest_path, final_ext, config)
        return (src_path.name, "success", str(dest_path))
    except Exception as e:
        logger.error(f"Failed to process {src_path.name}: {e}", exc_info=True)
        return (src_path.name, "error", f"{type(e).__name__}: {e}")

def _process_image_logic(
    src_path: Path, dest_path: Path, target_ext: str, config: ProcessConfig
):
    with Image.open(src_path) as img:
        img = img.convert("RGB") if img.mode in ('CMYK', 'P') else img

        exif_data = img.info.get("exif") if config.preserve_metadata and "exif" in img.info else None

        if config.crop_params and config.crop_params.get('w', 0) > 0:
            cp = config.crop_params
            img = img.crop((cp["x"], cp["y"], cp["x"] + cp["w"], cp["y"] + cp["h"]))

        if config.rotate_angle:
            img = img.rotate(config.rotate_angle, expand=True, resample=getattr(Image, "Resampling", Image).BICUBIC)

        if config.resize_enabled:
            img = _resize_image_logic(img, config)
        if config.filter_type:
            img = _apply_filter_logic(img, config)
        if config.watermark_params:
            img = _apply_watermark_logic(img, config)

        _save_image_logic(img, dest_path, target_ext, exif_data, config.quality)

def _save_image_logic(
    img: Image.Image, dest_path: Path, target_ext: str, exif_data: Optional[bytes], quality: Optional[int]
):
    ext = target_ext.lower()
    save_params = {"format": FORMAT_MAPPING.get(ext, "JPEG")}
    if quality is not None:
        quality = int(max(1, min(100, quality)))
        if ext in (".jpg", ".jpeg", ".webp"):
            save_params["quality"] = quality
        elif ext == ".png":
            save_params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
    if exif_data:
        save_params["exif"] = exif_data
    if ext in [".jpg", ".jpeg", ".bmp"] and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, **save_params)

def _resize_image_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    orig_w, orig_h = img.size
    if config.resize_only_shrink and orig_w <= config.resize_width and orig_h <= config.resize_height:
        return img
    size = (config.resize_width, config.resize_height)
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS
    match config.resize_mode:
        case ResizeMode.CONTAIN:
            img.thumbnail(size, resample_filter)
            return img
        case ResizeMode.COVER:
            return ImageOps.fit(img, size, resample_filter, bleed=0.0)
        case ResizeMode.STRETCH:
            return img.resize(size, resample_filter)
        case _:
            return img

def _apply_watermark_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    wp = config.watermark_params
    if not wp or not wp.get("text"):
        return img
    base_image = img.convert("RGBA") if img.mode != "RGBA" else img.copy()
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_path = wp.get("font") or _get_bundled_font_path()
    font_size = wp.get("size", 32)
    color = wp.get("color", (255, 255, 255, 128))
    pos = wp.get("pos", "bottom-right")
    margin = wp.get("margin", config.watermark_margin)
    text = wp["text"]
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        logger.warning(f"Could not load font '{font_path}'. Using default font.")
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    positions = {
        "bottom-right": (base_image.width - text_width - margin, base_image.height - text_height - margin),
        "bottom-left": (margin, base_image.height - text_height - margin),
        "top-right": (base_image.width - text_width - margin, margin),
        "top-left": (margin, margin),
        "center": ((base_image.width - text_width) // 2, (base_image.height - text_height) // 2),
    }
    x, y = positions.get(pos, positions["bottom-right"])
    draw.text((x, y), text, font=font, fill=color)
    return Image.alpha_composite(base_image, overlay)

def _apply_filter_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    filter_type = config.filter_type
    if not filter_type:
        return img
    match filter_type:
        case FilterType.GRAYSCALE:
            return img.convert("L")
        case _:
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
            elif filter_type == FilterType.ENHANCE:
                enhancer = ImageEnhance.Contrast(rgb_img)
                filtered_img = enhancer.enhance(config.enhance_factor)
            else:
                return img
            if has_alpha:
                filtered_img.putalpha(alpha)
            return filtered_img

# =====================
# 5. 主调度器
# =====================

class ImageProcessor:
    def __init__(self):
        self.logger = get_logger("ImageProcessor")

    def batch_process(
        self,
        files: Sequence[str],
        output_dir: str,
        config: ProcessConfig,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Tuple[int, int, List[str]]:
        if not files:
            self.logger.info("No files to process.")
            if progress_callback:
                progress_callback(1.0, "No files to process")
            return 0, 0, []
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        tasks = [(Path(file_path), output_dir, config, config.start_number + i) for i, file_path in enumerate(files)]
        total = len(tasks)
        results = []
        use_mp = (config.num_processes > 1 and total > 1)
        if use_mp:
            self.logger.info(f"Multiprocessing: {config.num_processes} processes for {total} files.")
            try:
                ctx = multiprocessing.get_context("spawn")
                with ctx.Pool(processes=config.num_processes) as pool:
                    for i, result in enumerate(pool.imap_unordered(_mp_worker, tasks)):
                        self._handle_result(result, results)
                        if progress_callback:
                            progress_callback((i + 1) / total, result[0])
            except Exception as e:
                self.logger.error(f"Multiprocessing failed: {e}, falling back to serial.", exc_info=True)
                results.clear()
                self._process_serial(tasks, results, progress_callback)
        else:
            self.logger.info(f"Single-threaded processing {total} files.")
            self._process_serial(tasks, results, progress_callback)
        return len(results), total, sorted(results)

    def _process_serial(self, tasks, results, progress_callback):
        total_files = len(tasks)
        for i, task in enumerate(tasks):
            result = _mp_worker(task)
            self._handle_result(result, results)
            if progress_callback:
                progress_callback((i + 1) / total_files, task[0])

    def _handle_result(self, result, results):
        original_filename, status, data = result
        if status == "success":
            self.logger.info(f"✅ Success: {original_filename} -> {Path(data).name}")
            results.append(data)
        else:
            self.logger.error(f"❌ Failed: {original_filename}, Reason: {data}")

def _mp_worker(args):
    src_path, out_dir, config, counter = args
    return process_image(src_path, out_dir, config, counter=counter)

# =====================
# 6. 工具函数
# =====================

def find_duplicate_images(file_paths: List[str], threshold: int = 8) -> List[List[str]]:
    path_to_hashes: Dict[str, imagehash.ImageHash] = {}
    for path in file_paths:
        try:
            with Image.open(path) as img:
                path_to_hashes[path] = imagehash.phash(img)
        except (FileNotFoundError, UnidentifiedImageError) as e:
            logger.warning(f"Cannot hash {path}: {e}")
            continue
    paths = list(path_to_hashes.keys())
    groups, visited_indices = [], set()
    index_map = {p: i for i, p in enumerate(paths)}
    for i, p in enumerate(paths):
        if i in visited_indices:
            continue
        group = {p}
        for j in range(i + 1, len(paths)):
            if j in visited_indices:
                continue
            if path_to_hashes[p] - path_to_hashes[paths[j]] <= threshold:
                group.add(paths[j])
        if len(group) > 1:
            groups.append(sorted(list(group)))
            visited_indices.update(index_map[g] for g in group if g in index_map)
    return groups

def get_exif_data(image_path: str) -> Dict[str, Any]:
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd_name in ("0th", "Exif", "GPS", "1st", "thumbnail"):
            ifd_data = exif_dict.get(ifd_name)
            if not isinstance(ifd_data, dict):
                continue
            for tag, value in ifd_data.items():
                tag_info = piexif.TAGS.get(ifd_name, {}).get(tag, {"name": f"UnknownTag_{hex(tag)}"})
                tag_name = tag_info.get("name")
                if isinstance(value, bytes):
                    try:
                        value = value.strip(b'\x00').decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            value = value.strip(b'\x00').decode('latin-1')
                        except UnicodeDecodeError:
                            value = repr(value)
                exif_data[f"{ifd_name}:{tag_name}"] = value
        return exif_data
    except (FileNotFoundError, piexif.InvalidImageDataError, ValueError) as e:
        logger.warning(f"Could not read EXIF: {image_path}: {e}")
        return {}

def get_image_main_color(image_path: str) -> Tuple[Optional[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
    try:
        ct = ColorThief(image_path)
        dominant_color = ct.get_color(quality=1)
        palette = ct.get_palette(color_count=6, quality=1)
        return dominant_color, palette
    except Exception as e:
        logger.warning(f"Color analysis failed: {image_path}: {e}")
        return None, []

def plot_image_histogram(image_path: str) -> Optional[io.BytesIO]:
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
        logger.warning(f"Histogram failed: {image_path}: {e}")
        return None
    finally:
        if fig:
            plt.close(fig)

def ocr_image(image_path: str, lang: str = "chi_sim+eng", tesseract_cmd: Optional[str] = None) -> str:
    local_tesseract_cmd = tesseract_cmd or os.environ.get("TESSERACT_CMD")
    if local_tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = local_tesseract_cmd
    try:
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img, lang=lang).strip()
    except pytesseract.TesseractNotFoundError:
        msg = "Tesseract not found."
        logger.error(msg)
        return f"OCR Configuration Error: {msg}"
    except Exception as e:
        logger.error(f"OCR error: {image_path}: {e}", exc_info=True)
        return f"OCR Error: {e}"

def remove_background(image_path: str, output_path: Optional[str] = None) -> Optional[Image.Image]:
    try:
        with open(image_path, 'rb') as i:
            input_data = i.read()
        output_data = remove(input_data)
        output_image = Image.open(io.BytesIO(output_data))
        if output_path:
            output_image.save(output_path)
        return output_image
    except FileNotFoundError:
        logger.error(f"Background removal failed: File not found: {image_path}")
        return None
    except Exception as e:
        logger.error(f"Background removal failed: {image_path}: {e}", exc_info=True)
        return None

def select_best_image_in_group(group_paths: List[str]) -> Optional[str]:
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
        logger.error(f"Could not read any valid image in group: {group_paths}")
        return None
    return best_path

def _get_bundled_font_path(font_name: str = "DejaVuSans.ttf") -> Optional[str]:
    possible_paths = [
        Path(__file__).parent / "assets/fonts" / font_name,
        Path.cwd() / "fonts" / font_name,
        f"/usr/share/fonts/truetype/dejavu/{font_name}",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for path in possible_paths:
        if Path(path).exists():
            return str(path)
    logger.debug("No bundled font found, will use default.")
    return None