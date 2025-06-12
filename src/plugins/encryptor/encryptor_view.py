from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Signal

from core.widget.button_grid import ButtonGrid
from core.widget.input_bar import InputBar


class EncryptorView(QWidget):
    encrypt_requested = Signal(str, str)
    decrypt_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("加密解密器")
        self.setMinimumSize(400, 300)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # 密码输入
        self.password_input = InputBar(
            label_text="密码: "
        )
        layout.addWidget(self.password_input)

        # 原始数据输入
        self.input_text = InputBar(
            label_text="输入数据: ",
            multiline=True
        )
        layout.addWidget(self.input_text)

        # 结果输出
        self.output_text = InputBar(
            label_text="输出结果: ",
            multiline=True
        )
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # 按钮区
        self.encrypt_btn = ButtonGrid(
            QHBoxLayout,
            ["加密", "解密"],
            [self._on_encrypt_clicked, self._on_decrypt_clicked]
        )
        layout.addWidget(self.encrypt_btn)

        # 设置布局
        self.setLayout(layout)

    def _on_encrypt_clicked(self):
        password = self.password_input.text().strip()
        data = self.input_text.text()
        self.encrypt_requested.emit(password, data)

    def _on_decrypt_clicked(self):
        password = self.password_input.text().strip()
        data = self.input_text.text()
        self.decrypt_requested.emit(password, data)

    def show_result(self, result: str):
        self.output_text.setText(result)

    def show_error(self, message: str):
        QMessageBox.critical(self, "错误", message)
