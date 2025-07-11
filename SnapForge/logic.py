# logic.py
import os
import io
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt
import pytesseract
from rembg import remove

class ProcessLog:
    def __init__(self):
        self.entries = []
    def add(self, msg: str, level: str = "info"):
        prefix = {"info": "✅", "warn": "⚠️", "error": "❌", "skip": "⏩"}.get(level, "")
        self.entries.append(f"{prefix} {msg}")
    def get_text(self) -> str:
        return "\n".join(self.entries)

class ImageProcessor:
    def __init__(self):
        self.format_mapping = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
            ".bmp": "BMP", ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP"
        }

    def batch_process(self, files, process_log, **kwargs):
        filter_ext_norm = self._normalize_extension(kwargs.get('filter_extension'))
        convert_ext_norm = self._normalize_extension(kwargs.get('convert_format'))
        
        processed_counter = 0
        result_paths = []
        
        files_to_process = []
        if filter_ext_norm:
            for file_path in files:
                if self._normalize_extension(os.path.splitext(file_path)[1]) == filter_ext_norm:
                    files_to_process.append(file_path)
                else:
                    process_log.add(f"跳过: {os.path.basename(file_path)}（格式不符）", level="skip")
        else:
            files_to_process = files

        total_to_process = len(files_to_process)
        if total_to_process == 0:
            self._update_progress(kwargs.get('progress_callback'), 1, 1, "无文件处理")
            return 0, 0, []

        out_dir = os.path.dirname(os.path.abspath(files[0]))
        for index, file_path in enumerate(files_to_process):
            filename = os.path.basename(file_path)
            try:
                original_ext = self._normalize_extension(os.path.splitext(file_path)[1])
                final_ext = convert_ext_norm or original_ext
                new_filename = self._generate_filename(kwargs.get('prefix'), kwargs.get('start_number', 1) + processed_counter, final_ext, out_dir)
                temp_path = os.path.join(out_dir, new_filename)
                
                self._process_image(file_path, temp_path, final_ext, **kwargs)

                processed_counter += 1
                result_paths.append(temp_path)
                process_log.add(f"成功: {filename} → {new_filename}", level="info")
            except Exception as e:
                process_log.add(f"失败: {filename}，原因: {e}", level="error")
            finally:
                self._update_progress(kwargs.get('progress_callback'), index + 1, total_to_process, filename)
        
        return processed_counter, total_to_process, result_paths
    
    def _normalize_extension(self, ext):
        if not ext: return None
        return f".{ext.lower()}" if not ext.startswith('.') else ext.lower()

    def _generate_filename(self, prefix, number, extension, target_dir):
        if not prefix: prefix = "processed"
        base_name = f"{prefix}_{number:04d}"
        new_name = f"{base_name}{extension}"
        counter = 1
        while os.path.exists(os.path.join(target_dir, new_name)):
            new_name = f"{base_name}_{counter}{extension}"
            counter += 1
        return new_name

    def _process_image(self, src_path, dest_path, target_ext, **kwargs):
        with Image.open(src_path) as img:
            exif_data = img.info.get("exif") if kwargs.get('preserve_metadata') else None
            
            if img.format == 'GIF': img = img.convert("RGBA")
            else: img = img.convert("RGBA")

            if kwargs.get('crop_params') and kwargs['crop_params'].get('w', 0) > 0 and kwargs['crop_params'].get('h', 0) > 0:
                cp = kwargs['crop_params']
                img = img.crop((cp["x"], cp["y"], cp["x"] + cp["w"], cp["y"] + cp["h"]))

            if kwargs.get('rotate', 0) != 0: img = img.rotate(kwargs['rotate'], expand=True, fillcolor=(0,0,0,0))

            if kwargs.get('resize_enabled'): img = self._resize_image(img, kwargs['resize_width'], kwargs['resize_height'], kwargs.get('resize_mode', 'fit'), kwargs.get('resize_only_shrink', True))
            
            if kwargs.get('filter_type'): img = self.apply_filter(img, kwargs['filter_type'])

            if kwargs.get('watermark'): img = self.apply_watermark(img, kwargs['watermark'])
            
            save_params = {}
            if target_ext in self.format_mapping: save_params["format"] = self.format_mapping[target_ext]
            
            if kwargs.get('quality') is not None:
                quality = kwargs.get('quality')
                if target_ext in (".jpg", ".jpeg", ".webp"): save_params["quality"] = int(max(1, min(100, quality)))
                elif target_ext == ".png": save_params["compress_level"] = int(max(0, min(9, (100 - quality) // 10)))
            
            if exif_data: save_params["exif"] = exif_data
            
            if target_ext in [".jpg", ".jpeg", ".bmp"] and img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            img.save(dest_path, **save_params)

    def _resize_image(self, img, width, height, mode="fit", only_shrink=True):
        orig_w, orig_h = img.size
        if only_shrink and orig_w <= width and orig_h <= height: return img
        if mode == "fit":
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            return img
        return ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)
            
    def _update_progress(self, callback, processed, total, filename=""):
        if callback:
            progress = int(processed / total * 100) if total > 0 else 100
            callback(progress, filename)

    def apply_watermark(self, img, watermark):
        text = watermark.get("text")
        if not text: return img
        base_image = img.copy()
        overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font_path, font_size, color, pos = watermark.get("font"), watermark.get("size", 32), watermark.get("color", (255,255,255,128)), watermark.get("pos", "bottom-right")
        try:
            font = ImageFont.truetype(font_path or "arial.ttf", font_size)
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

    def apply_filter(self, img, filter_type):
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

# --- Independent Functions ---
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