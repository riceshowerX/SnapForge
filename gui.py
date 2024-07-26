# gui.py 
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget, QMessageBox, QProgressBar
from PyQt6.QtCore import Qt
from utils import image_processor
import sys

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片处理工具")
        self.resize(400, 350)

        self.source_directory = None
        self.target_directory = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 选择文件夹
        self.source_label = QLabel("选择原始图片文件夹:")
        self.source_button = QPushButton("选择文件夹")
        self.source_button.clicked.connect(self.select_source_directory)

        self.target_label = QLabel("选择保存图片文件夹:")
        self.target_button = QPushButton("选择文件夹")
        self.target_button.clicked.connect(self.select_target_directory)

        layout.addWidget(self.source_label)
        layout.addWidget(self.source_button)
        layout.addWidget(self.target_label)
        layout.addWidget(self.target_button)

        # 批量重命名
        self.prefix_label = QLabel("前缀:")
        self.prefix_entry = QLineEdit()
        self.start_number_label = QLabel("起始编号:")
        self.start_number_entry = QLineEdit("1")
        self.rename_button = QPushButton("执行重命名")
        self.rename_button.clicked.connect(self.rename_files)

        layout.addWidget(self.prefix_label)
        layout.addWidget(self.prefix_entry)
        layout.addWidget(self.start_number_label)
        layout.addWidget(self.start_number_entry)
        layout.addWidget(self.rename_button)

        # 批量转换
        self.format_label = QLabel("目标格式 (如 jpeg, png):")
        self.format_entry = QLineEdit()
        self.convert_button = QPushButton("执行转换")
        self.convert_button.clicked.connect(self.convert_files)

        layout.addWidget(self.format_label)
        layout.addWidget(self.format_entry)
        layout.addWidget(self.convert_button)

        # 批量压缩
        self.quality_label = QLabel("压缩质量 (1-100):")
        self.quality_entry = QLineEdit("80")
        self.compress_button = QPushButton("执行压缩")
        self.compress_button.clicked.connect(self.compress_files)

        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_entry)
        layout.addWidget(self.compress_button)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_source_directory(self):
        self.source_directory = QFileDialog.getExistingDirectory(self, "选择原始图片文件夹")

    def select_target_directory(self):
        self.target_directory = QFileDialog.getExistingDirectory(self, "选择保存图片文件夹")

    def rename_files(self):
        if not self.source_directory or not self.target_directory:
            QMessageBox.warning(self, "警告", "请先选择原始和保存图片文件夹！")
            return

        prefix = self.prefix_entry.text()
        try:
            start_number = int(self.start_number_entry.text())
        except ValueError:
            QMessageBox.warning(self, "警告", "起始编号必须是一个整数！")
            return

        try:
            renamed_count = image_processor.batch_rename_files(
                self.source_directory,
                self.target_directory,
                prefix,
                start_number,
                self.update_progress_bar
            )
            QMessageBox.information(self, "结果", f"重命名完成！共重命名了 {renamed_count} 个文件。")
        except Exception as e:
            # 处理其他潜在的异常
            QMessageBox.warning(self, "错误", f"发生错误: {e}")


    def convert_files(self):
        if not self.source_directory or not self.target_directory:
            QMessageBox.warning(self, "警告", "请先选择原始和保存图片文件夹！")
            return

        target_format = self.format_entry.text().lower()
        if not target_format:
            QMessageBox.warning(self, "警告", "目标格式不能为空！")
            return

        try:
            converted_count = image_processor.batch_convert_images(
                self.source_directory,
                self.target_directory,
                target_format,
                self.update_progress_bar
            )
            QMessageBox.information(self, "结果", f"格式转换完成！共转换了 {converted_count} 个文件。")
        except Exception as e:
            # 处理其他潜在的异常
            QMessageBox.warning(self, "错误", f"发生错误: {e}")

    def compress_files(self):
        if not self.source_directory or not self.target_directory:
            QMessageBox.warning(self, "警告", "请先选择原始和保存图片文件夹！")
            return

        try:
            quality = int(self.quality_entry.text())
            if quality < 1 or quality > 100:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "警告", "压缩质量必须是1到100之间的整数！")
            return

        try:
            compressed_count = image_processor.batch_compress_images(
                self.source_directory,
                self.target_directory,
                quality,
                self.update_progress_bar
            )
            QMessageBox.information(self, "结果", f"压缩完成！共压缩了 {compressed_count} 个文件。")
        except Exception as e:
            # 处理其他潜在的异常
            QMessageBox.warning(self, "错误", f"发生错误: {e}")

    def update_progress_bar(self, current, total):
        """更新进度条。

        Args:
            current (int): 当前进度。
            total (int): 总进度。
        """
        self.progress_bar.setValue(int(current / total * 100))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec())