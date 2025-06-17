import threading
from asyncio import Event
from core.base.base_task import AsyncTask


class CrawlerBrowserTask(AsyncTask):
    def __init__(self, playwright, browser_config, user_data_dir):
        super().__init__("CrawlerBrowserTask")
        # type headless args
        self.browser_config = browser_config
        self.user_data_dir = user_data_dir
        self.container = getattr(playwright, self.browser_config["type"])
        self.context = None
        self.page = None
        self.is_stop = False

        self.lock = threading.Lock()
        self.pending_tasks = []
        self.has_task = Event()  # 用于唤醒协程，创建时自动加入事件循环

    async def execute(self):
        """启动浏览器，并打开一个页面"""
        self.context = await self.container.launch_persistent_context(
            self.user_data_dir,
            headless=self.browser_config["headless"],
            args=self.browser_config["args"]
        )
        self.page = await self.context.new_page()

        # 启动任务处理循环
        await self._process_tasks()

    async def _process_tasks(self):
        while not self.is_stop:
            # 等待者自动被 has_task 捕获
            await self.has_task.wait()

            # async wit lock 是协程级锁，对其他线程无效
            with self.lock:
                self.has_task.clear()
                if not self.pending_tasks:
                    continue
                task_func, *arguments = self.pending_tasks.pop(0)

            # 处理任务
            await task_func(*arguments)

    def new_tasks(self, tasks):
        """
        由主线程直接调用，无其余用途
        任务例如：[[func1,argument1,argument2], [func2,argument1,argument2]]
        """
        with self.lock:
            self.pending_tasks.extend(tasks)

        # 唤醒等待者 —— 必须在事件循环中调用 set
        self.loop.call_soon_threadsafe(self.has_task.set)

    def request_stop(self):
        """
        由主线程直接调用，无其余用途
        无需加锁、无需使用 threadsafe api
        """
        self.is_stop = True
