# main.py
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui import BatchRenameApp

def main():
    # 初始化日志记录，添加日志文件大小限制
    from logging.handlers import RotatingFileHandler
    logging.basicConfig(
        handlers=[RotatingFileHandler('app.log', maxBytes=1 * 1024 * 1024, backupCount=5)],  # 1MB, 最多5个备份
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
    )

    app = QApplication(sys.argv)

    try:
        window = BatchRenameApp()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        logging.exception("发生未捕获的异常")
        # 弹出错误对话框
        QMessageBox.critical(None, "错误", f"发生未捕获的异常：\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
