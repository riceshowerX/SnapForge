# main.py
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform

from core import ImageProcessor, Config
from kivy_ui.main_window import MainWindow

# 加载 KV 文件
Builder.load_file("kivy_ui/main_window.kv")

Window.clearcolor = (1, 1, 1, 1)  # 设置背景颜色为白色


class SnapForgeApp(App):
    source_directory = StringProperty(None)
    target_directory = StringProperty(None)
    source_file = StringProperty(None)
    progress_value = NumericProperty(0)
    config = Config()
    image_processor = ImageProcessor(config)

    def build(self):
        self.root = MainWindow()
        self.root.ids.source_button.bind(on_press=self.select_source)
        self.root.ids.target_button.bind(on_press=self.select_target_directory)
        self.root.ids.rename_button.bind(on_press=self.rename_files)
        self.root.ids.convert_button.bind(on_press=self.convert_files)
        self.root.ids.compress_button.bind(on_press=self.compress_files)
        self.root.ids.progress_bar.bind(value=self.progress_value)
        return self.root

    def select_source(self, instance):
        if platform == 'android':
            # Android平台文件选择
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            FileChooser = autoclass('androidx.activity.result.contract.ActivityResultContracts$StartActivityForResult')
            startActivityForResult = autoclass('androidx.activity.ComponentActivity').registerForActivityResult(
                FileChooser(), self.on_file_selected)
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")
            startActivityForResult.launch(intent)
        else:
            # 其他平台文件选择
            self.source_file = os.path.abspath(os.path.expanduser(os.path.join('~', "Documents")))
            self.root.ids.source_button.text = '已选择: {}'.format(self.source_file)

    def on_file_selected(self, data):
        if data is not None:
            self.source_file = data.getDataString()
            self.root.ids.source_button.text = '已选择: {}'.format(self.source_file)

    def select_target_directory(self, instance):
        if platform == 'android':
            # Android平台文件夹选择
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            FileChooser = autoclass('androidx.activity.result.contract.ActivityResultContracts$StartActivityForResult')
            startActivityForResult = autoclass('androidx.activity.ComponentActivity').registerForActivityResult(
                FileChooser(), self.on_directory_selected)
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            startActivityForResult.launch(intent)
        else:
            # 其他平台文件夹选择
            self.target_directory = os.path.abspath(os.path.expanduser(os.path.join('~', "Documents")))
            self.root.ids.target_button.text = '已选择: {}'.format(self.target_directory)

    def on_directory_selected(self, data):
        if data is not None:
            self.target_directory = data.getDataString()
            self.root.ids.target_button.text = '已选择: {}'.format(self.target_directory)

    def rename_files(self, instance):
        if not self.source_file or not self.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        prefix = self.root.ids.prefix_input.text
        try:
            start_number = int(self.root.ids.start_number_input.text)
        except ValueError:
            self.show_error_message("起始编号必须是一个整数！")
            return

        self.progress_value = 0
        renamed_count = self.image_processor.batch_rename_files(
            self.source_file,
            self.target_directory,
            prefix,
            start_number,
            self.update_progress
        )
        self.show_info_message(f"重命名完成！共重命名了 {renamed_count} 个文件。")

    def convert_files(self, instance):
        if not self.source_file or not self.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        target_format = self.root.ids.format_input.text
        if not target_format:
            self.show_error_message("请指定目标格式！")
            return

        self.progress_value = 0
        converted_count = self.image_processor.batch_convert_images(
            self.source_file,
            self.target_directory,
            target_format,
            self.update_progress
        )
        self.show_info_message(f"转换完成！共转换了 {converted_count} 个文件。")

    def compress_files(self, instance):
        if not self.source_file or not self.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        try:
            quality = int(self.root.ids.quality_input.text)
        except ValueError:
            self.show_error_message("压缩质量必须是一个整数！")
            return

        self.progress_value = 0
        compressed_count = self.image_processor.batch_compress_images(
            self.source_file,
            self.target_directory,
            quality,
            self.update_progress
        )
        self.show_info_message(f"压缩完成！共压缩了 {compressed_count} 个文件。")

    def update_progress(self, current, total):
        self.progress_value = (current / total) * 100

    def show_info_message(self, message):
        self.root.ids.status_label.text = message

    def show_error_message(self, message):
        self.root.ids.status_label.text = message
        # 可以使用其他方式显示错误信息，例如弹窗


if __name__ == "__main__":
    SnapForgeApp().run()