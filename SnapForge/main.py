# main.py
import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui import BatchRenameApp

def main():
    # 初始化日志记录
    logging.basicConfig(filename='app.log', level=logging.DEBUG,  # 设置为 DEBUG 以便调试
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

    app = QApplication(sys.argv)

    try:
        window = BatchRenameApp()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        # 捕获完整的堆栈信息
        error_msg = f"发生未捕获的异常：\n{str(e)}"
        error_detail = traceback.format_exc()  # 获取堆栈信息
        logging.error(error_detail)  # 记录完整堆栈信息到日志文件
        
        # 弹出用户友好的错误对话框
        user_msg = "应用程序遇到严重错误并将关闭。请检查日志文件了解详情。"
        QMessageBox.critical(None, "错误", user_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
