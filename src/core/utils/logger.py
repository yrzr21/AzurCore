# src/core/utils/logger.py
import logging
import os
from datetime import datetime
from core.config_manager import config


class Logger:
    def __init__(self):
        self.level = None
        self.name = None
        self.logger = None
        self.formatter = None
        self.log_path = None

        self.init()

    def init(self):
        """初始化 logger """
        self.log_path = self._setup_logfile()
        self._restore_config()
        self._setup_log_handler()

    # 日志输出接口
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def save_config(self):
        config["log"] = {
            "log_dir": os.path.dirname(self.log_path),
            "log_file": self.log_path,
            "level": self.level,
            "formatter": {
                "fmt": self.formatter._fmt,
                "datefmt": self.formatter.datefmt,
            },
            "propagate": self.logger.propagate,
        }

    @staticmethod
    def _setup_logfile():
        log_file = config["log"].get("log_file")
        if log_file and os.path.exists(log_file):
            return log_file

        log_dir = config["log"]["log_dir"]
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = f"{now}.log"
        log_path = os.path.join(log_dir, log_file)
        return log_path

    def _restore_config(self):
        """使用配置文件恢复当前 log 配置"""
        self.name = config["app_name"]
        self.level = getattr(logging, config["log"]["level"].upper())

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)  # 低于 level 的日志不会被记录
        self.logger.propagate = False  # 防止日志重复输出

        fmt = config["log"]["formatter"]["fmt"]
        dateformat = config["log"]["formatter"]["dateformat"]
        self.formatter = logging.Formatter(fmt=fmt, datefmt=dateformat)

    def _setup_log_handler(self):
        # 防止不小心重复实例化 Logger
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # 输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

        # 输出到文件
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)


# 可能被多线程访问
logger = Logger()
