from core.utils.config_manager import config
from core.plugin_manager import plugins
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QDockWidget, QListWidget, QVBoxLayout
from PySide6.QtCore import Qt

from core.utils.file import open_in_default
from core.utils.logger import logger
from core.widget.dock import Dock
from core.widget.file_list import ListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.restore_config()

        self.plugin_widgets = {}  # 插件名 -> QWidget

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.setCentralWidget(self.container)  # ← 只做一次设置！

        # 当前插件名记录
        self.current_plugin = None
        logger.info("初始化成功")

    def init_ui(self):
        self.init_sidebar()
        self.init_menu_bar()

    def init_sidebar(self):
        self.plugin_list = ListWidget(
            current_text_changed_handler=self.switch_plugin
        )

        # 侧边栏
        self.dock = Dock(
            "插件", Qt.LeftDockWidgetArea, self.plugin_list
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

        for plugin_name, plugin in plugins.items():
            widget = plugin.get_widget()
            self.plugin_widgets[plugin_name] = widget
            self.plugin_list.addItem(plugin_name)

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        # layer 0
        file_menu = menu_bar.addMenu("文件")
        # layer 1
        recent_menu = file_menu.addMenu("最近文件")
        recent_files = config["ui_settings"]["recent_files"]
        for file_path in recent_files:
            # 使用 lambda 绑定默认参数
            recent_menu.addAction(file_path, lambda: open_in_default(file_path))

        # layer 0
        menu_bar.addMenu("选项")

    def switch_plugin(self, plugin_name):
        if hasattr(self, 'current_plugin') and self.current_plugin == plugin_name:
            return

        plugin = plugins.plugins.get(plugin_name)
        if not plugin:
            logger.error(f"插件 {plugin_name} 不存在")
            return

        # 从缓存或创建插件界面
        if plugin_name not in self.plugin_widgets:
            self.plugin_widgets[plugin_name] = plugin.get_widget()

        new_widget = self.plugin_widgets[plugin_name]

        # 清空旧插件界面
        while self.container_layout.count():
            old_item = self.container_layout.takeAt(0)
            old_widget = old_item.widget()
            if old_widget:
                old_widget.setParent(None)

        # 加载新插件界面
        self.container_layout.addWidget(new_widget)
        logger.info(f"成功从插件 {self.current_plugin} 切换到 {plugin_name}")
        self.current_plugin = plugin_name

    def restore_config(self):
        """使用 config 设置窗口"""
        app_name = config["app_name"]
        version = config["version"]
        self.setWindowTitle(f"{app_name} v{version}")

        geometry = config["window_geometry"]
        self.setGeometry(
            geometry["x"],
            geometry["y"],
            geometry["width"],
            geometry["height"]
        )

    def save_config(self):
        """保存配置信息到 config"""
        geometry = self.geometry()

        config["window_geometry"] = {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        }

    def closeEvent(self, event):
        """窗口关闭，即程序关闭，此时保存当前配置"""
        super().closeEvent(event)

        # 退出应用
        logger.info("退出应用")
        QApplication.quit()
