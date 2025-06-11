from PySide6.QtCore import QTimer


class TimeoutTimer:
    def __init__(self, interval: int, timeout_handler, start_time=None):
        """start_time 默认使用当前时间"""
        self._timer = QTimer()
        self._timer.setInterval(interval)
        self._timer.timeout.connect(timeout_handler)

        if start_time is None:
            self._timer.start()
        else:
            self._timer.start(start_time)

    def stop(self):
        self._timer.stop()

    def start(self):
        self._timer.start()
