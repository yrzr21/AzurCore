from core.config_manager import config
from core.plugin_manager import plugins
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QDockWidget, QListWidget, QVBoxLayout
from PySide6.QtCore import Qt


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

    def init_ui(self):
        self.init_sidebar()
        self.init_menu_bar()

    def init_sidebar(self):
        # 侧边栏
        self.dock = QDockWidget("插件", self)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin_list = QListWidget()
        self.plugin_list.currentTextChanged.connect(self.switch_plugin)
        self.dock.setWidget(self.plugin_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

        for plugin_name, plugin in plugins.items():
            widget = plugin.get_widget()
            self.plugin_widgets[plugin_name] = widget
            self.plugin_list.addItem(plugin_name)

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&文件")
        recent_files = config["ui_settings"]["recent_files"]
        if recent_files:
            recent_menu = file_menu.addMenu("最近文件")
            for file_path in recent_files:
                recent_menu.addAction(file_path)

        options_menu = menu_bar.addMenu("&选项")

    def switch_plugin(self, plugin_name):
        if hasattr(self, 'current_plugin') and self.current_plugin == plugin_name:
            return

        plugin = plugins.plugins.get(plugin_name)
        if not plugin:
            print(f"插件 {plugin_name} 不存在")
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
        config.save()

    def closeEvent(self, event):
        """窗口关闭，即程序关闭，此时保存当前配置"""
        super().closeEvent(event)

        config.save()

        # 退出应用
        QApplication.quit()
