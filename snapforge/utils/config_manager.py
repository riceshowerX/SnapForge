# snapforge/utils/config_manager.py
import yaml

class ConfigManager:
    """配置管理器。"""

    def __init__(self, config_path="config.yaml"):
        """初始化配置管理器。

        Args:
            config_path (str, optional): 配置文件路径。Defaults to "config.yaml".
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """加载配置。

        Returns:
            dict: 配置字典。
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f: # 使用 UTF-8 编码
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"配置文件 '{self.config_path}' 不存在。")
            return {}
        except Exception as e:
            print(f"加载配置文件失败：{e}")
            return {}

    def save_config(self):
        """保存配置。"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f: # 使用 UTF-8 编码
                yaml.dump(self.config, f)
        except Exception as e:
            print(f"保存配置文件失败：{e}")

    def get_value(self, key, default=None):
        """获取配置值。

        Args:
            key (str): 配置键。
            default (any, optional): 默认值。Defaults to None.

        Returns:
            any: 配置值。
        """
        return self.config.get(key, default)

    def set_value(self, key, value):
        """设置配置值。

        Args:
            key (str): 配置键。
            value (any): 配置值。
        """
        self.config[key] = value
        self.save_config()

config_manager = ConfigManager()