# snapforge/__main__.py
from PyQt5.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .utils.config_manager import config_manager
from .plugins import plugin_manager # 导入 plugin_manager

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()

    # 加载配置
    config_manager.load_config()

    # 加载插件
    plugin_manager.load_plugins("plugins/custom_plugins")

    # 运行应用程序
    app.exec_()

if __name__ == "__main__":
    main()