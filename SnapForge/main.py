import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui import BatchRenameApp  # 确保这里引用正确


def main():
    app = QApplication(sys.argv)

    try:
        window = BatchRenameApp()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        error_msg = f"发生未捕获的异常：\n{str(e)}\n\n详细信息：\n{traceback.format_exc()}"
        print(error_msg)
        # 弹出错误对话框
        QMessageBox.critical(None, "错误", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
