# main.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.button import Button
from core import ImageProcessor, Config

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 使用正确的路径加载 .kv 文件
kv_path = os.path.join(current_dir, "kivy_ui", "main_window.kv")
Builder.load_file(kv_path)


class MainWindow(BoxLayout):
    source_directory = StringProperty(None)
    target_directory = StringProperty(None)
    source_file = StringProperty(None)
    progress_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.config = Config()
        self.image_processor = ImageProcessor(self.config)


class SnapForgeApp(App):
    def build(self):
        self.root = MainWindow()
        Clock.schedule_once(self.bind_buttons)
        return self.root

    def bind_buttons(self, dt):
        self.root.ids.source_button.bind(on_press=self.select_source)
        self.root.ids.target_button.bind(on_press=self.select_target_directory)
        self.root.ids.rename_button.bind(on_press=self.rename_files)
        self.root.ids.convert_button.bind(on_press=self.convert_files)
        self.root.ids.compress_button.bind(on_press=self.compress_files)

    def select_source(self, instance):
        content = FileChooserListView(path=os.path.expanduser("~"))
        content.bind(on_submit=self._on_file_selected)
        self._popup = Popup(title="选择图片文件", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def select_target_directory(self, instance):
        content = FileChooserListView(path=os.path.expanduser("~"), dirselect=True)
        content.bind(on_submit=self._on_directory_selected)
        self._popup = Popup(title="选择保存图片文件夹", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def _on_file_selected(self, instance, selection, touch):
        if selection:
            self.root.source_file = selection[0]
            self.root.ids.source_button.text = f'已选择: {os.path.basename(self.root.source_file)}'
        self._popup.dismiss()

    def _on_directory_selected(self, instance, selection, touch):
        if selection:
            self.root.target_directory = selection[0]
            self.root.ids.target_button.text = f'已选择: {os.path.basename(self.root.target_directory)}'
        self._popup.dismiss()

    def rename_files(self, instance):
        if not self.root.source_file or not self.root.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        prefix = self.root.ids.prefix_input.text
        try:
            start_number = int(self.root.ids.start_number_input.text)
        except ValueError:
            self.show_error_message("起始编号必须是一个整数！")
            return

        self.root.progress_value = 0
        try:
            renamed_count = self.root.image_processor.batch_rename_files(
                self.root.source_file,
                self.root.target_directory,
                prefix,
                start_number,
                self.update_progress
            )
            self.show_info_message(f"重命名完成！共重命名了 {renamed_count} 个文件。")
        except Exception as e:
            self.show_error_message(f"重命名失败: {str(e)}")

    def convert_files(self, instance):
        if not self.root.source_file or not self.root.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        target_format = self.root.ids.format_input.text
        if not target_format:
            self.show_error_message("请指定目标格式！")
            return

        self.root.progress_value = 0
        try:
            converted_count = self.root.image_processor.batch_convert_images(
                self.root.source_file,
                self.root.target_directory,
                target_format,
                self.update_progress
            )
            self.show_info_message(f"转换完成！共转换了 {converted_count} 个文件。")
        except Exception as e:
            self.show_error_message(f"转换失败: {str(e)}")

    def compress_files(self, instance):
        if not self.root.source_file or not self.root.target_directory:
            self.show_error_message("请先选择原始图片文件和保存图片文件夹！")
            return

        try:
            quality = int(self.root.ids.quality_input.text)
            if quality < 1 or quality > 100:
                raise ValueError("质量值必须在1到100之间")
        except ValueError as e:
            self.show_error_message(f"无效的压缩质量: {str(e)}")
            return

        self.root.progress_value = 0
        try:
            compressed_count = self.root.image_processor.batch_compress_images(
                self.root.source_file,
                self.root.target_directory,
                quality,
                self.update_progress
            )
            self.show_info_message(f"压缩完成！共压缩了 {compressed_count} 个文件。")
        except Exception as e:
            self.show_error_message(f"压缩失败: {str(e)}")

    def update_progress(self, current, total):
        self.root.progress_value = (current / total) * 100
        self.root.ids.progress_bar.value = self.root.progress_value

    def show_info_message(self, message):
        self.root.ids.status_label.text = message

    def show_error_message(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        button = Button(text="确定", size_hint=(1, 0.2))
        content.add_widget(button)
        popup = Popup(title="错误", content=content, size_hint=(0.7, 0.3))
        button.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    SnapForgeApp().run()