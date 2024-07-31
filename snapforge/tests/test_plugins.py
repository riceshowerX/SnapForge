# snapforge/tests/test_plugins.py
import unittest
from ..plugins.plugin_manager import PluginManager
from ..plugins.base_plugin import BasePlugin

class TestPlugin(BasePlugin):
    def run(self, image_path, *args, **kwargs):
        print(f"处理图像：{image_path}")

class TestPluginManager(unittest.TestCase):
    def test_load_plugins(self):
        """测试加载插件功能。"""
        plugin_manager = PluginManager()
        plugin_manager.load_plugins("tests/plugins")
        self.assertIn("TestPlugin", plugin_manager.plugins)

    def test_unload_plugin(self):
        """测试卸载插件功能。"""
        plugin_manager = PluginManager()
        plugin_manager.load_plugins("tests/plugins")
        plugin_manager.unload_plugin("TestPlugin")
        self.assertNotIn("TestPlugin", plugin_manager.plugins)

    def test_get_plugin(self):
        """测试获取插件功能。"""
        plugin_manager = PluginManager()
        plugin_manager.load_plugins("tests/plugins")
        plugin = plugin_manager.get_plugin("TestPlugin")
        self.assertIsInstance(plugin, TestPlugin)

    def test_run_plugin(self):
        """测试执行插件功能。"""
        plugin_manager = PluginManager()
        plugin_manager.load_plugins("tests/plugins")
        plugin_manager.run_plugin("TestPlugin", "test.jpg")