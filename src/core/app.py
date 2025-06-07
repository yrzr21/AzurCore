from PySide6.QtWidgets import QMainWindow
from src.core.plugin_manager import PluginManager

plugin_dir = "E:\develop\Projects\MyApp\src\plugins"


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Super App")
        self.setGeometry(100, 100, 1000, 700)

        # 插件系统初始化
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins(plugin_dir)

        # 创建菜单系统
        self._create_menu()

    def _create_menu(self):
        menu_bar = self.menuBar()

        # 动态生成插件菜单
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            plugin_menu = menu_bar.addMenu(f"&{plugin_name}")
            plugin.setup_menu(plugin_menu)
