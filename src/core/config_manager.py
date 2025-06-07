import json
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file):
        self.config_file = Path(config_file)

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"打开配置文件 {self.config_file} 失败: {e}")

    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def __getitem__(self, key):
        """支持下标访问（字典风格）"""
        return self.config[key]


config = ConfigManager("E:\develop\Projects\MyApp\config.json")
