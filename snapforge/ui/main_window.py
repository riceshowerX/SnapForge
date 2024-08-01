# snapforge/ui/main_window.py
import os

from PyQt5 import QtWidgets
from tqdm import tqdm

from .compress_dialog import CompressDialog
from .convert_dialog import ConvertDialog
from .rename_dialog import RenameDialog
from ..core import rename_processor, convert_processor, compress_processor
from ..utils import file_utils


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SnapForge")
        self.resize(800, 600)
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """初始化用户界面。"""
        # 创建主布局
        layout = QtWidgets.QVBoxLayout()

        # 文件选择区域
        self.init_file_selection(layout)

        # 操作按钮区域
        self.init_operation_buttons(layout)

        # 进度条
        self.progress_bar = QtWidgets.QProgressBar()
        layout.addWidget(self.progress_bar)

        # 设置主布局
        self.setLayout(layout)

    def init_file_selection(self, layout):
        """初始化文件选择区域。"""
        file_select_layout = QtWidgets.QHBoxLayout()
        self.file_path_label = QtWidgets.QLabel("文件路径：")
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_button = QtWidgets.QPushButton("选择文件")
        file_select_layout.addWidget(self.file_path_label)
        file_select_layout.addWidget(self.file_path_edit)
        file_select_layout.addWidget(self.file_path_button)
        layout.addLayout(file_select_layout)

    def init_operation_buttons(self, layout):
        """初始化操作按钮区域。"""
        button_layout = QtWidgets.QHBoxLayout()
        self.rename_button = QtWidgets.QPushButton("重命名")
        self.convert_button = QtWidgets.QPushButton("转换格式")
        self.compress_button = QtWidgets.QPushButton("压缩")
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.compress_button)
        layout.addLayout(button_layout)

    def connect_signals(self):
        """连接信号与槽。"""
        self.file_path_button.clicked.connect(self.select_file)
        self.rename_button.clicked.connect(self.rename_images)
        self.convert_button.clicked.connect(self.convert_images)
        self.compress_button.clicked.connect(self.compress_images)

    def select_file(self):
        """选择文件。"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*);;图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)

    def rename_images(self):
        """重命名图像。"""
        file_path = self.file_path_edit.text()
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择文件！")
            return

        dialog = RenameDialog()
        if dialog.exec_():
            new_name_prefix = dialog.prefix_edit.text()
            new_name_suffix = dialog.suffix_edit.text()
            self.process_images(
                file_path,
                rename_processor.RenameProcessor(new_name_prefix, new_name_suffix).process,
            )

    def convert_images(self):
        """转换图像格式。"""
        file_path = self.file_path_edit.text()
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择文件！")
            return

        dialog = ConvertDialog()
        if dialog.exec_():
            target_format = dialog.format_combo.currentText()
            self.process_images(
                file_path,
                convert_processor.ConvertProcessor(target_format).process,
            )

    def compress_images(self):
        """压缩图像。"""
        file_path = self.file_path_edit.text()
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择文件！")
            return

        dialog = CompressDialog()
        if dialog.exec_():
            quality = dialog.quality_spin.value()
            self.process_images(
                file_path,
                compress_processor.CompressProcessor(quality).process,
            )

    def process_images(self, file_path, process_func):
        """处理图像文件或文件夹。

        Args:
            file_path (str): 文件或文件夹路径。
            process_func (function): 处理函数。
        """
        if os.path.isfile(file_path):
            self.process_image(file_path, process_func)
        elif os.path.isdir(file_path):
            self.process_folder(file_path, process_func)
        else:
            QtWidgets.QMessageBox.warning(self, "错误", "无效的文件路径！")

    def process_image(self, image_path, process_func):
        """处理单个图像文件。

        Args:
            image_path (str): 图像文件路径。
            process_func (function): 处理函数。
        """
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        success = process_func(image_path)
        if success:
            QtWidgets.QMessageBox.information(self, "完成", "处理成功！")
        else:
            QtWidgets.QMessageBox.warning(self, "错误", "处理失败！")

    def process_folder(self, folder_path, process_func):
        """处理文件夹中的所有图像文件。

        Args:
            folder_path (str): 文件夹路径。
            process_func (function): 处理函数。
        """
        image_paths = file_utils.get_image_paths(folder_path)
        if image_paths:
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(image_paths))
            for i, image_path in enumerate(tqdm(image_paths, desc="处理中...")):
                success = process_func(image_path)
                if success:
                    self.progress_bar.setValue(i + 1)
            QtWidgets.QMessageBox.information(self, "完成", "处理成功！")
        else:
            QtWidgets.QMessageBox.warning(self, "错误", "文件夹中没有找到图像文件！")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
