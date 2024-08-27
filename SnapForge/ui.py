# ui.py
import os
import sys

from PIL import Image
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QMessageBox, QCheckBox, QProgressBar, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal

from logic import batch_process  # 从 logic.py 导入处理函数


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, directory, prefix, start_number, extension, convert_format, compress_quality):
        super().__init__()
        self.directory = directory
        self.prefix = prefix
        self.start_number = start_number
        self.extension = extension
        self.convert_format = convert_format
        self.compress_quality = compress_quality

    def run(self):
        try:
            processed_count = batch_process(self.directory, self.prefix, self.start_number, self.extension,
                                           self.convert_format, self.compress_quality, self.progress_updated)
            self.finished.emit(processed_count)
        except Exception as e:
            self.error_occurred.emit(str(e))


class BatchRenameApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片批量处理工具")
        self.setGeometry(300, 300, 500, 450)  # 调整窗口大小以容纳进度条
        self.setWindowIcon(QIcon("resources/icon.png"))  # 请确保图标文件存在

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout(self.central_widget)  # 使用 QGridLayout 进行布局

        # 目录选择
        self.directory_label = QLabel("选择目录:")
        layout.addWidget(self.directory_label, 0, 0)

        self.directory_input = QLineEdit()
        layout.addWidget(self.directory_input, 0, 1, 1, 3)  # 横跨3列

        self.directory_button = QPushButton("浏览")
        self.directory_button.clicked.connect(self.browse_directory)
        layout.addWidget(self.directory_button, 0, 4)

        # 启用重命名
        self.rename_checkbox = QCheckBox("启用重命名")
        layout.addWidget(self.rename_checkbox, 1, 0, 1, 2)  # 横跨2列

        # 文件名前缀
        self.prefix_label = QLabel("文件名前缀:")
        layout.addWidget(self.prefix_label, 2, 0)

        self.prefix_input = QLineEdit()
        layout.addWidget(self.prefix_input, 2, 1, 1, 4)  # 横跨4列

        # 起始编号
        self.start_number_label = QLabel("起始编号:")
        layout.addWidget(self.start_number_label, 3, 0)

        self.start_number_input = QLineEdit()
        self.start_number_input.setText("1")
        layout.addWidget(self.start_number_input, 3, 1, 1, 4)

        # 文件扩展名
        self.extension_label = QLabel("文件扩展名:")
        layout.addWidget(self.extension_label, 4, 0)

        self.extension_input = QLineEdit()
        self.extension_input.setText(".jpg")
        layout.addWidget(self.extension_input, 4, 1, 1, 4)

        # 启用格式转换
        self.convert_format_checkbox = QCheckBox("启用格式转换")
        self.convert_format_checkbox.stateChanged.connect(self.toggle_format_input)
        layout.addWidget(self.convert_format_checkbox, 5, 0, 1, 2)

        self.convert_format_label = QLabel("目标格式:")
        self.convert_format_label.setEnabled(False)
        layout.addWidget(self.convert_format_label, 6, 0)

        self.convert_format_input = QLineEdit()
        self.convert_format_input.setEnabled(False)
        layout.addWidget(self.convert_format_input, 6, 1, 1, 4)

        # 启用质量压缩
        self.compress_checkbox = QCheckBox("启用质量压缩")
        self.compress_checkbox.stateChanged.connect(self.toggle_compress_input)
        layout.addWidget(self.compress_checkbox, 7, 0, 1, 2)

        self.compress_quality_label = QLabel("压缩质量 (0-100):")
        self.compress_quality_label.setEnabled(False)
        layout.addWidget(self.compress_quality_label, 8, 0)

        self.compress_quality_input = QLineEdit()
        self.compress_quality_input.setEnabled(False)
        self.compress_quality_input.setText("85")
        layout.addWidget(self.compress_quality_input, 8, 1, 1, 4)

        # 开始处理按钮
        self.process_button = QPushButton("开始处理")
        self.process_button.clicked.connect(self.start_processing)
        layout.addWidget(self.process_button, 9, 0, 1, 5)  # 横跨5列

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar, 10, 0, 1, 5)

        # 结果标签
        self.result_label = QLabel("")
        layout.addWidget(self.result_label, 11, 0, 1, 5)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.directory_input.setText(directory)

    def toggle_format_input(self):
        enabled = self.convert_format_checkbox.isChecked()
        self.convert_format_label.setEnabled(enabled)
        self.convert_format_input.setEnabled(enabled)

    def toggle_compress_input(self):
        enabled = self.compress_checkbox.isChecked()
        self.compress_quality_label.setEnabled(enabled)
        self.compress_quality_input.setEnabled(enabled)

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

        self.process_button.setEnabled(False)  # 禁用按钮
        self.result_label.setText("处理中...")

        self.worker_thread = WorkerThread(directory, prefix, start_number, extension, convert_format,
                                          compress_quality)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.finished.connect(self.processing_finished)
        self.worker_thread.error_occurred.connect(self.processing_error)
        self.worker_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def processing_finished(self, processed_count):
        self.result_label.setText(f"已成功处理 {processed_count} 个文件！")
        self.process_button.setEnabled(True)  # 启用按钮

    def processing_error(self, error_message):
        QMessageBox.critical(self, "错误", f"处理过程中发生错误:\n{error_message}")
        self.result_label.setText("处理失败！")
        self.process_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchRenameApp()
    window.show()
    sys.exit(app.exec())