# snapforge/core/convert_processor.py
import logging

from .base_processor import BaseProcessor
from ..utils import image_utils

# 设置日志配置
logging.basicConfig(level=logging.INFO)


class ConvertProcessor(BaseProcessor):
    """转换处理器。"""

    def __init__(self, target_format: str):
        """初始化转换处理器。

        Args:
            target_format (str): 目标格式，例如 "png"、"jpg"。
        """
        self.target_format = target_format

    def process(self, image_path: str, *args, **kwargs) -> bool:
        """转换图像格式。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。

        Returns:
            bool: 处理是否成功。
        """
        try:
            image_utils.convert_image(image_path, self.target_format)
            logging.info(f"转换图像格式：{image_path} -> {self.target_format}")
            return True
        except Exception as e:
            logging.error(f"转换图像格式失败：{e}")
            return False
