# utils/image_processor.py
import os
from PIL import Image
from . import error_handler

def rename_file(source_file, target_dir, prefix, start_number):
    try:
        file_extension = os.path.splitext(source_file)[1]
        new_file_name = f"{prefix}{start_number}{file_extension}"
        new_path = os.path.join(target_dir, new_file_name)
        os.rename(source_file, new_path)
        return new_path
    except Exception as e:
        error_handler.handle_error(f"重命名文件 {source_file} 时出错: {e}")
        return None

def batch_rename_files(source_dir, target_dir, prefix, start_number, progress_callback=None):
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                continue

            old_path = os.path.join(root, file)
            new_path = rename_file(old_path, target_dir, prefix, start_number + i)
            if new_path:
                count += 1
                if progress_callback:
                    progress_callback(i + 1, len(files))  # 更新进度条
    return count

def convert_file(source_file, target_dir, target_format):
    try:
        file_name = os.path.splitext(os.path.basename(source_file))[0]
        new_file_name = f"{file_name}.{target_format}"
        new_path = os.path.join(target_dir, new_file_name)
        img = Image.open(source_file)
        img.save(new_path, target_format.upper())
        return new_path
    except Exception as e:
        error_handler.handle_error(f"转换文件 {source_file} 时出错: {e}")
        return None

def batch_convert_images(source_dir, target_dir, target_format, progress_callback=None):
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                continue
            old_path = os.path.join(root, file)
            new_path = convert_file(old_path, target_dir, target_format)
            if new_path:
                count += 1
                if progress_callback:
                    progress_callback(i + 1, len(files))
    return count

def compress_file(source_file, target_dir, quality):
    try:
        new_path = os.path.join(target_dir, os.path.basename(source_file))
        img = Image.open(source_file)
        img.save(new_path, optimize=True, quality=quality)
        return new_path
    except Exception as e:
        error_handler.handle_error(f"压缩文件 {source_file} 时出错: {e}")
        return None

def batch_compress_images(source_dir, target_dir, quality, progress_callback=None):
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            old_path = os.path.join(root, file)
            new_path = compress_file(old_path, target_dir, quality)
            if new_path:
                count += 1
                if progress_callback:
                    progress_callback(i + 1, len(files))
    return count