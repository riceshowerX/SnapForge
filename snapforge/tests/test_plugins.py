# snapforge/tests/test_plugins.py
import os
import shutil
import tempfile
import unittest

from snapforge.plugins.base_plugin import BasePlugin
from snapforge.plugins.plugin_manager import PluginManager


class TestPlugin(BasePlugin):
    """用于测试的插件。"""

    def run(self, image_path, *args, **kwargs):
        """执行插件功能。"""
        print(f"处理图像：{image_path}")


class TestPluginManager(unittest.TestCase):

    def setUp(self) -> None:
        """在每个测试用例执行前创建临时插件目录和插件文件。"""
        # 创建临时目录
        self.test_plugin_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()

        # 创建插件文件
        self.plugin_file_path = os.path.join(self.test_plugin_dir, "test_plugin.py")
        with open(self.plugin_file_path, "w") as f:
            f.write("""
from snapforge.plugins.base_plugin import BasePlugin

class TestPlugin(BasePlugin):
    def run(self, image_path, *args, **kwargs):
        print(f"处理图像：{image_path}")
""")

    def tearDown(self) -> None:
        """在每个测试用例执行后删除临时插件目录。"""
        shutil.rmtree(self.test_plugin_dir, ignore_errors=True)

    def test_load_plugins(self) -> None:
        """测试加载插件功能。"""
        self.plugin_manager.load_plugins(self.test_plugin_dir)
        self.assertIn("TestPlugin", self.plugin_manager.plugins)

    def test_unload_plugin(self) -> None:
        """测试卸载插件功能。"""
        self.plugin_manager.load_plugins(self.test_plugin_dir)
        self.plugin_manager.unload_plugin("TestPlugin")
        self.assertNotIn("TestPlugin", self.plugin_manager.plugins)

    def test_get_plugin(self) -> None:
        """测试获取插件功能。"""
        self.plugin_manager.load_plugins(self.test_plugin_dir)
        plugin = self.plugin_manager.get_plugin("TestPlugin")
        self.assertIsInstance(plugin, TestPlugin)

    def test_run_plugin(self) -> None:
        """测试执行插件功能。"""
        self.plugin_manager.load_plugins(self.test_plugin_dir)
        try:
            self.plugin_manager.run_plugin("TestPlugin", "test.jpg")
            # 检查输出（可以使用 mock 来验证输出内容）
        except Exception as e:
            self.fail(f"执行插件失败: {e}")
