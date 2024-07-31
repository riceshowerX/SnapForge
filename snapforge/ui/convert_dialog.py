# snapforge/ui/convert_dialog.py
from .base_dialog import BaseDialog
from PyQt5 import QtWidgets

class ConvertDialog(BaseDialog):
    """转换对话框。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("转换设置")

        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 格式选择下拉框
        self.format_label = QtWidgets.QLabel("目标格式：")
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["png", "jpg", "bmp"])
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_combo)

        # 设置布局
        self.setLayout(layout)