from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton

from core.utils.logger import logger


class ButtonGrid(QWidget):
    def __init__(self, layout_class, button_texts, button_handlers):
        super().__init__()
        # 不能用语法糖：layout_class(self)
        # 更通用、支持动态类传入
        self.main_layout = layout_class()
        self.setLayout(self.main_layout)

        self.buttons = {}  # text: button
        self.add_buttons(button_texts, button_handlers)

    def add_buttons(self, button_texts, button_handlers):
        """批量添加按钮，存储引用"""
        if isinstance(button_texts, str):
            # 处理单个按钮
            button = QPushButton(button_texts)
            if callable(button_handlers):
                button.clicked.connect(button_handlers)
            self.main_layout.addWidget(button)

            # 存储引用
            self.buttons[button_texts] = button
            return

        # 处理多个按钮
        for i, (text, handler) in enumerate(zip(button_texts, button_handlers)):
            button = QPushButton(text)
            if callable(handler):
                button.clicked.connect(handler)
            self.main_layout.addWidget(button)

            # 存储引用
            self.buttons[text] = button

    # 设置特定按钮启用状态的方法
    def set_all_enabled(self, enabled):
        """
        设置所有按钮的启用状态
        :param enabled: True/False
        """
        for button in self.buttons.values():
            button.setEnabled(enabled)

    def set_button_enabled(self, button_key, enabled):
        """
        设置特定按钮的启用状态

        :param button_key: 按钮文本
        :param enabled: True/False
        """

        if button_key in self.buttons:
            self.buttons[button_key].setEnabled(enabled)
