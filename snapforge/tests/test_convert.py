# snapforge/tests/test_convert.py
import unittest
import os
import tempfile
from snapforge.core.convert_processor import ConvertProcessor
from snapforge.utils.image_utils import convert_image


class TestConvertProcessor(unittest.TestCase):

    def setUp(self) -> None:
        """在每个测试用例执行前创建临时测试文件。"""
        # 创建一个临时文件
        self.test_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        self.test_file.write(b"Test data")  # 写入一些测试数据
        self.test_file.close()
        self.file_path = self.test_file.name
        self.target_format = "png"
        self.converted_file_path = f"{os.path.splitext(self.file_path)[0]}.{self.target_format}"

    def tearDown(self) -> None:
        """在每个测试用例执行后删除临时测试文件。"""
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        if os.path.isfile(self.converted_file_path):
            os.remove(self.converted_file_path)

    def test_convert_image(self) -> None:
        """测试转换图像格式功能。"""
        try:
            convert_image(self.file_path, self.target_format)
            self.assertTrue(os.path.exists(self.converted_file_path))
        except Exception as e:
            self.fail(f"转换图像格式失败: {e}")

    def test_convert_processor(self) -> None:
        """测试转换处理器。"""
        processor = ConvertProcessor(target_format=self.target_format)
        result = processor.process(self.file_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.converted_file_path))
