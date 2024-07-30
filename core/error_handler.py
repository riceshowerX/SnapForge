# SnapForge/core/error_handler.py
import logging

# 配置日志记录器
logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def handle_error(error_message):
    """
    处理错误，记录错误信息到日志文件。

    Args:
        error_message: 错误信息字符串。
    """
    logging.error(error_message)
    # 可选：在控制台或弹窗中显示错误信息
    print(f"错误：{error_message}")
    # 也可以使用 QMessageBox 或其他方式显示错误信息给用户