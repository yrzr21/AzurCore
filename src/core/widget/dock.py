from PySide6.QtWidgets import QWidget, QDockWidget


class Dock(QDockWidget):
    def __init__(self, title, allowed_areas, widget: QWidget):
        super().__init__()
        self.setWindowTitle(title)
        self.setWidget(widget)

        # 允许停靠的区域
        # 例如 Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        self.setAllowedAreas(allowed_areas)
