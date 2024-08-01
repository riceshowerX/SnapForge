# snapforge/ui/base_dialog.py
from PyQt5 import QtWidgets


class BaseDialog(QtWidgets.QDialog):
    """基础对话框类，用于通用的操作设置对话框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化用户界面。"""
        self.setWindowTitle("操作设置")

        # 创建主布局
        layout = QtWidgets.QVBoxLayout()

        # 创建和配置按钮盒子
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 将按钮盒子添加到布局中
        layout.addWidget(button_box)

        # 设置主布局
        self.setLayout(layout)


# 使用示例
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = BaseDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    sys.exit(app.exec_())
