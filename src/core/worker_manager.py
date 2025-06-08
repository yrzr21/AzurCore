from PySide6.QtCore import QObject, QThreadPool
from core.base.base_task import BaseTask


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
        print("WorkerManager:execute")
        self.thread_pool.start(task)

    def wait_for_all_done(self, timeout=-1):
        """等待所有任务完成"""
        return self.thread_pool.waitForDone(timeout)

    def active_thread_count(self):
        """获取当前活动线程数"""
        return self.thread_pool.activeThreadCount()


worker_manager = WorkerManager()
