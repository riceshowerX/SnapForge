# snapforge/ui/rename_dialog.pyfrom .base_dialog import BaseDialog
from .base_dialog import BaseDialog
from PyQt5 import QtWidgets

class RenameDialog(BaseDialog):
    """重命名对话框。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("重命名设置")
        self.init_ui()

    def init_ui(self):
        """初始化用户界面。"""
        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 初始化前缀和后缀输入框
        self.init_prefix_suffix(layout)

        # 添加确认和取消按钮
        self.init_buttons(layout)

        # 设置布局
        self.setLayout(layout)

    def init_prefix_suffix(self, layout):
        """初始化前缀和后缀输入框。"""
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

    def init_buttons(self, layout):
        """初始化确认和取消按钮。"""
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
