import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from batch_rename import batch_rename_files
from batch_convert import batch_convert_images
from batch_compress import batch_compress_images

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片处理工具")
        self.setGeometry(100, 100, 600, 400)

        self.source_directory = None
        self.target_directory = None

        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create UI components
        self.create_directory_selection(layout)
        self.create_rename_section(layout)
        self.create_convert_section(layout)
        self.create_compress_section(layout)

    def create_directory_selection(self, layout):
        # Source directory
        hbox1 = QHBoxLayout()
        self.source_button = QPushButton("选择原始图片文件夹")
        self.source_button.clicked.connect(self.select_source_directory)
        hbox1.addWidget(QLabel("选择原始图片文件夹:"))
        hbox1.addWidget(self.source_button)

        # Target directory
        hbox2 = QHBoxLayout()
        self.target_button = QPushButton("选择保存图片文件夹")
        self.target_button.clicked.connect(self.select_target_directory)
        hbox2.addWidget(QLabel("选择保存图片文件夹:"))
        hbox2.addWidget(self.target_button)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)

    def create_rename_section(self, layout):
        layout.addWidget(QLabel("批量重命名图片"))

        self.prefix_entry = QLineEdit()
        self.prefix_entry.setPlaceholderText("前缀")
        self.start_number_entry = QLineEdit()
        self.start_number_entry.setPlaceholderText("起始编号")

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("前缀:"))
        hbox.addWidget(self.prefix_entry)
        hbox.addWidget(QLabel("起始编号:"))
        hbox.addWidget(self.start_number_entry)

        layout.addLayout(hbox)

        rename_button = QPushButton("执行重命名")
        rename_button.clicked.connect(self.rename_files)
        layout.addWidget(rename_button)

    def create_convert_section(self, layout):
        layout.addWidget(QLabel("批量转换图片格式"))

        self.format_entry = QLineEdit()
        self.format_entry.setPlaceholderText("目标格式 (如 jpeg, png)")

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("目标格式:"))
        hbox.addWidget(self.format_entry)

        layout.addLayout(hbox)

        convert_button = QPushButton("执行转换")
        convert_button.clicked.connect(self.convert_files)
        layout.addWidget(convert_button)

    def create_compress_section(self, layout):
        layout.addWidget(QLabel("批量压缩图片"))

        self.quality_entry = QLineEdit()
        self.quality_entry.setPlaceholderText("压缩质量 (1-100)")

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("压缩质量:"))
        hbox.addWidget(self.quality_entry)

        layout.addLayout(hbox)

        compress_button = QPushButton("执行压缩")
        compress_button.clicked.connect(self.compress_files)
        layout.addWidget(compress_button)

    def select_source_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择原始图片文件夹")
        if directory:
            self.source_directory = directory

    def select_target_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择保存图片文件夹")
        if directory:
            self.target_directory = directory

    def rename_files(self):
        if not self.source_directory:
            QMessageBox.warning(self, "警告", "请先选择原始图片文件夹！")
            return

        prefix = self.prefix_entry.text()
        try:
            start_number = int(self.start_number_entry.text())
        except ValueError:
            QMessageBox.warning(self, "警告", "起始编号必须是一个整数！")
            return

        result = batch_rename_files(self.source_directory, prefix, start_number)
        QMessageBox.information(self, "结果", result)

    def convert_files(self):
        if not self.source_directory or not self.target_directory:
            QMessageBox.warning(self, "警告", "请先选择原始和保存图片文件夹！")
            return

        target_format = self.format_entry.text()
        if not target_format:
            QMessageBox.warning(self, "警告", "目标格式不能为空！")
            return

        result = batch_convert_images(self.source_directory, self.target_directory, target_format)
        QMessageBox.information(self, "结果", result)

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

        result = batch_compress_images(self.source_directory, self.target_directory, quality)
        QMessageBox.information(self, "结果", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec())
