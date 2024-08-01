# snapforge/plugins/plugin_manager.py
import importlib
import os
import logging
from .base_plugin import BasePlugin
from typing import Optional, Dict, Any


# 设置日志配置
logging.basicConfig(level=logging.INFO)


class PluginManager:
    """插件管理器。"""

    def __init__(self):
        """初始化插件管理器。"""
        self.plugins: Dict[str, BasePlugin] = {}

    def load_plugins(self, plugin_dir: str = "custom_plugins") -> None:
        """加载插件。

        Args:
            plugin_dir (str, optional): 插件目录。默认为 "custom_plugins"。
        """
        # 获取插件目录的绝对路径
        plugin_dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), plugin_dir)

        for filename in os.listdir(plugin_dir_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module_path = f"{plugin_dir}.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    for name, cls in module.__dict__.items():
                        if isinstance(cls, type) and issubclass(cls, BasePlugin) and cls is not BasePlugin:
                            self.plugins[name] = cls()
                            logging.info(f"加载插件：{name}")
                except Exception as e:
                    logging.error(f"加载插件失败：{e}")

    def unload_plugin(self, plugin_name: str) -> None:
        """卸载插件。

        Args:
            plugin_name (str): 插件名称。
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logging.info(f"卸载插件：{plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件。

        Args:
            plugin_name (str): 插件名称。

        Returns:
            Optional[BasePlugin]: 插件对象，如果插件存在则返回，否则返回 None。
        """
        return self.plugins.get(plugin_name)

    def run_plugin(self, plugin_name: str, image_path: str, *args: Any, **kwargs: Any) -> None:
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
                logging.info(f"执行插件：{plugin_name}")
            except Exception as e:
                logging.error(f"执行插件失败：{e}")
        else:
            logging.warning(f"插件 '{plugin_name}' 不存在。")
