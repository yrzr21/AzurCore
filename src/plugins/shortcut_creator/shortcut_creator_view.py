import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, QProgressBar, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

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

    def _on_browse_target(self):
        directory = self.browse_folder()
        if directory:
            self.target_input.setText(directory)

    def _on_add_files(self):
        items = self.open_files()
        if items:
            self.file_list.addItems(items)

    def _on_add_folder_files(self):
        folder = self.browse_folder("选择包含文件的文件夹")
        if folder:
            files = self._scan_folder(folder)
            self.add_unique_items(files)

    def _on_add_folder(self):
        folder = self.browse_folder()
        if folder:
            files = self._scan_folder(folder)
            self.file_list.addItems(files)

    def _on_clear_list(self):
        self.file_list.clear()

    def _on_create_shortcuts(self):
        data = self.get_ui_data()
        self.create_requested.emit(data)

    def _on_cancel(self):
        self.cancel_requested.emit()

    def _on_inputs_changed(self):
        data = self.get_ui_data()
        self.confirmation_actions.set_button_enabled(
            "创建快捷方式",
            bool(data["target_dir"]) and bool(data["file_paths"])
        )

    # ui helpers
    def browse_folder(self, title="选择目录", start_path="~"):
        """打开目录选择对话框"""
        return self._open_dialog(QFileDialog.getExistingDirectory, title, start_path)

    def open_files(self, title="选择文件", start_path="~"):
        """打开文件选择对话框"""
        files, _ = self._open_dialog(QFileDialog.getOpenFileNames, title, start_path)
        return files or []

    def _open_dialog(self, dialog_func, title, start_path):
        """通用对话框打开方法"""
        start_path = os.path.expanduser(start_path)
        result = dialog_func(self, title, start_path)
        return result if result else None

    def _scan_folder(self, folder_path, max_depth=2):
        """扫描文件夹中的文件 (UI工具方法)"""
        files = []
        for root, _, filenames in os.walk(folder_path):
            depth = root.replace(folder_path, "").count(os.sep)
            if max_depth is not None and depth >= max_depth:
                continue
            files.extend(os.path.join(root, f) for f in filenames)
        return files

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

    def add_unique_items(self, paths):
        existing = set(self.file_list.item(i).text() for i in range(self.file_list.count()))
        new_items = [p for p in paths if p not in existing]
        self.file_list.addItems(new_items)
