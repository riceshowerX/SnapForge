# main.py
import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui import BatchRenameApp

def main():
    # 初始化日志记录
    logging.basicConfig(filename='app.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

    app = QApplication(sys.argv)

    try:
        window = BatchRenameApp()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        error_msg = f"发生未捕获的异常：\n{str(e)}"
        logging.exception(error_msg)  # 将错误信息记录到日志文件
        # 弹出错误对话框
        QMessageBox.critical(None, "错误", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
