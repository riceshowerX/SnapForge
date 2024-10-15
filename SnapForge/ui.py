# UI.py
import os
import sys
import cv2  # 使用 OpenCV 进行图像处理
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QMessageBox, QCheckBox, QProgressBar, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor
import logging

class ImageProcessor:
    def batch_process(self, directory, prefix, start_number, extension, convert_format, compress_quality, progress_callback):
        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        total_files = len(files)
        processed_count = 0

        with ThreadPoolExecutor() as executor:
            futures = []
            for i, file in enumerate(files):
                file_path = os.path.join(directory, file)
                new_name = f"{prefix}{start_number + i}{extension}"
                futures.append(executor.submit(self.process_image, file_path, new_name, directory, convert_format, compress_quality))

            for future in futures:
                result = future.result()
                if result:
                    processed_count += 1
                    progress_callback(int((processed_count / total_files) * 100))

        return processed_count

    def process_image(self, file_path, new_name, directory, convert_format, compress_quality):
        try:
            # 使用 OpenCV 读取图像
            image = cv2.imread(file_path)
            if convert_format:
                # 转换格式
                new_name = new_name.replace(os.path.splitext(new_name)[1], f".{convert_format.lower()}")
            if compress_quality is not None:
                # 保存图像时应用压缩质量
                cv2.imwrite(os.path.join(directory, new_name), image, [int(cv2.IMWRITE_JPEG_QUALITY), compress_quality])
            else:
                cv2.imwrite(os.path.join(directory, new_name), image)
            return True
        except Exception as e:
            logging.error(f"处理文件 {file_path} 时出现错误: {e}")
            return False


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
        self.processor = ImageProcessor()

    def run(self):
        try:
            processed_count = self.processor.batch_process(
                self.directory,
                self.prefix,
                self.start_number,
                self.extension,
                self.convert_format,
                self.compress_quality,
                self.update_progress
            )
            self.finished.emit(processed_count)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit(0)

    def update_progress(self, progress):
        self.progress_updated.emit(progress)

class BatchRenameApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片批量处理工具")
        self.setGeometry(300, 300, 500, 450)
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout(self.central_widget)

        # 目录选择
        self.directory_label = QLabel("选择目录:")
        layout.addWidget(self.directory_label, 0, 0)

        self.directory_input = QLineEdit()
        layout.addWidget(self.directory_input, 0, 1, 1, 3)

        self.directory_button = QPushButton("浏览")
        self.directory_button.clicked.connect(self.browse_directory)
        layout.addWidget(self.directory_button, 0, 4)

        # 启用重命名
        self.rename_checkbox = QCheckBox("启用重命名")
        layout.addWidget(self.rename_checkbox, 1, 0, 1, 2)

        # 文件名前缀
        self.prefix_label = QLabel("文件名前缀:")
        layout.addWidget(self.prefix_label, 2, 0)

        self.prefix_input = QLineEdit()
        layout.addWidget(self.prefix_input, 2, 1, 1, 4)

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
        layout.addWidget(self.process_button, 9, 0, 1, 5)

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
        if not os.path.isdir(directory):
            QMessageBox.critical(self, "错误", "目录路径无效。")
            return

        prefix = self.prefix_input.text() if self.rename_checkbox.isChecked() else None

        try:
            start_number = int(self.start_number_input.text())
            if start_number <= 0:
                raise ValueError("起始编号必须是正整数")
        except ValueError as e:
            QMessageBox.critical(self, "错误", str(e))
            return

        extension = self.extension_input.text().strip()
        if not extension.startswith("."):
            QMessageBox.critical(self, "错误", "请确保扩展名以 '.' 开头。")
            return

        convert_format = self.convert_format_input.text().strip().lower() if self.convert_format_checkbox.isChecked() else None
        compress_quality = None

        if self.compress_checkbox.isChecked():
            try:
                compress_quality = int(self.compress_quality_input.text())
                if not (0 <= compress_quality <= 100):
                    raise ValueError("压缩质量必须在 0 到 100 之间。")
            except ValueError as e:
                QMessageBox.critical(self, "错误", str(e))
                return

        self.progress_bar.setValue(0)
        self.result_label.setText("")

        self.thread = WorkerThread(directory, prefix, start_number, extension, convert_format, compress_quality)
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.finished.connect(self.processing_finished)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def processing_finished(self, processed_count):
        if processed_count > 0:
            self.result_label.setText(f"处理完成，成功处理 {processed_count} 个文件。")
        else:
            self.result_label.setText("没有处理任何文件。")

    def show_error(self, error_message):
        QMessageBox.critical(self, "错误", error_message)
