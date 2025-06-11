from core.utils.timeout_timer import TimeoutTimer
from core.worker_manager import worker_manager
from PySide6.QtCore import Signal, QObject
from core.base.base_task import BaseTask
from core.utils.logger import logger


class BaseService(QObject):
    """
    计算密集型任务封装为 task，统一向 worker_manager 申请执行
    任务取消：request_cancel，task 尽快收尾工作，并触发信号
    任务完成/错误：在 handler 中断开连接与从 active_tasks 中移除
    """

    task_started = Signal()
    progress_updated = Signal(int)
    task_completed = Signal(bool, object)  # success, result
    error_occurred = Signal(str)

    def __init__(self, name):
        super().__init__()
        self.name = name  # for debug

        # Python 持有引用 ≠ Qt C++ 层不销毁
        # QThreadPool 执行完 QRunnable task 就会直接销毁
        # 所以在 BaseTask 中需要 setAutoDelete(False)
        self.active_tasks = []

    def deliver(self, task: BaseTask):
        """将 task 交付给 worker 执行"""
        self.active_tasks.append(task)

        task.started.connect(self.on_task_started)
        task.progress.connect(self.on_progress_updated)
        # task 运行完毕后 会自动通知 controller
        task.finished.connect(self.on_task_finished)
        task.error.connect(self.on_task_error)

        worker_manager.execute(task)

    def cancel_task(self, task: BaseTask):
        """终止任务并断连"""
        if task not in self.active_tasks or not task.is_running:
            logger.error(f"{self}: cancelling unactivated task {task}")
            return

        task.request_cancel()

    def cancel_all(self):
        """终止所有任务"""
        # 小列表副本的开销可以接受，且避免了迭代器失效
        for task in list(self.active_tasks):
            self.cancel_task(task)

    # signal
    def on_task_started(self):
        self.task_started.emit()

    def on_progress_updated(self, new_progress: int):
        self.progress_updated.emit(new_progress)

    def on_task_finished(self, task, success, result):
        """处理任务完成"""
        self._disconnect_and_remove_task(task)
        self.task_completed.emit(success, result)

    def on_task_error(self, task, message):
        """处理任务错误"""
        logger.info(f"{task} error: {message}")

        self._disconnect_and_remove_task(task)
        self.error_occurred.emit(message)

    # helpers
    def _disconnect_and_remove_task(self, task):
        task.finished.disconnect(self.on_task_finished)
        task.error.disconnect(self.on_task_error)
        self.active_tasks.remove(task)

    def __str__(self):
        return self.name


class BatchedService(BaseService):
    """
    批量任务服务，将多个任务打包成一个任务
    任务取消：request_cancel，task 尽快收尾工作，并触发信号
    任务完成/错误：在 handler 中断开连接与从 active_tasks 中移除
    """

    def __init__(self, name, interval, max_batch_size):
        super().__init__(name)

        self.timeout_timer = TimeoutTimer(interval, self._do_deliver)
        self.interval = interval
        self.max_batch_size = max_batch_size
        self.batch_size = 0

        self.task_queue = []

    def deliver(self, task: BaseTask):
        if self.batch_size >= self.max_batch_size:
            self._do_deliver()
        else:
            self.task_queue.append(task)

    def _do_deliver(self):
        if not self.task_queue:
            return
        self.timeout_timer.stop()

        for task in self.task_queue:
            super().deliver(task)
        self.batch_size = 0
        self.task_queue.clear()

        self.timeout_timer.start()
