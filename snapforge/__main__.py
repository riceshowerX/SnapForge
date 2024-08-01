# snapforge/__main__.py
from PyQt5.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .utils.config_manager import config_manager
from .plugins import plugin_manager  # 导入 plugin_manager
import sys


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    try:
        # 加载配置
        config_manager.load_config()
    except Exception as e:
        print(f"Error loading config: {e}")

    try:
        # 加载插件
        plugin_manager.load_plugins("plugins/custom_plugins")
    except Exception as e:
        print(f"Error loading plugins: {e}")

    window.show()

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
