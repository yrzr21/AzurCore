from PySide6.QtWidgets import QProgressBar, QWidget, QHBoxLayout


class ProgressBar(QWidget):
    def __init__(self, bar_range=(0, 100), visible=True):
        super().__init__()
        # 语法糖：()+setLayout
        self.main_layout = QHBoxLayout(self)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(bar_range[0], bar_range[1])
        self.progress_bar.setVisible(visible)

        self.main_layout.addWidget(self.progress_bar)

    def set_value(self, value):
        self.progress_bar.setValue(value)

    def set_visible(self, visible):
        self.progress_bar.setVisible(visible)
