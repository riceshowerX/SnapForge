# custom_plugin_example.py
import logging
from snapforge.plugins.base_plugin import BasePlugin


# 设置日志配置
logging.basicConfig(level=logging.INFO)


class MyPlugin(BasePlugin):
    """自定义插件示例。"""

    def run(self, image_path: str, *args, **kwargs) -> None:
        """处理图像的自定义功能。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。
        """
        # 在这里实现你的自定义插件功能
        logging.info(f"处理图像：{image_path}")
