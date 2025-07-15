# logic.py

import os
import io
import multiprocessing
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List

# Pillow and related imaging libraries
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import imagehash
import piexif

# Analysis and other utility libraries
from colorthief import ColorThief
import matplotlib.pyplot as plt
import pytesseract
from rembg import remove

# ==========================================================
# 1. 全局常量 (Centralized Constants)
# ==========================================================
FORMAT_MAPPING = {
    ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP",
    ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP"
}

AVAILABLE_FILTERS = [
    "grayscale", "sharpen", "blur", "contour", "emboss", "edge", "enhance"
]

# ==========================================================
# 2. 配置对象 (Upgraded Dataclass)
# ==========================================================
@dataclass
class ProcessConfig:
    """
    一个用于封装所有图像处理参数的数据类，使配置传递更清晰、安全。
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
    resize_mode: str = "contain"  # 'contain': 适应边界, 'cover': 裁剪填充, 'stretch': 拉伸
    resize_only_shrink: bool = True

    # --- Transformations & Effects ---
    crop_params: Optional[Dict[str, int]] = None
    rotate_angle: int = 0
    filter_type: Optional[str] = None
    watermark_params: Optional[Dict[str, Any]] = None

    # --- Advanced & Metadata ---
    preserve_metadata: bool = True
    num_processes: Optional[int] = field(default_factory=lambda: max(1, os.cpu_count() - 1 if os.cpu_count() else 1))

# ==========================================================
# 3. 日志类 (Unchanged)
# ==========================================================
class ProcessLog:
    def __init__(self):
        self.entries = []
    def add(self, msg: str, level: str = "info"):
        prefix = {"info": "✅", "warn": "⚠️", "error": "❌", "skip": "⏩"}.get(level, "")
        self.entries.append(f"{prefix} {msg}")
    def get_text(self) -> str:
        return "\n".join(self.entries)

# ==========================================================
# 4. 核心处理工作流 (Refactored & Optimized Workflow)
# ==========================================================
def _process_single_image_worker(args: Tuple[str, str, int, ProcessConfig]) -> Tuple[str, str, Optional[str]]:
    """
    为多进程设计的独立工作函数。
    它处理单个图像并返回结果元组：(原始文件名, 状态, 结果路径或错误信息)。
    """
    src_path_str, out_dir_str, counter, config = args
    src_path = Path(src_path_str)
    original_filename = src_path.name
    
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
        
        base_name = config.naming_template.format(**naming_context)
        original_ext = src_path.suffix.lower()
        # 确保扩展名前面有点，且为小写
        final_ext = (config.convert_format.lower() if config.convert_format else original_ext)
        if not final_ext.startswith('.'):
            final_ext = '.' + final_ext
        
        new_filename = f"{base_name}{final_ext}"
        dest_path = Path(out_dir_str) / new_filename

        _process_image_logic(src_path, dest_path, final_ext, config)
        
        return (original_filename, "success", str(dest_path))

    except Exception as e:
        return (original_filename, "error", f"{type(e).__name__}: {e}")

def _process_image_logic(src_path: Path, dest_path: Path, target_ext: str, config: ProcessConfig):
    """
    核心的、单一图像处理逻辑，经过性能和流程优化。
    """
    with Image.open(src_path) as img:
        exif_data = img.info.get("exif") if config.preserve_metadata and "exif" in img.info else None

        if config.crop_params and config.crop_params.get('w', 0) > 0:
            cp = config.crop_params
            img = img.crop((cp["x"], cp["y"], cp["x"] + cp["w"], cp["y"] + cp["h"]))

        if config.rotate_angle != 0:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            img = img.rotate(config.rotate_angle, expand=True, fillcolor=(0,0,0,0))

        if config.resize_enabled:
            img = _resize_image_logic(img, config)
        
        if config.filter_type:
            img = _apply_filter_logic(img, config.filter_type)

        if config.watermark_params:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            img = _apply_watermark_logic(img, config.watermark_params)
        
        _save_image_logic(img, dest_path, target_ext, exif_data, config.quality)

def _save_image_logic(img: Image.Image, dest_path: Path, target_ext: str, exif_data: Optional[bytes], quality: Optional[int]):
    """将处理后的图像保存到磁盘的辅助函数。"""
    save_params = {"format": FORMAT_MAPPING.get(target_ext)}
    if quality is not None:
        if target_ext in (".jpg", ".jpeg", ".webp"):
            save_params["quality"] = int(max(1, min(100, quality)))
        elif target_ext == ".png":
            save_params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
    
    if exif_data:
        save_params["exif"] = exif_data
    
    if target_ext in [".jpg", ".jpeg", ".bmp"] and img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            background.paste(img, mask=img.getchannel('A'))
        else:
            background.paste(img)
        img = background
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, **save_params)

def _resize_image_logic(img: Image.Image, config: ProcessConfig) -> Image.Image:
    """根据配置对图像进行缩放。"""
    orig_w, orig_h = img.size
    if config.resize_only_shrink and orig_w <= config.resize_width and orig_h <= config.resize_height:
        return img

    size = (config.resize_width, config.resize_height)
    resample_filter = Image.Resampling.LANCZOS

    if config.resize_mode == "contain":
        img.thumbnail(size, resample_filter)
        return img
    elif config.resize_mode == "cover":
        return ImageOps.fit(img, size, resample_filter)
    elif config.resize_mode == "stretch":
        return img.resize(size, resample_filter)
    return img

def _apply_watermark_logic(img: Image.Image, watermark_params: Dict[str, Any]) -> Image.Image:
    """在图像上应用文本水印。"""
    text = watermark_params.get("text")
    if not text: return img

    base_image = img.copy()
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_path = watermark_params.get("font")
    font_size = watermark_params.get("size", 32)
    color = watermark_params.get("color", (255, 255, 255, 128))
    pos = watermark_params.get("pos", "bottom-right")
    margin = 15

    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except (IOError, TypeError):
        font = ImageFont.load_default()

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

def _apply_filter_logic(img: Image.Image, filter_type: str) -> Image.Image:
    """对图像应用指定的滤镜效果。"""
    if filter_type not in AVAILABLE_FILTERS: return img
    if filter_type == "grayscale": return img.convert("L")

    rgb_img = img.convert("RGB") if img.mode != "RGB" else img
    
    filter_map = {
        "sharpen": ImageFilter.SHARPEN, "blur": ImageFilter.BLUR,
        "contour": ImageFilter.CONTOUR, "emboss": ImageFilter.EMBOSS,
        "edge": ImageFilter.FIND_EDGES
    }
    
    if filter_type in filter_map:
        filtered_img = rgb_img.filter(filter_map[filter_type])
    elif filter_type == "enhance":
        enhancer = ImageEnhance.Contrast(rgb_img)
        filtered_img = enhancer.enhance(1.5)
    else:
        return img
    
    if img.mode == "RGBA":
        filtered_img = filtered_img.convert("RGBA")
        filtered_img.putalpha(img.getchannel('A'))
        
    return filtered_img

# ==========================================================
# 5. 主调度器类 (Upgraded ImageProcessor)
# ==========================================================
class ImageProcessor:
    def batch_process(self,
                      files: List[str],
                      output_dir: str,
                      config: ProcessConfig,
                      process_log: ProcessLog,
                      progress_callback=None) -> Tuple[int, int, List[str]]:
        if not files:
            if progress_callback: progress_callback(1.0, "没有文件需要处理")
            return 0, 0, []

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        tasks = [(file_path, output_dir, config.start_number + i, config) for i, file_path in enumerate(files)]
        
        processed_count, total_files = 0, len(tasks)
        result_paths = []
        
        use_multiprocessing = (config.num_processes > 0 and total_files > 1)

        try:
            if not use_multiprocessing:
                raise ValueError("用户配置为单线程或只有一个文件")

            with multiprocessing.Pool(processes=config.num_processes) as pool:
                for i, result in enumerate(pool.imap_unordered(_process_single_image_worker, tasks)):
                    is_success = self._handle_result(result, process_log, result_paths)
                    if is_success: processed_count += 1
                    if progress_callback: progress_callback((i + 1) / total_files, result[0])
        except (ValueError, Exception) as e:
            level = "warn" if isinstance(e, ValueError) else "error"
            process_log.add(f"多进程处理失败或已禁用 ({e})。回退到单线程模式。", level=level)
            
            for i, task in enumerate(tasks):
                result = _process_single_image_worker(task)
                is_success = self._handle_result(result, process_log, result_paths)
                if is_success: processed_count += 1
                if progress_callback: progress_callback((i + 1) / total_files, result[0])

        return processed_count, total_files, sorted(result_paths)

    def _handle_result(self, result: Tuple[str, str, Optional[str]], log: ProcessLog, paths: List[str]) -> bool:
        """辅助方法，用于处理单个任务的结果并返回成功状态。"""
        original_filename, status, data = result
        if status == "success":
            log.add(f"成功: {original_filename} → {Path(data).name}", level="info")
            paths.append(data)
            return True
        else:
            log.add(f"失败: {original_filename}，原因: {data}", level="error")
            return False

# ==========================================================
# 6. 独立的工具函数 (Upgraded Standalone Functions)
# ==========================================================
def find_duplicate_images(file_paths: List[str], threshold: int = 8) -> List[List[str]]:
    hashes, groups, used = {}, [], set()
    for path_str in file_paths:
        try:
            with Image.open(path_str) as img: hashes[path_str] = imagehash.phash(img)
        except Exception: continue
    
    paths_list = list(hashes.keys())
    for i in range(len(paths_list)):
        path1 = paths_list[i]
        if path1 in used: continue
        group = [path1]
        for j in range(i + 1, len(paths_list)):
            path2 = paths_list[j]
            if path2 not in used and abs(hashes[path1] - hashes[path2]) <= threshold: group.append(path2)
        if len(group) > 1:
            for p in group: used.add(p)
            groups.append(sorted(group))
    return groups

def get_exif_data(image_path: str) -> Dict[str, Any]:
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd_name in ("0th", "Exif", "GPS", "1st", "thumbnail"):
            ifd_data = exif_dict.get(ifd_name)
            if not isinstance(ifd_data, dict): continue
            for tag, value in ifd_data.items():
                tag_name = piexif.TAGS.get(ifd_name, {}).get(tag, {}).get("name", hex(tag))
                if isinstance(value, bytes):
                    try: value = value.strip(b'\x00').decode('utf-8', errors='replace')
                    except Exception: value = repr(value)
                exif_data[f"{ifd_name}:{tag_name}"] = value
        return exif_data
    except Exception: return {}

def get_image_main_color(image_path: str) -> Tuple[Optional[Tuple], List]:
    try:
        ct = ColorThief(image_path)
        return ct.get_color(quality=1), ct.get_palette(color_count=6, quality=1)
    except Exception: return None, []

def plot_image_histogram(image_path: str) -> Optional[io.BytesIO]:
    try:
        with Image.open(image_path) as img: rgb_img = img.convert('RGB')
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        colors = ('r', 'g', 'b')
        for i, color in enumerate(colors):
            ax.plot(rgb_img.getchannel(i).histogram(), color=color, alpha=0.7)
        ax.set_title("RGB Histogram", fontsize=10)
        ax.set_xlim([0, 256])
        ax.grid(True)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception: return None

def ocr_image(image_path: str, lang: str = "chi_sim+eng") -> str:
    try:
        with Image.open(image_path) as img: return pytesseract.image_to_string(img, lang=lang).strip()
    except Exception as e: return f"OCR 错误: {e}"

def remove_background(image_path: str, output_path: Optional[str] = None) -> Image.Image:
    with open(image_path, 'rb') as i: input_data = i.read()
    output_data = remove(input_data)
    if output_path:
        with open(output_path, 'wb') as o: o.write(output_data)
    return Image.open(io.BytesIO(output_data))

def select_best_image_in_group(group_paths: List[str]) -> str:
    best_path, max_res, max_size = None, -1, -1
    for path_str in group_paths:
        try:
            path = Path(path_str)
            with Image.open(path) as img:
                res, size = img.width * img.height, path.stat().st_size
                if res > max_res or (res == max_res and size > max_size):
                    max_res, max_size, best_path = res, size, path_str
        except Exception: continue
    return best_path if best_path else group_paths[0]