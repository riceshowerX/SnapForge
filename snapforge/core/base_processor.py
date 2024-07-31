# snapforge/core/base_processor.py
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """图像处理器的基类。"""

    @abstractmethod
    def process(self, image_path, *args, **kwargs):
        """处理图像。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。

        Returns:
            bool: 处理是否成功。
        """
        pass