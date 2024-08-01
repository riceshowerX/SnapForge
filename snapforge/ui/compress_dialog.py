# snapforge/ui/compress_dialog.py
from PyQt5 import QtWidgets

from .base_dialog import BaseDialog


class CompressDialog(BaseDialog):
    """压缩对话框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("压缩设置")
        self.init_ui()

    def init_ui(self):
        """初始化用户界面。"""
        # 获取 BaseDialog 的主布局
        layout = self.layout()

        # 质量选择旋钮
        self.quality_label = QtWidgets.QLabel("压缩质量 (0-100)：")
        self.quality_spin = QtWidgets.QSpinBox()
        self.quality_spin.setRange(0, 100)
        self.quality_spin.setValue(80)

        # 将控件添加到布局中
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_spin)


# 使用示例
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = CompressDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        print(f"Selected Quality: {dialog.quality_spin.value()}")
    else:
        print("Dialog Rejected")
    sys.exit(app.exec_())
