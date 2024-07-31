# snapforge/plugins/plugin_manager.py
import importlib
import os
from .base_plugin import BasePlugin

class PluginManager:
    """插件管理器。"""

    def __init__(self):
        """初始化插件管理器。"""
        self.plugins = {}

    def load_plugins(self, plugin_dir="custom_plugins"):
        """加载插件。

        Args:
            plugin_dir (str, optional): 插件目录。Defaults to "custom_plugins".
        """
        # 获取插件目录的绝对路径
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), plugin_dir)

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                module_path = f"{plugin_dir}.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    for name, cls in module.__dict__.items():
                        if issubclass(cls, BasePlugin) and cls is not BasePlugin:
                            self.plugins[name] = cls()
                            print(f"加载插件：{name}")
                except Exception as e:
                    print(f"加载插件失败：{e}")

    def unload_plugin(self, plugin_name):
        """卸载插件。

        Args:
            plugin_name (str): 插件名称。
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            print(f"卸载插件：{plugin_name}")

    def get_plugin(self, plugin_name):
        """获取插件。

        Args:
            plugin_name (str): 插件名称。

        Returns:
            BasePlugin: 插件对象。
        """
        return self.plugins.get(plugin_name)

    def run_plugin(self, plugin_name, image_path, *args, **kwargs):
        """执行插件。

        Args:
            plugin_name (str): 插件名称。
            image_path (str): 图像文件路径。
            *args: 可变参数。
            **kwargs: 关键字参数。
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            try:
                plugin.run(image_path, *args, **kwargs)
                print(f"执行插件：{plugin_name}")
            except Exception as e:
                print(f"执行插件失败：{e}")
        else:
            print(f"插件 '{plugin_name}' 不存在。")