# snapforge/utils/image_utils.py
import os

import cv2
from PIL import Image


def resize_image(image_path, width, height):
    """调整图像尺寸。

    Args:
        image_path (str): 图像文件路径。
        width (int): 新宽度。
        height (int): 新高度。
    """
    try:
        image = Image.open(image_path)
        image = image.resize((width, height))
        image.save(image_path)
    except Exception as e:
        print(f"调整图像尺寸失败：{e}")


def compress_image(image_path, quality):
    """压缩图像。

    Args:
        image_path (str): 图像文件路径。
        quality (int): 压缩质量 (0-100)，值越低压缩率越高。
    """
    try:
        image = cv2.imread(image_path)
        extension = get_file_extension(image_path)
        if extension.lower() == "jpg" or extension.lower() == "jpeg":
            cv2.imwrite(image_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        else:
            cv2.imwrite(image_path, image)
    except Exception as e:
        print(f"压缩图像失败：{e}")


def convert_image(image_path, target_format):
    """转换图像格式。

    Args:
        image_path (str): 图像文件路径。
        target_format (str): 目标格式，例如 "png"、"jpg"。
    """
    try:
        image = Image.open(image_path)
        image.save(image_path.replace(get_file_extension(image_path), f".{target_format}"), target_format)
    except Exception as e:
        print(f"转换图像格式失败：{e}")


def get_file_extension(file_path):
    """获取文件扩展名。

    Args:
        file_path (str): 文件路径。

    Returns:
        str: 文件扩展名，不含点号。
    """
    return os.path.splitext(file_path)[1][1:]
