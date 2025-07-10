import os
import threading
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import imagehash
import piexif
from colorthief import ColorThief
import matplotlib.pyplot as plt
import io
import pytesseract
from typing import List, Optional, Dict, Any
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
    def __init__(self, threads: int = 1):
        self.supported_formats = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
        self.format_mapping = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
            ".bmp": "BMP", ".gif": "GIF", ".tiff": "TIFF", ".webp": "WEBP"
        }
        self.threads = threads

    def batch_process(
        self,
        files: List[str],
        prefix: Optional[str]=None,
        start_number: int=1,
        extension: Optional[str]=None,
        convert_format: Optional[str]=None,
        quality: Optional[int]=None,
        progress_callback=None,
        preserve_metadata: bool=True,
        resize_enabled: bool=False,
        resize_width: Optional[int]=None,
        resize_height: Optional[int]=None,
        resize_mode: str="fit",
        resize_only_shrink: bool=True,
        watermark: Optional[Dict]=None,
        crop_params: Optional[Dict]=None,
        rotate: int=0,
        filter_type: Optional[str]=None,
        exif_edit: Optional[Dict]=None,
        process_log: Optional[ProcessLog]=None
    ):
        if extension:
            extension = self._normalize_extension(extension)
        if convert_format:
            convert_format = self._normalize_extension(convert_format)
        processed = 0
        total_files = len(files)
        result_paths = []
        if total_files == 0:
            if progress_callback:
                progress_callback(100, "")
            return (0, 0, [])
        out_dir = os.path.dirname(os.path.abspath(files[0]))

        # 支持多线程并发
        results = [None] * total_files
        lock = threading.Lock()
        def process_one(index, file_path):
            nonlocal processed
            filename = os.path.basename(file_path)
            filename = "".join(x for x in filename if x.isalnum() or x in "._-")
            try:
                # 图片类型检测
                file_ext = self._normalize_extension(os.path.splitext(file_path)[1])
                if extension and file_ext != extension:
                    if process_log: process_log.add(f"跳过: {filename}（类型不符，仅处理{extension}）", level="skip")
                    return
                try:
                    with Image.open(file_path) as test_img:
                        test_img.verify()
                except Exception:
                    if process_log: process_log.add(f"跳过: {filename}（不是有效图片）", level="skip")
                    return
                if resize_enabled and (not resize_width or not resize_height or resize_width < 1 or resize_height < 1):
                    if process_log: process_log.add(f"跳过: {filename}（非法尺寸参数）", level="skip")
                    return
                if convert_format and file_ext == convert_format and not quality:
                    if process_log: process_log.add(f"跳过: {filename}（输入输出格式相同且无压缩变更）", level="skip")
                    return
                # 自动检测EXIF与色彩空间
                exif_info = get_exif_data(file_path)
                img_info = ""
                try:
                    with Image.open(file_path) as im:
                        img_info = f", 分辨率: {im.size}, 模式: {im.mode}, DPI: {im.info.get('dpi', '未知')}"
                except Exception:
                    pass
                new_filename = self._generate_filename(
                    prefix, start_number + index,
                    convert_format or file_ext, out_dir
                )
                temp_path = os.path.join(out_dir, new_filename)
                self._process_image(
                    file_path, temp_path,
                    convert_format, quality, preserve_metadata,
                    resize_enabled, resize_width, resize_height, resize_mode, resize_only_shrink,
                    watermark, crop_params, rotate, filter_type, exif_edit
                )
                with lock:
                    nonlocal result_paths
                    processed += 1
                    result_paths.append(temp_path)
                if process_log: process_log.add(f"成功: {filename} → {new_filename}{img_info}", level="info")
            except Exception as e:
                if process_log: process_log.add(f"失败: {filename}，原因: {repr(e)}", level="error")
            finally:
                self._update_progress(progress_callback, processed, total_files, filename)

        # 并发处理
        if self.threads > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(process_one, idx, path) for idx, path in enumerate(files)]
                concurrent.futures.wait(futures)
        else:
            for idx, file_path in enumerate(files):
                process_one(idx, file_path)

        return (processed, total_files, result_paths)

    def _normalize_extension(self, ext):
        if not ext:
            return None
        ext = ext.lower()
        if not ext.startswith("."):
            ext = "." + ext
        if ext == ".jpeg":
            return ".jpg"
        return ext

    def _generate_filename(self, prefix, number, extension, target_dir):
        base_name = f"{prefix}_{number:04d}" if prefix else f"{number:04d}"
        new_name = f"{base_name}{extension}"
        counter = 1
        while os.path.exists(os.path.join(target_dir, new_name)):
            new_name = f"{base_name}_{counter}{extension}"
            counter += 1
        return new_name

    def _process_image(
        self,
        src_path,
        dest_path,
        target_ext,
        quality,
        preserve_metadata,
        resize_enabled=False,
        resize_width=None,
        resize_height=None,
        resize_mode="fit",
        resize_only_shrink=True,
        watermark=None,
        crop_params=None,
        rotate=0,
        filter_type=None,
        exif_edit=None
    ):
        file_ext = self._normalize_extension(os.path.splitext(src_path)[1])
        with Image.open(src_path) as img:
            img = img.convert("RGBA") if img.mode not in ("RGB", "RGBA") else img.copy()
            exif_data = img.info.get("exif") if preserve_metadata else None
            # EXIF智能写回
            if exif_edit and exif_data:
                try:
                    exif_dict = piexif.load(exif_data)
                    for k, v in exif_edit.items():
                        if k in exif_dict["0th"]:
                            exif_dict["0th"][k] = v
                    exif_data = piexif.dump(exif_dict)
                except Exception:
                    pass
            if crop_params:
                x, y, w, h = crop_params.get("x",0), crop_params.get("y",0), crop_params.get("w"), crop_params.get("h")
                img = img.crop((x, y, x+w, y+h)) if w and h else img
            if rotate:
                img = img.rotate(rotate, expand=True)
            if resize_enabled and resize_width and resize_height:
                img = self._resize_image(img, resize_width, resize_height, resize_mode, resize_only_shrink)
            if filter_type:
                img = self.apply_filter(img, filter_type)
            if watermark:
                img = self.apply_watermark(img, watermark)
            save_params = {}
            if target_ext:
                pil_format = self.format_mapping.get(target_ext)
                if pil_format:
                    save_params["format"] = pil_format
            if quality is not None:
                if target_ext in (".jpg", ".jpeg", ".webp"):
                    save_params["quality"] = max(1, min(100, quality))
                elif target_ext == ".png":
                    save_params["compress_level"] = min(9, max(0, 9 - quality // 11))
            if exif_data:
                save_params["exif"] = exif_data
            if target_ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
            img.save(dest_path, **save_params)

    def _resize_image(self, img, width, height, mode="fit", only_shrink=True):
        orig_w, orig_h = img.size
        if only_shrink and orig_w <= width and orig_h <= height:
            return img
        if mode == "fit":
            img_copy = img.copy()
            img_copy.thumbnail((width, height), Image.LANCZOS)
            return img_copy
        elif mode == "fill":
            ratio = max(width / orig_w, height / orig_h)
            new_size = (int(orig_w * ratio), int(orig_h * ratio))
            img2 = img.resize(new_size, Image.LANCZOS)
            left = (img2.width - width) // 2
            top = (img2.height - height) // 2
            return img2.crop((left, top, left + width, top + height))
        elif mode == "pad":
            img_copy = img.copy()
            img_copy.thumbnail((width, height), Image.LANCZOS)
            new_img = Image.new("RGBA", (width, height), (255,255,255,0))
            offset_x = (width - img_copy.width) // 2
            offset_y = (height - img_copy.height) // 2
            new_img.paste(img_copy, (offset_x, offset_y))
            return new_img
        elif mode == "crop":
            left = max(0, (orig_w - width) // 2)
            top = max(0, (orig_h - height) // 2)
            return img.crop((left, top, left + width, top + height))
        else:
            return img

    def _update_progress(self, callback, processed, total, filename=""):
        if callback:
            progress = int(processed / total * 100)
            progress = min(100, max(0, progress))  # 确保进度值在 [0, 100] 范围内
            callback(progress, filename)

    def apply_watermark(self, img, watermark: Dict[str, Any]):
        # 支持图片logo水印
        text = watermark.get("text")
        font_path = watermark.get("font", None)
        font_size = watermark.get("size", 32)
        color = watermark.get("color", (255,255,255,128))
        pos = watermark.get("pos", "bottom-right")
        logo_path = watermark.get("logo", None)
        logo_alpha = watermark.get("logo_alpha", 128)

        if img.mode != "RGBA":
            img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)

        # 文字水印
        if text:
            try:
                font = ImageFont.truetype(font_path or "arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            text_size = draw.textsize(text, font=font)
            margin = 10
            positions = {
                "bottom-right": (img.width - text_size[0] - margin, img.height - text_size[1] - margin),
                "bottom-left": (margin, img.height - text_size[1] - margin),
                "top-right": (img.width - text_size[0] - margin, margin),
                "top-left": (margin, margin),
                "center": ((img.width-text_size[0])//2, (img.height-text_size[1])//2)
            }
            xy = positions.get(pos, positions["bottom-right"])
            draw.text(xy, text, font=font, fill=color)

        # logo水印
        if logo_path and os.path.isfile(logo_path):
            try:
                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    # 缩放logo到图片宽度的1/6
                    scale = img.width // 6 / logo.width
                    logo = logo.resize((int(logo.width*scale), int(logo.height*scale)))
                    l_w, l_h = logo.size
                    # 位置与文字一致
                    margin = 10
                    positions = {
                        "bottom-right": (img.width - l_w - margin, img.height - l_h - margin),
                        "bottom-left": (margin, img.height - l_h - margin),
                        "top-right": (img.width - l_w - margin, margin),
                        "top-left": (margin, margin),
                        "center": ((img.width-l_w)//2, (img.height-l_h)//2)
                    }
                    xy = positions.get(pos, positions["bottom-right"])
                    # 设置透明度
                    alpha = logo.split()[3].point(lambda p: logo_alpha)
                    logo.putalpha(alpha)
                    overlay.paste(logo, xy, logo)
            except Exception:
                pass

        return Image.alpha_composite(img, overlay)

    def apply_filter(self, img, filter_type):
        if filter_type == "grayscale":
            return img.convert("L").convert("RGBA")
        elif filter_type == "sharpen":
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == "blur":
            return img.filter(ImageFilter.BLUR)
        elif filter_type == "contour":
            return img.filter(ImageFilter.CONTOUR)
        elif filter_type == "emboss":
            return img.filter(ImageFilter.EMBOSS)
        elif filter_type == "edge":
            return img.filter(ImageFilter.FIND_EDGES)
        elif filter_type == "enhance":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.5)
        else:
            return img

def find_duplicate_images(file_paths, threshold=8, method="phash"):
    """支持多种去重算法: phash(默认), ahash, dhash, colorhist"""
    hashes = {}
    groups = []
    for path in file_paths:
        try:
            with Image.open(path) as img:
                if method == "phash":
                    h = imagehash.phash(img)
                elif method == "ahash":
                    h = imagehash.average_hash(img)
                elif method == "dhash":
                    h = imagehash.dhash(img)
                elif method == "colorhist":
                    h = tuple(img.histogram())
                else:
                    h = imagehash.phash(img)
            hashes[path] = h
        except Exception:
            continue
    used = set()
    for path1, hash1 in hashes.items():
        if path1 in used:
            continue
        group = [path1]
        for path2, hash2 in hashes.items():
            if path2 != path1 and path2 not in used:
                # 支持 colorhist
                try:
                    dist = (hash1 - hash2) if hasattr(hash1, '__sub__') else sum(abs(a-b) for a,b in zip(hash1, hash2))//1000
                except Exception:
                    dist = 1000
                if dist <= threshold:
                    group.append(path2)
                    used.add(path2)
        if len(group) > 1:
            for p in group:
                used.add(p)
            groups.append(group)
    return groups

def get_exif_data(image_path):
    try:
        exif_dict = piexif.load(image_path)
        exif_data = {}
        for ifd in exif_dict:
            if isinstance(exif_dict[ifd], dict):
                for tag in exif_dict[ifd]:
                    tag_name = piexif.TAGS[ifd][tag]["name"]
                    value = exif_dict[ifd][tag]
                    if isinstance(value, bytes):
                        try:
                            value = value.decode()
                        except Exception:
                            value = str(value)
                    exif_data[tag_name] = value
        return exif_data
    except Exception:
        return {}

def get_image_main_color(image_path):
    try:
        ct = ColorThief(image_path)
        dom_color = ct.get_color(quality=1)
        palette = ct.get_palette(color_count=6)
        return dom_color, palette
    except Exception:
        return None, []

def plot_image_histogram(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        plt.figure(figsize=(4,1.5))
        color = ('r','g','b')
        for i,c in enumerate(color):
            histo = img.getchannel(i).histogram()
            plt.plot(histo, color=c, label=f"{c.upper()}")
        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None

def ocr_image(image_path, lang="chi_sim", auto_rotate=True):
    """OCR支持自动旋转和居中，提升准确率"""
    try:
        img = Image.open(image_path)
        if auto_rotate:
            try:
                osd = pytesseract.image_to_osd(img)
                if "Rotate: 90" in osd:
                    img = img.rotate(-90, expand=True)
                elif "Rotate: 180" in osd:
                    img = img.rotate(-180, expand=True)
                elif "Rotate: 270" in osd:
                    img = img.rotate(-270, expand=True)
            except Exception:
                pass
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except Exception as e:
        return f"OCR失败: {e}"

def smart_classify(image_path):
    try:
        img = Image.open(image_path)
        w, h = img.size
        if w > h*1.5:
            shape = "横幅"
        elif h > w*1.5:
            shape = "竖幅"
        else:
            shape = "方形"
        dom_color, _ = get_image_main_color(image_path)
        color_str = str(dom_color) if dom_color else "未知"
        return [shape, f"主色:{color_str}"]
    except Exception:
        return ["无法识别"]

def ai_image_recognition_cloud(file_paths, provider="baidu", **provider_kwargs):
    if provider == "baidu":
        return ai_recognition_baidu(file_paths, **provider_kwargs)
    elif provider == "deepseek":
        return ai_recognition_deepseek(file_paths, **provider_kwargs)
    else:
        return {path: ["未实现"] for path in file_paths}

def ai_recognition_baidu(file_paths, app_id=None, api_key=None, secret_key=None, **kwargs):
    try:
        from aip import AipImageClassify
    except ImportError:
        raise Exception("请先 pip install baidu-aip")
    if not app_id or not api_key or not secret_key:
        return {path: ["缺少API参数"] for path in file_paths}
    client = AipImageClassify(app_id, api_key, secret_key)
    results = {}
    for path in file_paths:
        with open(path, 'rb') as f:
            img_data = f.read()
        res = client.advancedGeneral(img_data)
        tags = [item['keyword'] for item in res.get('result', [])]
        results[path] = tags or ["未识别"]
    return results

def ai_recognition_deepseek(file_paths, api_key=None, endpoint=None, **kwargs):
    import requests
    if not api_key:
        return {path: ["缺少API参数"] for path in file_paths}
    results = {}
    for path in file_paths:
        with open(path, 'rb') as f:
            img_data = f.read()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/octet-stream"
        }
        allowed_endpoints = ["https://api.deepseek.com/v1/vision/detect"]
        url = endpoint if endpoint in allowed_endpoints else "https://api.deepseek.com/v1/vision/detect"
        try:
            response = requests.post(
                url,
                data=img_data,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            res = response.json()
            if "labels" in res:
                tags = res["labels"]
            elif "result" in res:
                tags = [item.get("label", "") for item in res["result"]]
            else:
                tags = ["未识别"]
            results[path] = tags or ["未识别"]
        except Exception as e:
            results[path] = [f"调用失败: {e}"]
    return results

def remove_background(image_path, output_path=None):
    with Image.open(image_path) as img:
        result = remove(img)
        if output_path:
            result.save(output_path)
        return result