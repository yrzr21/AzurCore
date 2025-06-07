import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QLabel,
    QMessageBox, QProgressBar, QCheckBox
)
from plugins.shortcut_creator._shortcut_creator_worker import ShortcutCreatorWorker


class ShortcutCreatorWindow(QWidget):
    """插件主界面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量快捷方式创建器")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.worker_thread = None

    def init_ui(self):
        """
        创建并组织所有界面元素
        使用布局管理器（QVBoxLayout, QHBoxLayout）自动排列控件
        包含：
            目标目录选择区
            文件列表显示区
            文件操作按钮区
            选项区（复选框）
            进度条
            操作按钮区
        """
        layout = QVBoxLayout()

        # 目标目录选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标目录:"))

        self.target_input = QLineEdit()
        target_layout.addWidget(self.target_input)

        self.target_browse_btn = QPushButton("浏览...")
        self.target_browse_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(self.target_browse_btn)

        # 文件列表
        file_list_layout = QHBoxLayout()
        self.file_list = QListWidget()
        file_list_layout.addWidget(self.file_list)

        btn_layout = QVBoxLayout()
        self.add_files_btn = QPushButton("添加文件")
        self.add_files_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(self.add_folder_btn)

        self.clear_list_btn = QPushButton("清空列表")
        self.clear_list_btn.clicked.connect(self.clear_file_list)
        btn_layout.addWidget(self.clear_list_btn)

        file_list_layout.addLayout(btn_layout)

        # 额外选项
        option_layout = QHBoxLayout()
        self.desktop_checkbox = QCheckBox("同时在桌面创建快捷方式")
        option_layout.addWidget(self.desktop_checkbox)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)

        # 操作按钮
        action_layout = QHBoxLayout()
        self.create_btn = QPushButton("创建快捷方式")
        self.create_btn.clicked.connect(self.create_shortcuts)
        self.create_btn.setEnabled(False)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.cancel_btn.setEnabled(False)

        action_layout.addWidget(self.create_btn)
        action_layout.addWidget(self.cancel_btn)

        # 组合所有布局
        layout.addLayout(target_layout)
        layout.addLayout(file_list_layout)
        layout.addLayout(option_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(action_layout)

        self.setLayout(layout)

        # 监听状态变化
        self.target_input.textChanged.connect(self.validate_inputs)
        self.file_list.model().rowsInserted.connect(self.validate_inputs)
        self.file_list.model().rowsRemoved.connect(self.validate_inputs)

    def browse_target(self):
        """选择目标目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择目标目录",
            os.path.expanduser("~")
        )
        if directory:
            self.target_input.setText(directory)

    def add_files(self):
        """添加文件到列表"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择文件",
            os.path.expanduser("~")
        )
        if files:
            for file_path in files:
                self.file_list.addItem(file_path)

    def add_folder(self):
        """添加文件夹中的所有文件到列表"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择文件夹",
            os.path.expanduser("~")
        )
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.file_list.addItem(file_path)

    def clear_file_list(self):
        """清空文件列表"""
        self.file_list.clear()

    def validate_inputs(self):
        """验证输入是否完整"""
        has_target = bool(self.target_input.text().strip())
        has_files = self.file_list.count() > 0
        self.create_btn.setEnabled(has_target and has_files)

    def create_shortcuts(self):
        """开始创建快捷方式"""
        target_dir = self.target_input.text().strip()
        file_paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        create_desktop = self.desktop_checkbox.isChecked()

        # 创建后台线程
        self.worker_thread = ShortcutCreatorWorker(
            target_dir,
            file_paths,
            create_desktop
        )

        # 连接信号
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_success)
        self.worker_thread.error.connect(self.show_error)

        # 更新UI状态
        self.create_btn.setEnabled(False)
        self.target_input.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 启动线程
        self.worker_thread.start()

    def cancel_operation(self):
        """取消操作"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.cancel_btn.setEnabled(False)
            QMessageBox.information(self, "操作取消", "操作已被用户取消")
            self.reset_ui()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def on_success(self):
        """操作完成处理"""
        QMessageBox.information(
            self,
            "操作完成",
            f"成功创建了{self.file_list.count()}个快捷方式!"
        )
        self.reset_ui()

    def show_error(self, message):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", message)

    def reset_ui(self):
        """重置UI状态"""
        self.target_input.setEnabled(True)
        self.create_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait(500)
            self.worker_thread = None
