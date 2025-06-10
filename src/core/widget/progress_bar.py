from PySide6.QtWidgets import QProgressBar, QWidget, QHBoxLayout


class ProgressBar(QProgressBar):
    def __init__(self, bar_range=(0, 100), visible=True):
        super().__init__()

        self.setRange(bar_range[0], bar_range[1])
        self.setVisible(visible)
