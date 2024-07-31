# snapforge/ui/compress_dialog.py
from .base_dialog import BaseDialog
from PyQt5 import QtWidgets

class CompressDialog(BaseDialog):
    """压缩对话框。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("压缩设置")

        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 质量选择旋钮
        self.quality_label = QtWidgets.QLabel("压缩质量 (0-100)：")
        self.quality_spin = QtWidgets.QSpinBox()
        self.quality_spin.setRange(0, 100)
        self.quality_spin.setValue(80)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_spin)

        # 设置布局
        self.setLayout(layout)