import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
from logic import ImageProcessor

def main():
    app = QApplication(sys.argv)
    processor = ImageProcessor()  # 创建业务逻辑对象
    window = MainWindow(processor)  # 传入业务逻辑对象
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
