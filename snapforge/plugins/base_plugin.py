# snapforge/plugins/base_plugin.py
class BasePlugin:
    """插件基类。"""

    def run(self, image_path: str, *args, **kwargs) -> None:
        """执行插件功能。

        Args:
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。

        Raises:
            NotImplementedError: 如果子类没有实现该方法，将引发此异常。
        """
        raise NotImplementedError("请实现 run 方法。")
