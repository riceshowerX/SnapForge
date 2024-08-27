import sys
from PyQt6.QtWidgets import QApplication
from ui import BatchRenameApp

def main():
    app = QApplication(sys.argv)
    window = BatchRenameApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
