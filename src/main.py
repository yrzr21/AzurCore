from PySide6.QtWidgets import QApplication
from src.core.app import MyApp


def run():
    app = QApplication()
    window = MyApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    run()
