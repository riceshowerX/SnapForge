# custom_plugin_example.py

from snapforge.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def run(self, image_path, *args, **kwargs):
        # 在这里实现你的自定义插件功能
        print(f"处理图像：{image_path}")