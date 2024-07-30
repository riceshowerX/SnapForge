# main.py
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
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
        return self.root

    def select_source(self, instance):
        content = FileChooserIconView()
        content.bind(on_submit=self._on_file_selected)
        self._popup = Popup(title="选择图片文件", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def _on_file_selected(self, filechooser, selection, *args):
        if selection:
            self.source_file = os.path.abspath(selection[0])
            self.root.ids.source_button.text = f'已选择: {self.source_file}'
        self._popup.dismiss()

    def select_target_directory(self, instance):
        content = FileChooserListView(path='/', filters=['*'])
        content.bind(on_submit=self._on_directory_selected)
        self._popup = Popup(title="选择保存图片文件夹", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def _on_directory_selected(self, filechooser, selection, *args):
        if selection:
            self.target_directory = os.path.abspath(selection[0])
            self.root.ids.target_button.text = f'已选择: {self.target_directory}'
        self._popup.dismiss()

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
        self.root.ids.progress_bar.value = self.progress_value

    def show_info_message(self, message):
        self.root.ids.status_label.text = message

    def show_error_message(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        close_button = Button(text="关闭")
        close_button.bind(on_press=self._close_popup)
        content.add_widget(close_button)
        self._popup = Popup(title="错误", content=content, size_hint=(0.8, 0.4))
        self._popup.open()

    def _close_popup(self, instance):
        self._popup.dismiss()

if __name__ == "__main__":
    SnapForgeApp().run()
