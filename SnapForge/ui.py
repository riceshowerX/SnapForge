from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PIL import Image
import os


def batch_rename(directory, prefix, start_number=1, extension=".jpg", convert_format=None, compress_quality=None):
    extension = extension.lower()
    count = start_number
    for filename in os.listdir(directory):
        if filename.lower().endswith(extension):
            src = os.path.join(directory, filename)

            # 处理文件名
            if prefix:
                new_extension = convert_format.lower() if convert_format else extension
                if not new_extension.startswith("."):
                    new_extension = f".{new_extension}"

                dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

                while os.path.exists(dst):
                    count += 1
                    dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

                # 处理图片格式转换和质量压缩
                if convert_format or compress_quality is not None:
                    with Image.open(src) as img:
                        if convert_format:
                            if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")
                        if compress_quality is not None:
                            img.save(dst, quality=compress_quality)
                        else:
                            img.save(dst)
                else:
                    os.rename(src, dst)

                # 删除源文件
                try:
                    os.remove(src)
                except PermissionError:
                    print(f"无法删除文件 {src}，权限不足或文件被占用。")

                count += 1

    return count - start_number


class BatchRenameApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片批量处理工具")
        self.setGeometry(300, 300, 500, 400)
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # 目录选择
        self.directory_label = QLabel("选择目录:")
        layout.addWidget(self.directory_label)

        self.directory_input = QLineEdit()
        layout.addWidget(self.directory_input)

        self.directory_button = QPushButton("浏览")
        self.directory_button.clicked.connect(self.browse_directory)
        layout.addWidget(self.directory_button)

        # 启用重命名
        self.rename_checkbox = QCheckBox("启用重命名")
        layout.addWidget(self.rename_checkbox)

        # 文件名前缀
        self.prefix_label = QLabel("文件名前缀:")
        layout.addWidget(self.prefix_label)

        self.prefix_input = QLineEdit()
        layout.addWidget(self.prefix_input)

        # 起始编号
        self.start_number_label = QLabel("起始编号:")
        layout.addWidget(self.start_number_label)

        self.start_number_input = QLineEdit()
        self.start_number_input.setText("1")
        layout.addWidget(self.start_number_input)

        # 文件扩展名
        self.extension_label = QLabel("文件扩展名:")
        layout.addWidget(self.extension_label)

        self.extension_input = QLineEdit()
        self.extension_input.setText(".jpg")
        layout.addWidget(self.extension_input)

        # 启用格式转换
        self.convert_format_checkbox = QCheckBox("启用格式转换")
        self.convert_format_checkbox.stateChanged.connect(self.toggle_format_input)
        layout.addWidget(self.convert_format_checkbox)

        self.convert_format_label = QLabel("目标格式:")
        self.convert_format_label.setEnabled(False)
        layout.addWidget(self.convert_format_label)

        self.convert_format_input = QLineEdit()
        self.convert_format_input.setEnabled(False)
        layout.addWidget(self.convert_format_input)

        # 启用质量压缩
        self.compress_checkbox = QCheckBox("启用质量压缩")
        self.compress_checkbox.stateChanged.connect(self.toggle_compress_input)
        layout.addWidget(self.compress_checkbox)

        self.compress_quality_label = QLabel("压缩质量 (0-100):")
        self.compress_quality_label.setEnabled(False)
        layout.addWidget(self.compress_quality_label)

        self.compress_quality_input = QLineEdit()
        self.compress_quality_input.setEnabled(False)
        self.compress_quality_input.setText("85")
        layout.addWidget(self.compress_quality_input)

        # 开始处理按钮
        self.process_button = QPushButton("开始处理")
        self.process_button.clicked.connect(self.start_processing)
        layout.addWidget(self.process_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.directory_input.setText(directory)

    def toggle_format_input(self):
        if self.convert_format_checkbox.isChecked():
            self.convert_format_label.setEnabled(True)
            self.convert_format_input.setEnabled(True)
        else:
            self.convert_format_label.setEnabled(False)
            self.convert_format_input.setEnabled(False)

    def toggle_compress_input(self):
        if self.compress_checkbox.isChecked():
            self.compress_quality_label.setEnabled(True)
            self.compress_quality_input.setEnabled(True)
        else:
            self.compress_quality_label.setEnabled(False)
            self.compress_quality_input.setEnabled(False)

    def start_processing(self):
        directory = self.directory_input.text()
        prefix = self.prefix_input.text() if self.rename_checkbox.isChecked() else None
        start_number = int(self.start_number_input.text()) if self.rename_checkbox.isChecked() else 1
        extension = self.extension_input.text()
        convert_format = self.convert_format_input.text() if self.convert_format_checkbox.isChecked() else None
        compress_quality = int(self.compress_quality_input.text()) if self.compress_checkbox.isChecked() else None

        if not os.path.isdir(directory):
            QMessageBox.critical(self, "错误", "目录路径无效。")
            return

        if self.rename_checkbox.isChecked() or self.convert_format_checkbox.isChecked() or self.compress_checkbox.isChecked():
            renamed_count = batch_rename(directory, prefix, start_number, extension, convert_format, compress_quality)
            self.result_label.setText(f"已成功处理 {renamed_count} 个文件！")
        else:
            self.result_label.setText("请启用至少一种处理功能。")


if __name__ == '__main__':
    app = QApplication([])
    window = BatchRenameApp()
    window.show()
    app.exec()