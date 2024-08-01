# snapforge/core/compress_processor.py
import logging

from .base_processor import BaseProcessor
from ..utils import image_utils

# 设置日志配置
logging.basicConfig(level=logging.INFO)


class CompressProcessor(BaseProcessor):
    """压缩处理器。"""

    def __init__(self, quality: int):
        """初始化压缩处理器。

        Args:
            quality (int): 压缩质量 (0-100)，值越低压缩率越高。
        """
        self.quality = quality

    def process(self, image_path: str, *args, **kwargs) -> bool:
        """压缩图像。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。

        Returns:
            bool: 处理是否成功。
        """
        try:
            image_utils.compress_image(image_path, self.quality)
            logging.info(f"压缩图像：{image_path}")
            return True
        except FileNotFoundError:
            logging.error(f"图像文件未找到：{image_path}")
            return False
        except ValueError as ve:
            logging.error(f"无效的压缩质量：{ve}")
            return False
        except Exception as e:
            logging.error(f"压缩图像失败：{e}")
            return False
