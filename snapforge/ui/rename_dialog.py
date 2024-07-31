# snapforge/ui/rename_dialog.py
from .base_dialog import BaseDialog
from PyQt5 import QtWidgets

class RenameDialog(BaseDialog):
    """重命名对话框。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("重命名设置")

        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 前缀输入框
        self.prefix_label = QtWidgets.QLabel("前缀：")
        self.prefix_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.prefix_label)
        layout.addWidget(self.prefix_edit)

        # 后缀输入框
        self.suffix_label = QtWidgets.QLabel("后缀：")
        self.suffix_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.suffix_label)
        layout.addWidget(self.suffix_edit)

        # 设置布局
        self.setLayout(layout)