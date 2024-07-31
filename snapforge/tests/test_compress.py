# snapforge/tests/test_compress.py
import unittest
from ..core.compress_processor import CompressProcessor
from ..utils.image_utils import compress_image

class TestCompressProcessor(unittest.TestCase):
    def test_compress_image(self):
        """测试压缩图像功能。"""
        file_path = "test.jpg"
        quality = 50
        compress_image(file_path, quality)

    def test_compress_processor(self):
        """测试压缩处理器。"""
        processor = CompressProcessor(quality=50)
        self.assertTrue(processor.process("test.jpg"))