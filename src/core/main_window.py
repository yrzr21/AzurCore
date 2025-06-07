from core.config_manager import config
from core.plugin_manager import plugins
from PySide6.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.restore_config()

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

    def init_ui(self):
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("&文件")

        # 添加最近文件
        recent_files = config["ui_settings"]["recent_files"]
        if recent_files:
            recent_menu = file_menu.addMenu("最近文件")
            for file_path in recent_files:
                recent_menu.addAction(file_path)

        # 插件菜单
        plugin_menu = menu_bar.addMenu("&插件")
        for plugin_name, plugin in plugins.items():
            plugin.setup_menu(plugin_menu)

        # 选项菜单
        options_menu = menu_bar.addMenu("&选项")

    def closeEvent(self, event):
        """窗口关闭，即程序关闭，此时保存当前配置"""
        super().closeEvent(event)

        config.save()

        # 退出应用
        QApplication.quit()
