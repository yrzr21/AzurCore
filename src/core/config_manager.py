import json
import threading
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file):
        self.config_file = Path(config_file)
        self._lock = threading.Lock()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"打开配置文件 {self.config_file} 失败: {e}")
            exit(-1)

    def save(self):
        """仅在仅在程序退出前调用"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def __getitem__(self, key):
        with self._lock:
            return self._config[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._config[key] = value


config = ConfigManager("E:\develop\Projects\AzurCore\config.json")
