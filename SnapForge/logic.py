import os
import io
import logging
import multiprocessing
import importlib.resources
from pathlib import Path
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import (
    Optional, Dict, Any, Tuple, List, Set, Callable, Sequence
)

# Pillow and external libraries
from PIL import (
    Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, UnidentifiedImageError
)
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt

# =====================
# 1. 类型与配置 (已重构)
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
    """格式转换相关配置"""
    format: str
    quality: int = 85

    def __post_init__(self):
        self.format = self.format.lower().lstrip('.')
        if not (0 <= self.quality <= 100):
            raise ValueError("quality must be between 0 and 100")

@dataclass(slots=True)
class ResizeConfig:
    """缩放相关配置"""
    width: int = 800
    height: int = 600
    mode: ResizeMode = ResizeMode.CONTAIN
    only_shrink: bool = True

@dataclass(slots=True)
class CropConfig:
    """裁剪相关配置"""
    x: int
    y: int
    w: int
    h: int

    def __post_init__(self):
        if self.w <= 0 or self.h <= 0:
            raise ValueError("Crop dimensions must be positive")
        if self.x < 0 or self.y < 0:
            raise ValueError("Crop coordinates cannot be negative")

@dataclass(slots=True)
class RotateConfig:
    """旋转相关配置"""
    angle: int = 0

@dataclass(slots=True)
class FilterConfig:
    """滤镜相关配置"""
    type: FilterType
    enhance_factor: float = 1.5

    def __post_init__(self):
        if self.enhance_factor <= 0:
            raise ValueError("enhance_factor must be positive")

@dataclass(slots=True)
class WatermarkConfig:
    """水印相关配置"""
    text: str
    font_path: Optional[str] = None
    size: int = 32
    color: Tuple[int, int, int, int] = (255, 255, 255, 128)
    position: str = "bottom-right"
    margin: int = 20

# --- 主配置类 (通过组合构建) ---
@dataclass(kw_only=True, slots=True, frozen=False)
class ProcessConfig:
    rename_config: Optional[RenameConfig] = None
    convert_config: Optional[ConvertConfig] = None
    resize_config: Optional[ResizeConfig] = None
    crop_config: Optional[CropConfig] = None
    rotate_config: Optional[RotateConfig] = None
    filter_config: Optional[FilterConfig] = None
    watermark_config: Optional[WatermarkConfig] = None

    preserve_metadata: bool = True
    num_processes: int = field(default_factory=lambda: 2)

    def __post_init__(self):
        if self.num_processes < 1:
            raise ValueError("num_processes must be >= 1")


# =====================
# 2. 日志与常量 (已改进)
# =====================
FORMAT_MAPPING = {
    "jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "bmp": "BMP",
    "gif": "GIF", "tiff": "TIFF", "webp": "WEBP"
}

def get_logger(name: str = "image_processor"):
    """
    获取一个logger实例。库代码不应配置处理器(handler)，这应由应用层代码负责。
    """
    return logging.getLogger(name)

logger = get_logger(__name__)


# =====================
# 3. 核心处理逻辑 (已重构)
# =====================

def process_image(
    src_path: Path, dest_dir: Path, config: ProcessConfig, *, counter: int
) -> Tuple[str, str, Optional[str]]:
    """单张图片处理函数，处理流程由ProcessConfig驱动"""
    try:
        with Image.open(src_path) as temp_img:
            width, height = temp_img.size

        # --- 文件名处理 ---
        original_stem = src_path.stem
        original_ext = src_path.suffix.lower()

        if config.rename_config:
            rc = config.rename_config
            naming_context = {
                "prefix": rc.prefix, "counter": counter,
                "original_filename": original_stem, "width": width, "height": height
            }
            base_name = rc.naming_template.format(**naming_context)
        else:
            base_name = original_stem
        
        final_ext = f".{config.convert_config.format}" if config.convert_config else original_ext
        dest_path = dest_dir / f"{base_name}{final_ext}"

        _process_image_logic(src_path, dest_path, final_ext, config)
        return src_path.name, "success", str(dest_path)
    except Exception as e:
        logger.error(f"Failed to process {src_path.name}: {e}", exc_info=True)
        return src_path.name, "error", f"{type(e).__name__}: {e}"

def _process_image_logic(src_path: Path, dest_path: Path, target_ext: str, config: ProcessConfig):
    with Image.open(src_path) as img:
        img = img.convert("RGB") if img.mode in ('CMYK', 'P') else img

        exif_data = img.info.get("exif") if config.preserve_metadata and "exif" in img.info else None
        
        # 按顺序应用各种处理，传递更精确的配置对象
        if config.crop_config and config.crop_config.w > 0:
            img = _apply_crop_logic(img, config.crop_config)
        if config.rotate_config and config.rotate_config.angle != 0:
            img = _apply_rotate_logic(img, config.rotate_config)
        if config.resize_config:
            img = _resize_image_logic(img, config.resize_config)
        if config.filter_config:
            img = _apply_filter_logic(img, config.filter_config)
        if config.watermark_config:
            img = _apply_watermark_logic(img, config.watermark_config)
        
        quality = config.convert_config.quality if config.convert_config else 85
        _save_image_logic(img, dest_path, target_ext, exif_data, quality)

def _save_image_logic(img: Image.Image, dest_path: Path, target_ext: str, exif_data: Optional[bytes], quality: int):
    ext = target_ext.lower().lstrip('.')
    save_params = {"format": FORMAT_MAPPING.get(ext, "JPEG")}

    quality = int(max(1, min(100, quality)))
    if ext in ("jpg", "jpeg", "webp"):
        save_params["quality"] = quality
    elif ext == "png":
        save_params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
    
    if exif_data: save_params["exif"] = exif_data
        
    if ext in ["jpg", "jpeg", "bmp"] and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
        
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, **save_params)

def _apply_crop_logic(img: Image.Image, config: CropConfig) -> Image.Image:
    return img.crop((config.x, config.y, config.x + config.w, config.y + config.h))

def _apply_rotate_logic(img: Image.Image, config: RotateConfig) -> Image.Image:
    return img.rotate(config.angle, expand=True, resample=getattr(Image, "Resampling", Image).BICUBIC)

def _resize_image_logic(img: Image.Image, config: ResizeConfig) -> Image.Image:
    orig_w, orig_h = img.size
    if config.only_shrink and orig_w <= config.width and orig_h <= config.height:
        return img

    size = (config.width, config.height)
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS
    match config.mode:
        case ResizeMode.CONTAIN: img.thumbnail(size, resample_filter); return img
        case ResizeMode.COVER: return ImageOps.fit(img, size, resample_filter, bleed=0.0)
        case ResizeMode.STRETCH: return img.resize(size, resample_filter)
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

def _apply_filter_logic(img: Image.Image, config: FilterConfig) -> Image.Image:
    if config.type == FilterType.GRAYSCALE: return img.convert("L")
    has_alpha = 'A' in img.getbands()
    alpha = img.getchannel('A') if has_alpha else None
    rgb_img = img.convert("RGB") if has_alpha else img
    filter_map = {
        FilterType.SHARPEN: ImageFilter.SHARPEN, FilterType.BLUR: ImageFilter.BLUR,
        FilterType.CONTOUR: ImageFilter.CONTOUR, FilterType.EMBOSS: ImageFilter.EMBOSS,
        FilterType.EDGE: ImageFilter.FIND_EDGES
    }
    if config.type in filter_map: filtered = rgb_img.filter(filter_map[config.type])
    elif config.type == FilterType.ENHANCE:
        enhancer = ImageEnhance.Contrast(rgb_img); filtered = enhancer.enhance(config.enhance_factor)
    else: return img
    if alpha: filtered.putalpha(alpha)
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
        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=config.num_processes) as pool:
            # 先收集所有结果，再在主进程中统一处理，避免并发问题
            process_results = list(pool.imap_unordered(_mp_worker, tasks))
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
    logger.info("Hashing images for duplicate search...")
    hashes: List[Tuple[str, imagehash.ImageHash]] = []
    for path in file_paths:
        try:
            with Image.open(path) as img: hashes.append((path, imagehash.phash(img)))
        except (FileNotFoundError, UnidentifiedImageError) as e:
            logger.warning(f"Cannot hash {path}: {e}")
    if not hashes: return []
    logger.info(f"Building BK-Tree and searching with {len(hashes)} hashes...")
    tree = _BKTree(dist_fn=lambda h1, h2: h1 - h2)
    for h in hashes: tree.add(h)
    groups, visited = [], set()
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
                exif_data[f"{ifd}:{tag_name}"] = value
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
    fig = None
    try:
        with Image.open(image_path) as img: rgb_img = img.convert('RGB')
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        colors, names = ('r', 'g', 'b'), ('Red', 'Green', 'Blue')
        for i, color in enumerate(colors):
            ax.plot(rgb_img.getchannel(i).histogram(), color=color, alpha=0.8, label=names[i])
        ax.set_title("RGB Histogram", fontsize=10); ax.set_xlim([0, 256])
        ax.set_xlabel("Pixel Intensity"); ax.set_ylabel("Frequency")
        ax.legend(fontsize='small'); ax.grid(True); fig.tight_layout()
        buf = io.BytesIO(); fig.savefig(buf, format='png'); buf.seek(0)
        return buf
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.warning(f"Histogram creation failed for {image_path}: {e}"); return None
    finally:
        if fig: plt.close(fig)



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
            return str(font_path) if font_path.exists() else None
    except (ModuleNotFoundError, FileNotFoundError):
        logger.debug(f"Bundled font package 'assets.fonts' not found. Pillow's default font will be used.")
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