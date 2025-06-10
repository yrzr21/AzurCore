from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout
from PySide6.QtCore import Signal


class ListWidget(QListWidget):
    """基础列表组件"""

    def __init__(self, row_handler=None, current_text_changed_handler=None):
        super().__init__()

        if row_handler:
            self.model().rowsInserted.connect(row_handler)
            self.model().rowsRemoved.connect(row_handler)

        if current_text_changed_handler:
            self.currentTextChanged.connect(current_text_changed_handler)
