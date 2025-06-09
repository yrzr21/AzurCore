# src/core/utils/logger.py
import inspect
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
        self.use_module_tag = None

        self.init()

    def init(self):
        """初始化 logger """
        self.log_path = self._setup_logfile()
        self._restore_config()
        self._setup_log_handler()

    # 日志输出接口
    def info(self, msg):
        self.logger.info(self._tag_msg(msg))

    def warning(self, msg):
        self.logger.warning(self._tag_msg(msg))

    def error(self, msg):
        self.logger.error(self._tag_msg(msg))

    def debug(self, msg):
        self.logger.debug(self._tag_msg(msg))

    def save_config(self):
        with config.config_lock:
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
        log_file = config["log"]["log_file"]
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
        self.use_module_tag = config["log"]["use_module_tag"]

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

    def _tag_msg(self, msg):
        """自动从调用栈中提取 类名.方法名 或 函数名"""
        if not self.use_module_tag:
            return msg

        frame = inspect.currentframe()
        outer = frame.f_back.f_back  # 跳过 _tag_msg 和 info 层
        method_name = outer.f_code.co_name

        # 尝试获取类名（如果是类方法）
        instance = outer.f_locals.get('self', None)
        if instance:
            class_name = instance.__class__.__name__
            tag = f"{class_name}.{method_name}"
        else:
            # 否则为模块级函数
            tag = method_name

        return f"[{tag}] {msg}"


# 可能被多线程访问
logger = Logger()
