import sys
from PyQt6.QtWidgets import QApplication
from ui import BatchRenameApp  # 确保这里引用正确
from logic import ImageProcessor  # 如果需要

def main():
    app = QApplication(sys.argv)
    window = BatchRenameApp()  # 实例化 BatchRenameApp
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()