import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtGui import QIcon  # 导入 QIcon
from logic import batch_rename

class BatchRenameApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片批量重命名工具")
        self.setGeometry(300, 300, 400, 300)
        self.setWindowIcon(QIcon("resources/icon.ico"))  # 设置窗口图标

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.directory_label = QLabel("选择目录:")
        layout.addWidget(self.directory_label)

        self.directory_input = QLineEdit()
        layout.addWidget(self.directory_input)

        self.directory_button = QPushButton("浏览")
        self.directory_button.clicked.connect(self.browse_directory)
        layout.addWidget(self.directory_button)

        self.prefix_label = QLabel("文件名前缀:")
        layout.addWidget(self.prefix_label)

        self.prefix_input = QLineEdit()
        layout.addWidget(self.prefix_input)

        self.start_number_label = QLabel("起始编号:")
        layout.addWidget(self.start_number_label)

        self.start_number_input = QLineEdit()
        self.start_number_input.setText("1")
        layout.addWidget(self.start_number_input)

        self.extension_label = QLabel("文件扩展名:")
        layout.addWidget(self.extension_label)

        self.extension_input = QLineEdit()
        self.extension_input.setText(".jpg")
        layout.addWidget(self.extension_input)

        self.convert_format_checkbox = QCheckBox("转换文件格式")
        self.convert_format_checkbox.stateChanged.connect(self.toggle_format_input)
        layout.addWidget(self.convert_format_checkbox)

        self.convert_format_label = QLabel("目标格式:")
        self.convert_format_label.setEnabled(False)
        layout.addWidget(self.convert_format_label)

        self.convert_format_input = QLineEdit()
        self.convert_format_input.setEnabled(False)
        layout.addWidget(self.convert_format_input)

        self.rename_button = QPushButton("开始重命名")
        self.rename_button.clicked.connect(self.start_renaming)
        layout.addWidget(self.rename_button)

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

    def start_renaming(self):
        directory = self.directory_input.text()
        prefix = self.prefix_input.text()
        start_number = int(self.start_number_input.text())
        extension = self.extension_input.text()
        convert_format = self.convert_format_input.text() if self.convert_format_checkbox.isChecked() else None

        if not os.path.isdir(directory):
            QMessageBox.critical(self, "错误", "目录路径无效。")
            return

        if not prefix:
            QMessageBox.critical(self, "错误", "文件名前缀不能为空。")
            return

        try:
            renamed_count = batch_rename(directory, prefix, start_number, extension, convert_format)
            self.result_label.setText(f"已成功重命名并转换 {renamed_count} 个文件！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理过程中发生错误：{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchRenameApp()
    window.show()
    sys.exit(app.exec())
