import asyncio
from PySide6.QtCore import QObject, QThread


class IOWorker(QObject):
    """
    具体IO线程Worker，每个Worker管理一个独立事件循环
    """

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        # QObject 默认属于创建它的线程，会阻塞主线程
        # moveToThread() 会把这个对象（和它的信号槽逻辑）交给新的线程
        self.moveToThread(self.thread)

        self.thread.started.connect(self._start_loop)
        self.thread.start()

        self.loop = None

    def _start_loop(self):
        """self.thread.start()自动调用本方法"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.loop.run_forever()

    def submit(self, coro):
        """提交协程到本worker的事件循环执行"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        """关闭事件循环和线程"""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.quit()
        self.thread.wait()
