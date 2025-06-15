import random

from PySide6.QtCore import QObject

from core.worker.io_worker import IOWorker


class IOWorkerManager(QObject):
    """
    IO异步任务管理器，内部多个 worker 分别跑独立事件循环
    """

    def __init__(self, num_workers=1):
        super().__init__()
        self.workers = [IOWorker() for _ in range(num_workers)]

    def submit(self, task):
        """随机挑选一个worker提交任务"""
        worker = random.choice(self.workers)
        worker.submit(task.run)

    def shutdown(self):
        for worker in self.workers:
            worker.stop()
