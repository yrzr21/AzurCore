from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class TestPluginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("这是一个测试插件")
        self.button = QPushButton("点击我")
        self.button.clicked.connect(self.on_click)

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_click(self):
        self.label.setText("按钮被点击了！")
