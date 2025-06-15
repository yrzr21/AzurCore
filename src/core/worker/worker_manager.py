"""
IO 任务会与计算任务相互阻塞，所以分离IO与计算线程

通信机制，即task如何与service通信：回调/QT信号，
    前者增加了复杂度，后者性能有问题。
    考虑到项目非高频爬虫，姑且使用QT信号机制
"""

from PySide6.QtCore import QObject, QThreadPool
from core.base.base_task import BaseTask
from core.utils.logger import logger


# todo: 调度问题
# todo：对于高频小数据量爬虫，可缓存数据，定期投放给 service

class WorkerManager(QObject):
    """
    执行计算密集型任务，一个线程即一个 worker，一个 worker 同时只能执行一个任务
    """

    # # 管理器级别的状态信号
    # task_started = Signal(BaseTask)
    # task_completed = Signal(BaseTask, bool, str)  # (任务, 是否成功, 消息)
    # task_error = Signal(BaseTask, str)

    def __init__(self, max_concurrent=4):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_concurrent)

    def execute(self, task: BaseTask):
        """执行任务"""
        logger.debug(f"new task:{task}")
        self.thread_pool.start(task)

    def wait_for_all_done(self, timeout=-1):
        """等待所有任务完成"""
        return self.thread_pool.waitForDone(timeout)

    def active_thread_count(self):
        """获取当前活动线程数"""
        return self.thread_pool.activeThreadCount()


worker_manager = WorkerManager()
