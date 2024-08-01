# snapforge/tests/test_compress.py
import os
import tempfile
import unittest

from snapforge.core.compress_processor import CompressProcessor
from snapforge.utils.image_utils import compress_image


class TestCompressProcessor(unittest.TestCase):

    def setUp(self) -> None:
        """在每个测试用例执行前创建临时测试文件。"""
        # 创建一个临时文件
        self.test_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        self.test_file.write(b"Test data")  # 写入一些测试数据
        self.test_file.close()
        self.file_path = self.test_file.name
        self.quality = 50

    def tearDown(self) -> None:
        """在每个测试用例执行后删除临时测试文件。"""
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    def test_compress_image(self) -> None:
        """测试压缩图像功能。"""
        try:
            compress_image(self.file_path, self.quality)
            # 断言压缩功能是否按预期工作（需要根据实际实现来调整断言）
            self.assertTrue(os.path.isfile(self.file_path))
        except Exception as e:
            self.fail(f"压缩图像失败: {e}")

    def test_compress_processor(self) -> None:
        """测试压缩处理器。"""
        processor = CompressProcessor(quality=self.quality)
        result = processor.process(self.file_path)
        self.assertTrue(result)
        # 你可以进一步添加断言来验证处理后的结果，例如检查文件大小
