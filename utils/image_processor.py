# utils/image_processor.py
import os
from PIL import Image
from . import error_handler

def batch_rename_files(source_dir, target_dir, prefix, start_number, progress_callback=None):
    """批量重命名图片文件。

    Args:
        source_dir (str): 源文件夹路径。
        target_dir (str): 目标文件夹路径。
        prefix (str): 文件名前缀。
        start_number (int): 起始编号。
        progress_callback (function, optional): 进度回调函数。默认为 None。

    Returns:
        int: 重命名文件的数量。
    """
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                continue

            old_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1]
            new_file_name = f"{prefix}{start_number + i}{file_extension}"
            new_path = os.path.join(target_dir, new_file_name)

            try:
                os.rename(old_path, new_path)
                count += 1
                if progress_callback:
                    progress_callback(i, len(files))  # 更新进度条
            except Exception as e:
                error_handler.handle_error(f"重命名文件 {file} 时出错: {e}")
    return count


def batch_convert_images(source_dir, target_dir, target_format, progress_callback=None):
    """批量转换图片格式。

    Args:
        source_dir (str): 源文件夹路径。
        target_dir (str): 目标文件夹路径。
        target_format (str): 目标图片格式。
        progress_callback (function, optional): 进度回调函数。默认为 None。

    Returns:
        int: 转换文件的数量。
    """
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                continue
            old_path = os.path.join(root, file)
            file_name = os.path.splitext(file)[0]
            new_file_name = f"{file_name}.{target_format}"
            new_path = os.path.join(target_dir, new_file_name)
            try:
                img = Image.open(old_path)
                img.save(new_path, target_format.upper())
                count += 1
                if progress_callback:
                    progress_callback(i, len(files))
            except Exception as e:
                error_handler.handle_error(f"转换文件 {file} 时出错: {e}")
    return count


def batch_compress_images(source_dir, target_dir, quality, progress_callback=None):
    """批量压缩图片。

    Args:
        source_dir (str): 源文件夹路径。
        target_dir (str): 目标文件夹路径。
        quality (int): 压缩质量 (1-100)。
        progress_callback (function, optional): 进度回调函数。默认为 None。

    Returns:
        int: 压缩文件的数量。
    """
    count = 0
    for root, _, files in os.walk(source_dir):
        for i, file in enumerate(files):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            old_path = os.path.join(root, file)
            new_path = os.path.join(target_dir, file)
            try:
                img = Image.open(old_path)
                img.save(new_path, optimize=True, quality=quality)
                count += 1
                if progress_callback:
                    progress_callback(i, len(files))
            except Exception as e:
                error_handler.handle_error(f"压缩文件 {file} 时出错: {e}")
    return count