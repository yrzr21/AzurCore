import asyncio
import random

from playwright.async_api import async_playwright

from core.base.base_service import BaseService
from core.utils.config_manager import config
from core.worker.io_worker_manager import io_worker_manager
from plugins.crawler.task.crawler_browser_task import CrawlerBrowserTask


class CrawlerService(BaseService):

    def __init__(self, name):
        super().__init__(name)
        self.browser_config = config["crawler"]["browser"]
        self.user_root_dir = config["crawler"]["users"]["user_root_dir"]
        self.idle_user_ids = config["crawler"]["users"]["ids"]
        self.active_user_ids = []

        self.playwright = None
        self.activated_browser_tasks = []

    def new_crawler(self, num_browsers=1):
        # async_playwright.start 返回一个协程，需要显示 run
        self.playwright = asyncio.run(async_playwright().start())

        for _ in range(num_browsers):
            if not self.idle_user_ids:
                raise Exception("No idle user")
            user_id = random.choice(self.idle_user_ids)
            self.active_user_ids.append(user_id)
            self.idle_user_ids.remove(user_id)

            user_data_dir = self.user_root_dir + user_id
            task = CrawlerBrowserTask(
                playwright=self.playwright,
                browser_config=self.browser_config,
                user_data_dir=user_data_dir
            )

            self.activated_browser_tasks.append(task)
            io_worker_manager.submit(task)
