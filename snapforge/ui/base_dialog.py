# snapforge/ui/base_dialog.py
from PyQt5 import QtWidgets

class BaseDialog(QtWidgets.QDialog):
    """基础对话框类。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("操作设置")

        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 设置按钮
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 设置布局
        self.setLayout(layout)