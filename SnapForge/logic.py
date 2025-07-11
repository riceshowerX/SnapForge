# logic.py
import os
import io
import shutil
import multiprocessing
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt
import pytesseract
from rembg import remove
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List

# ==========================================================
# 1. 配置对象 (Dataclass) - 用于清晰、安全地传递参数
# ==========================================================
@dataclass
class ProcessConfig:
    # Renaming & Naming Template
    rename_enabled: bool = False
    prefix: Optional[str] = "image"
    start_number: int = 1
    naming_template: str = "{prefix}_{counter:04d}"

    # Conversion & Compression
    convert_format: Optional[str] = None
    quality: Optional[int] = 85

    # Resizing
    resize_enabled: bool = False
    resize_width: int = 800
    resize_height: int = 600
    resize_mode: str = "fit"
    resize_only_shrink: bool = True

    # Advanced
    preserve_metadata: bool = True
    watermark_params: Optional[Dict[str, Any]] = None
    crop_params: Optional[Dict[str, int]] = None
    rotate_angle: int = 0
    filter_type: Optional[str] = None

# ==========================================================
# 2. 日志类 (无变化)
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
# 3. 并行处理的工作函数 (这是一个顶层函数，以便多进程调用)
# ==========================================================
def _process_single_image_worker(args: Tuple[str, str, int, ProcessConfig]) -> Tuple[str, str, Optional[str]]:
    """
    Worker function for multiprocessing.
    Processes one image and returns (original_filename, status, result_path_or_error_msg).
    """
    src_path, out_dir, counter, config = args
    original_filename = os.path.basename(src_path)
    
    try:
        with Image.open(src_path) as img:
            naming_context = {
                "prefix": config.prefix,
                "counter": counter,
                "original_filename": os.path.splitext(original_filename)[0],
                "width": img.width,
                "height": img.height
            }
            
            base_name = config.naming_template.format(**naming_context)
            original_ext = os.path.splitext(src_path)[1].lower()
            final_ext = config.convert_format or original_ext
            new_filename = f"{base_name}{final_ext}"

            dest_path = os.path.join(out_dir, new_filename)
            _process_image_logic(src_path, dest_path, final_ext, config)
            
            return (original_filename, "success", dest_path)

    except Exception as e:
        return (original_filename, "error", str(e))

def _process_image_logic(src_path: str, dest_path: str, target_ext: str, config: ProcessConfig):
    """
    The actual image processing logic, extracted to be reusable.
    """
    with Image.open(src_path) as img:
        exif_data = img.info.get("exif") if config.preserve_metadata else None
        img = img.convert("RGBA")

        if config.crop_params and config.crop_params.get('w', 0) > 0 and config.crop_params.get('h', 0) > 0:
            cp = config.crop_params
            img = img.crop((cp["x"], cp["y"], cp["x"] + cp["w"], cp["y"] + cp["h"]))

        if config.rotate_angle != 0:
            img = img.rotate(config.rotate_angle, expand=True, fillcolor=(0,0,0,0))

        if config.resize_enabled:
            img = _resize_image_logic(img, config.resize_width, config.resize_height, config.resize_mode, config.resize_only_shrink)
        
        if config.filter_type:
            img = _apply_filter_logic(img, config.filter_type)

        if config.watermark_params:
            img = _apply_watermark_logic(img, config.watermark_params)
        
        save_params = {}
        format_mapping = { ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP", ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP" }
        if target_ext in format_mapping:
            save_params["format"] = format_mapping[target_ext]
        
        if config.quality is not None:
            if target_ext in (".jpg", ".jpeg", ".webp"):
                save_params["quality"] = int(max(1, min(100, config.quality)))
            elif target_ext == ".png":
                save_params["compress_level"] = int(max(0, min(9, (100 - config.quality) // 10)))
        
        if exif_data: save_params["exif"] = exif_data
        
        if target_ext in [".jpg", ".jpeg", ".bmp"] and img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        img.save(dest_path, **save_params)

def _resize_image_logic(img, width, height, mode="fit", only_shrink=True):
    orig_w, orig_h = img.size
    if only_shrink and orig_w <= width and orig_h <= height: return img
    if mode == "fit":
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img
    return ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)

def _apply_watermark_logic(img, watermark_params):
    text = watermark_params.get("text")
    if not text: return img
    base_image = img.copy()
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_path = watermark_params.get("font")
    font_size = watermark_params.get("size", 32)
    color = watermark_params.get("color", (255,255,255,128))
    pos = watermark_params.get("pos", "bottom-right")
    try: font = ImageFont.truetype(font_path or "arial.ttf", font_size)
    except IOError: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = 15
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

def _apply_filter_logic(img, filter_type):
    rgb_img = img.convert("RGB")
    if filter_type == "grayscale": return img.convert("L")
    elif filter_type == "sharpen": filtered_img = rgb_img.filter(ImageFilter.SHARPEN)
    elif filter_type == "blur": filtered_img = rgb_img.filter(ImageFilter.BLUR)
    elif filter_type == "contour": filtered_img = rgb_img.filter(ImageFilter.CONTOUR)
    elif filter_type == "emboss": filtered_img = rgb_img.filter(ImageFilter.EMBOSS)
    elif filter_type == "edge": filtered_img = rgb_img.filter(ImageFilter.FIND_EDGES)
    elif filter_type == "enhance":
        enhancer = ImageEnhance.Contrast(rgb_img)
        filtered_img = enhancer.enhance(1.5)
    else: return img
    return filtered_img.convert("RGBA")

# ==========================================================
# 4. ImageProcessor Class (Now orchestrates multiprocessing)
# ==========================================================
class ImageProcessor:
    def batch_process(self, files: List[str], config: ProcessConfig, process_log: ProcessLog, progress_callback=None) -> Tuple[int, int, List[str]]:
        if not files:
            if progress_callback: progress_callback(1.0, "")
            return 0, 0, []

        out_dir = os.path.dirname(os.path.abspath(files[0]))
        
        tasks = []
        for i, file_path in enumerate(files):
            counter = config.start_number + i
            tasks.append((file_path, out_dir, counter, config))

        processed_count = 0
        result_paths = []
        
        try:
            # Use all available cores for maximum performance
            num_processes = multiprocessing.cpu_count()
            with multiprocessing.Pool(processes=num_processes) as pool:
                total_tasks = len(tasks)
                for i, result in enumerate(pool.imap_unordered(_process_single_image_worker, tasks)):
                    original_filename, status, result_data = result
                    if status == "success":
                        process_log.add(f"成功: {original_filename} → {os.path.basename(result_data)}", level="info")
                        result_paths.append(result_data)
                        processed_count += 1
                    else:
                        process_log.add(f"失败: {original_filename}，原因: {result_data}", level="error")
                    
                    if progress_callback:
                        progress_callback((i + 1) / total_tasks, original_filename)
        except Exception as e:
            process_log.add(f"多进程处理失败: {e}", level="error")
            # Fallback to single-threaded processing if multiprocessing fails
            for task in tasks:
                original_filename, status, result_data = _process_single_image_worker(task)
                if status == "success":
                    # ... (log success)
                    pass
                else:
                    # ... (log error)
                    pass


        return processed_count, len(files), sorted(result_paths)

# ==========================================================
# 5. Independent Functions
# ==========================================================
def find_duplicate_images(file_paths, threshold=8):
    hashes, groups, used = {}, [], set()
    for path in file_paths:
        try:
            with Image.open(path) as img: hashes[path] = imagehash.phash(img)
        except Exception: continue
    for path1, hash1 in hashes.items():
        if path1 in used: continue
        group = [path1]
        for path2, hash2 in hashes.items():
            if path2 != path1 and path2 not in used and abs(hash1 - hash2) <= threshold: group.append(path2)
        if len(group) > 1:
            for p in group: used.add(p)
            groups.append(sorted(group))
    return groups

def get_exif_data(image_path):
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd in ("0th", "Exif", "GPS", "1st", "thumbnail"):
            if ifd in exif_dict and isinstance(exif_dict[ifd], dict):
                for tag, value in exif_dict[ifd].items():
                    tag_name = piexif.TAGS.get(ifd, {}).get(tag, {}).get("name", hex(tag))
                    if isinstance(value, bytes):
                        try: value = value.strip(b'\x00').decode('utf-8', errors='ignore')
                        except: value = str(value)
                    exif_data[f"{ifd}:{tag_name}"] = value
        return exif_data if exif_data else {}
    except Exception: return {}

def get_image_main_color(image_path):
    try:
        ct = ColorThief(image_path); return ct.get_color(quality=1), ct.get_palette(color_count=6, quality=1)
    except Exception: return None, []

def plot_image_histogram(image_path):
    try:
        with Image.open(image_path) as img: rgb_img = img.convert('RGB')
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(4, 2)); colors = ('r', 'g', 'b')
        for i, color in enumerate(colors): plt.plot(rgb_img.getchannel(i).histogram(), color=color)
        plt.xlim([0, 256]); plt.tight_layout(); buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100); plt.close(); buf.seek(0)
        return buf
    except Exception: return None

def ocr_image(image_path, lang="chi_sim+eng"):
    try:
        with Image.open(image_path) as img: return pytesseract.image_to_string(img, lang=lang).strip()
    except Exception as e: return f"OCR Error: {e}"

def smart_classify(image_path):
    try:
        with Image.open(image_path) as img:
            w, h = img.size; aspect_ratio = w / h
            shape = "横向宽幅" if aspect_ratio > 1.5 else "纵向长幅" if aspect_ratio < 0.67 else "常规比例"
        dom_color, _ = get_image_main_color(image_path)
        color_str = str(dom_color) if dom_color else "未知"
        return [shape, f"主色:{color_str}"]
    except Exception: return ["无法识别"]

def remove_background(image_path, output_path=None):
    with open(image_path, 'rb') as i: input_data = i.read()
    output_data = remove(input_data)
    if output_path:
        with open(output_path, 'wb') as o: o.write(output_data)
    return Image.open(io.BytesIO(output_data))

def select_best_image_in_group(group_paths):
    best_image_path, max_resolution, max_size = None, -1, -1
    for path in group_paths:
        try:
            with Image.open(path) as img:
                resolution = img.width * img.height
                size = os.path.getsize(path)
                if resolution > max_resolution or (resolution == max_resolution and size > max_size):
                    max_resolution, max_size, best_image_path = resolution, size, path
        except Exception: continue
    return best_image_path if best_image_path else group_paths[0]