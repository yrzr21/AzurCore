from PySide6.QtWidgets import QApplication

from core.config_manager import config
from core.main_window import MainWindow
from core.plugin_manager import plugins


class MyApp():
    def __init__(self):
        super().__init__()
        self.app = QApplication()

        plugins.load_plugins()

        self.main_window = MainWindow()
        self.main_window.init_ui()
        self.main_window.show()

    def run(self):
        self.app.exec()

    def __del__(self):
        config.save()


if __name__ == "__main__":
    MyApp().run()
