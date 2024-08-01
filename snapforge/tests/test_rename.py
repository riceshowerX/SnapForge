# snapforge/tests/test_rename.py
import os
import tempfile
import unittest

from snapforge.core.rename_processor import RenameProcessor
from snapforge.utils.file_utils import rename_file


class TestRenameProcessor(unittest.TestCase):

    def setUp(self) -> None:
        """在每个测试用例执行前创建临时文件。"""
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        # 创建临时文件
        self.old_file_path = os.path.join(self.test_dir, "test.jpg")
        with open(self.old_file_path, "wb") as f:
            f.write(b"dummy content")  # 写入一些内容以创建文件

    def tearDown(self) -> None:
        """在每个测试用例执行后删除临时目录及文件。"""
        try:
            os.remove(self.old_file_path)
        except Exception as e:
            print(f"删除测试文件失败: {e}")
        finally:
            try:
                os.rmdir(self.test_dir)
            except Exception as e:
                print(f"删除测试目录失败: {e}")

    def test_rename_file(self) -> None:
        """测试重命名文件功能。"""
        new_name_prefix = "new_"
        new_name_suffix = "_renamed"
        expected_new_name = os.path.join(self.test_dir, f"{new_name_prefix}test{new_name_suffix}.jpg")

        actual_new_name = rename_file(self.old_file_path, new_name_prefix, new_name_suffix)
        self.assertEqual(actual_new_name, expected_new_name)
        self.assertTrue(os.path.exists(expected_new_name))
        self.assertFalse(os.path.exists(self.old_file_path))

    def test_rename_processor(self) -> None:
        """测试重命名处理器。"""
        processor = RenameProcessor(new_name_prefix="new_", new_name_suffix="_renamed")
        result = processor.process(self.old_file_path)
        self.assertTrue(result)

        new_name = os.path.join(self.test_dir, "new_test_renamed.jpg")
        self.assertTrue(os.path.exists(new_name))
        self.assertFalse(os.path.exists(self.old_file_path))
