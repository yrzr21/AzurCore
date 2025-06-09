from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from core.utils.logger import logger


class BaseTask(QObject, QRunnable):
    """
    任务实体基类，在一个新线程中
    子类需要使用 progress 汇报进度、实现 execute 接口
    子类中出现的异常，要么自行处理+logger，要么 raise 异常
    """

    started = Signal()
    progress = Signal(int)  # 子类自行计算进度
    finished = Signal(object, bool, object)  # (task, success, result)
    error = Signal(object, str)  # task, message

    def __init__(self, name):
        # 多继承需要手动调用，因为Qt是C++实现的
        QObject.__init__(self)
        QRunnable.__init__(self)

        # Python 持有引用 ≠ Qt C++ 层不销毁
        # QThreadPool 执行完 QRunnable task 就会直接销毁
        # 所以要关闭这个自动销毁
        self.setAutoDelete(False)

        self.name = name  # for debug

        self.is_running = False
        self._is_canceled = False

    def run(self):
        """任务执行入口"""
        try:
            logger.info(f"{self.name} 开始执行")
            self.is_running = True
            self.started.emit()
            result = self.execute()
            self.is_running = False

            success = not self._is_canceled
            logger.info(f"{self.name} 执行完毕")
            self.finished.emit(self, success, result)

        except Exception as e:
            logger.error(f"{self.name} 执行失败，出现异常：{str(e)}")
            self.error.emit(self, f"任务失败: {str(e)}")

    def execute(self):
        """
        实际任务逻辑（需要子类实现）
        使用 _is_canceled 终止运行
        需返回 result+msg
        """
        raise NotImplementedError("子类必须实现execute方法")

    def request_cancel(self):
        """终止执行，仅设置状态"""
        logger.debug(f"{self.name} requested cancel")
        self._is_canceled = True

    def __str__(self):
        return self.name
