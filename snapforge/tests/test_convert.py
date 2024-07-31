# snapforge/tests/test_convert.py
import unittest
import os
from ..core.convert_processor import ConvertProcessor
from ..utils.image_utils import convert_image

class TestConvertProcessor(unittest.TestCase):
    def test_convert_image(self):
        """测试转换图像格式功能。"""
        file_path = "test.jpg"
        target_format = "png"
        convert_image(file_path, target_format)
        self.assertTrue(os.path.exists(f"test.png"))

    def test_convert_processor(self):
        """测试转换处理器。"""
        processor = ConvertProcessor(target_format="png")
        self.assertTrue(processor.process("test.jpg"))