# snapforge/ui/convert_dialog.py
from PyQt5 import QtWidgets

from .base_dialog import BaseDialog


class ConvertDialog(BaseDialog):
    """转换对话框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("转换设置")
        self.init_ui()

    def init_ui(self):
        """初始化用户界面。"""
        # 获取 BaseDialog 的主布局
        layout = self.layout()

        # 格式选择下拉框
        self.format_label = QtWidgets.QLabel("目标格式：")
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["png", "jpg", "bmp"])

        # 将控件添加到布局中
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_combo)


# 使用示例
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = ConvertDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        print(f"Selected Format: {dialog.format_combo.currentText()}")
    else:
        print("Dialog Rejected")
    sys.exit(app.exec_())
