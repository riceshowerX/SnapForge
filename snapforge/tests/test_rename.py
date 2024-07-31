# snapforge/tests/test_rename.py
import unittest
from ..core.rename_processor import RenameProcessor
from ..utils.file_utils import rename_file

class TestRenameProcessor(unittest.TestCase):
    def test_rename_file(self):
        """测试重命名文件功能。"""
        file_path = "test.jpg"
        new_name_prefix = "new_"
        new_name_suffix = "_renamed"
        expected_new_name = f"{new_name_prefix}test{new_name_suffix}.jpg"
        actual_new_name = rename_file(file_path, new_name_prefix, new_name_suffix)
        self.assertEqual(actual_new_name, expected_new_name)

    def test_rename_processor(self):
        """测试重命名处理器。"""
        processor = RenameProcessor(new_name_prefix="new_", new_name_suffix="_renamed")
        self.assertTrue(processor.process("test.jpg"))