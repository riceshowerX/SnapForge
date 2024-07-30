# main_window.py
import os
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty
from kivy.core.text import LabelBase
from core import ImageProcessor, Config

# 注册自定义字体
LabelBase.register(name='SimHei', fn_regular=r'C:\Windows\Fonts\BRLNSR.TTF')  # 替换为字体文件的实际路径

class MainWindow(Widget):
    source_directory = StringProperty(None)
    target_directory = StringProperty(None)
    source_file = StringProperty(None)
    progress_value = NumericProperty(0)
    config = Config()
    image_processor = ImageProcessor(config)

    def select_source(self, instance):
        # 其他平台文件选择
        self.source_file = os.path.abspath(os.path.expanduser(os.path.join('~', "Documents")))
        self.ids.source_button.text = '已选择: {}'.format(self.source_file)

    def select_target_directory(self, instance):
        # 其他平台文件夹选择
        self.target_directory = os.path.abspath(os.path.expanduser(os.path.join('~', "Documents")))
        self.ids.target_button.text = '已选择: {}'.format(self.target_directory)

    def rename_files(self, instance):
        if not self.source_file or not self.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        prefix = self.ids.prefix_input.text
        try:
            start_number = int(self.ids.start_number_input.text)
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

        target_format = self.ids.format_input.text
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
            quality = int(self.ids.quality_input.text)
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
        self.ids.status_label.text = message

    def show_error_message(self, message):
        self.ids.status_label.text = message
        # 可以使用其他方式显示错误信息，例如弹窗
