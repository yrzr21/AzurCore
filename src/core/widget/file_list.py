import os

from PySide6.QtGui import QDragEnterEvent, QDropEvent, Qt
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QAbstractItemView
from PySide6.QtCore import Signal


class ListWidget(QListWidget):
    """基础列表组件"""

    def __init__(self, row_handler=None, current_text_changed_handler=None, accept_drop=False):
        super().__init__()

        if accept_drop:
            self.setAcceptDrops(True)
            self.setDragDropMode(QAbstractItemView.DropOnly)
            self.viewport().setAcceptDrops(True)
            self.setDefaultDropAction(Qt.CopyAction)

        if row_handler:
            self.model().rowsInserted.connect(row_handler)
            self.model().rowsRemoved.connect(row_handler)

        if current_text_changed_handler:
            self.currentTextChanged.connect(current_text_changed_handler)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """接受包含URL的拖拽事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """保持拖拽状态"""
        event.acceptProposedAction() if event.mimeData().hasUrls() else event.ignore()

    def dropEvent(self, event: QDropEvent):
        """处理文件放置"""
        if event.mimeData().hasUrls():
            paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if os.path.exists(url.toLocalFile())
            ]
            if paths:
                self.add_unique(paths)
            event.acceptProposedAction()

    def add_unique(self, paths):
        existing = set(self.item(i).text() for i in range(self.count()))
        new_items = [p for p in paths if p not in existing]
        self.addItems(new_items)