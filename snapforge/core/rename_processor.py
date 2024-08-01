# snapforge/core/rename_processor.py
import logging

from .base_processor import BaseProcessor
from ..utils import file_utils

# 设置日志配置
logging.basicConfig(level=logging.INFO)


class RenameProcessor(BaseProcessor):
    """重命名处理器。"""

    def __init__(self, new_name_prefix: str = None, new_name_suffix: str = None):
        """初始化重命名处理器。

        Args:
            new_name_prefix (str, optional): 新文件名前缀。默认为 None。
            new_name_suffix (str, optional): 新文件名后缀。默认为 None。
        """
        self.new_name_prefix = new_name_prefix
        self.new_name_suffix = new_name_suffix

    def process(self, image_path: str, *args, **kwargs) -> bool:
        """重命名图像。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。

        Returns:
            bool: 处理是否成功。
        """
        try:
            new_name = file_utils.rename_file(image_path, self.new_name_prefix, self.new_name_suffix)
            logging.info(f"重命名图像：{image_path} -> {new_name}")
            return True
        except Exception as e:
            logging.error(f"重命名图像失败：{e}")
            return False
