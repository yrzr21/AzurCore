from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout
from PySide6.QtCore import Signal


class ListWidget(QWidget):
    """基础列表组件"""

    def __init__(self, change_handler=None):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.model().rowsInserted.connect(change_handler)
        self.list_widget.model().rowsRemoved.connect(change_handler)
        self.main_layout.addWidget(self.list_widget)

    def item(self, index):
        return self.list_widget.item(index)

    def count(self):
        """获取文件数量"""
        return self.list_widget.count()

    def setEnabled(self, enabled):
        """设置组件启用状态"""
        self.list_widget.setEnabled(enabled)

    def addItems(self, items):
        """批量添加项目"""
        self.list_widget.addItems(items)

    def clear(self):
        """清空文件列表"""
        self.list_widget.clear()
