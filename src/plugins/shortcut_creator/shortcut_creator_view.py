import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, QProgressBar, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal


class ShortcutCreatorView(QWidget):
    """纯UI组件，不包含业务逻辑"""

    create_requested = Signal(dict)  # 传递数据字典
    cancel_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量快捷方式创建器")
        self.setMinimumSize(600, 400)

        self.init_ui()
        self.set_ui_state(busy=False)
        self.setAcceptDrops(True)

    def init_ui(self):
        """create ui and connect signals"""
        # 主容器：垂直布局
        self.layout = QVBoxLayout(self)

        # 目标目录选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标目录:"))
        self.target_input = QLineEdit()
        target_layout.addWidget(self.target_input)
        self.target_browse_btn = QPushButton("浏览...")
        target_layout.addWidget(self.target_browse_btn)
        self.layout.addLayout(target_layout)

        # 文件列表区域
        file_list_layout = QHBoxLayout()
        self.file_list = QListWidget()
        file_list_layout.addWidget(self.file_list)

        btn_layout = QVBoxLayout()
        self.add_files_btn = QPushButton("添加文件")
        self.add_folder_btn = QPushButton("添加文件夹")
        self.clear_list_btn = QPushButton("清空列表")

        btn_layout.addWidget(self.add_files_btn)
        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.clear_list_btn)

        file_list_layout.addLayout(btn_layout)
        self.layout.addLayout(file_list_layout)

        # 选项区域
        option_layout = QHBoxLayout()
        self.desktop_checkbox = QCheckBox("同时在桌面创建快捷方式")
        option_layout.addWidget(self.desktop_checkbox)
        self.layout.addLayout(option_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # 操作按钮
        action_layout = QHBoxLayout()
        self.create_btn = QPushButton("创建快捷方式")
        self.cancel_btn = QPushButton("取消")

        self.create_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

        action_layout.addWidget(self.create_btn)
        action_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(action_layout)

        # 连接UI事件信号
        self.target_browse_btn.clicked.connect(self._on_browse_target)
        self.add_files_btn.clicked.connect(self._on_add_files)
        self.add_folder_btn.clicked.connect(self._on_add_folder)
        self.clear_list_btn.clicked.connect(self._on_clear_list)

        # 触发服务层事件
        self.create_btn.clicked.connect(self._on_create_shortcuts)
        self.cancel_btn.clicked.connect(self._on_cancel)

        # 输入变化监听
        self.target_input.textChanged.connect(self._on_inputs_changed)
        self.file_list.model().rowsInserted.connect(self._on_inputs_changed)
        self.file_list.model().rowsRemoved.connect(self._on_inputs_changed)

    def get_ui_data(self):
        """获取用户输入数据"""
        return {
            "target_dir": self.target_input.text().strip(),
            "file_paths": [self.file_list.item(i).text() for i in range(self.file_list.count())]
        }

    # UI更新方法
    def update_progress(self, value):
        self.progress_bar.setValue(value)

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
        self.add_files_btn.setEnabled(not busy)
        self.add_folder_btn.setEnabled(not busy)
        self.clear_list_btn.setEnabled(not busy)
        self.desktop_checkbox.setEnabled(not busy)
        self.create_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.progress_bar.setVisible(busy)

        if not busy:
            # 清空进度条
            self.progress_bar.setValue(0)

    def reset_ui(self):
        """重置UI到初始状态"""
        self.set_ui_state(busy=False)
        self.progress_bar.setValue(0)

    # ui signal handler

    def _on_browse_target(self):
        directory = self.browse_folder()
        if directory:
            self.target_input.setText(directory)

    def _on_add_files(self):
        items = self.open_files()
        if items:
            self.file_list.addItems(items)

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
        self.create_btn.setEnabled(
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

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QDragEnterEvent, QDropEvent

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    paths.append(path)
                elif os.path.isdir(path):
                    paths.extend(self._scan_folder(path))  # 添加文件夹内容
            if paths:
                self.file_list.addItems(paths)
            event.acceptProposedAction()

