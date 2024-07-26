# utils/error_handler.py
from PyQt6.QtWidgets import QMessageBox

def handle_error(error_message):
    """显示错误信息弹窗。

    Args:
        error_message (str): 错误信息。
    """
    QMessageBox.warning(None, "错误", error_message)