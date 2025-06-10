import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from core.utils.logger import logger
from core.utils.File import browse_folder, open_files, scan_folder_files
from core.widget.button_grid import ButtonGrid
from core.widget.file_list import ListWidget
from core.widget.input_bar import InputBar
from core.widget.progress_bar import ProgressBar


class ShortcutCreatorView(QWidget):
    """纯UI组件，不包含业务逻辑"""

    create_requested = Signal(dict)  # 传递数据字典
    cancel_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量快捷方式创建器")
        self.setMinimumSize(600, 400)

        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.set_ui_state(busy=False)
        self.setAcceptDrops(True)

    def init_ui(self):
        """create ui and connect signals"""

        # 目标目录选择
        self.target_input = InputBar(
            "目标目录:", "浏览...",
            self._on_inputs_changed,
            self._on_browse_target
        )

        # 文件列表区域
        file_area_layout = QHBoxLayout()
        self.file_list = ListWidget(self._on_inputs_changed)
        self.file_actions = ButtonGrid(
            QVBoxLayout,
            ["添加文件", "添加文件夹", "添加文件夹下所有文件", "清空列表"],
            [
                self._on_add_files,
                self._on_add_folder,
                self._on_add_folder_files,
                self._on_clear_list
            ]
        )
        file_area_layout.addWidget(self.file_list, 5)
        file_area_layout.addWidget(self.file_actions, 1)

        # 进度条
        self.progress_bar = ProgressBar(visible=False)

        # 操作按钮
        self.confirmation_actions = ButtonGrid(
            QHBoxLayout,
            ["创建快捷方式", "取消"],
            [
                self._on_create_shortcuts,
                self._on_cancel
            ]
        )

        # 添加到主布局
        self.main_layout.addWidget(self.target_input)
        self.main_layout.addLayout(file_area_layout)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.confirmation_actions)

    def get_ui_data(self):
        """获取用户输入数据"""
        return {
            "target_dir": self.target_input.text().strip(),
            "file_paths": [self.file_list.item(i).text() for i in range(self.file_list.count())]
        }

    # UI更新方法
    def update_progress(self, value):
        self.progress_bar.set_value(value)

    def show_message(self, title, message, is_error=False):
        """显示消息弹窗"""
        if is_error:
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def set_ui_state(self, busy=False):
        """设置UI状态 (busy=True表示操作中)"""
        self.target_input.setEnabled(not busy)

        self.file_list.setEnabled(not busy)
        self.file_actions.set_all_enabled(not busy)

        self.confirmation_actions.set_button_enabled("创建快捷方式", not busy)
        self.confirmation_actions.set_button_enabled("取消", busy)
        self.progress_bar.set_visible(busy)

        if not busy:
            # 清空进度条
            self.progress_bar.set_value(0)

    def reset_ui(self):
        """重置UI到初始状态"""
        self.set_ui_state(busy=False)
        self.progress_bar.set_value(0)

    # ui signal handler
    def _on_inputs_changed(self):
        data = self.get_ui_data()
        self.confirmation_actions.set_button_enabled(
            "创建快捷方式",
            bool(data["target_dir"]) and bool(data["file_paths"])
        )

    def _on_browse_target(self):
        directory = browse_folder(self, "选择目录")
        logger.debug(f"选择的文件夹: {directory}")
        if directory:
            self.target_input.setText(directory)

    def _on_add_files(self):
        items = open_files(self, "选择文件")
        if items:
            self.file_list.addItems(items)

    def _on_add_folder(self):
        folder = browse_folder(self, "选择目录")
        if folder:
            self.file_list.addItem(folder)

    def _on_add_folder_files(self):
        folder = browse_folder(self, "选择包含文件的文件夹")
        if folder:
            files, _ = scan_folder_files(folder, max_depth=1000)
            self.file_list.addItems(files)

    def _on_clear_list(self):
        self.file_list.clear()

    def _on_create_shortcuts(self):
        data = self.get_ui_data()
        self.create_requested.emit(data)

    def _on_cancel(self):
        self.cancel_requested.emit()

    # 重写拖拽事件
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) or os.path.isdir(path):
                    paths.append(path)
            if paths:
                self.file_list.addItems(paths)
            event.acceptProposedAction()
