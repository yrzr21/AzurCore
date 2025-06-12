from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit


class InputBar(QWidget):
    """
    QLabel + QLineEdit/QTextEdit + QPushButton
    继续封装 InputBar 不是很明智（例如使用默认 handler），因为 handler 一般与业务逻辑紧耦合
    """

    def __init__(self, label_text="", button_text=None,
                 input_changed_handler=None, button_handler=None,
                 multiline=False):
        super().__init__()
        self.main_layout = QHBoxLayout(self)

        # QLabel
        self.label = QLabel(label_text)
        self.main_layout.addWidget(self.label)

        # QLineEdit/QTextEdit
        self.multiline = multiline
        if self.multiline:
            self.input_widget = QTextEdit()
        else:
            self.input_widget = QLineEdit()
        if input_changed_handler is not None:
            self.input_widget.textChanged.connect(input_changed_handler)
        self.main_layout.addWidget(self.input_widget)

        # QPushButton
        self.button = None
        if button_text is not None:
            self.button = QPushButton(button_text)
            self.button.clicked.connect(button_handler)
            self.main_layout.addWidget(self.button)

    # QLineEdit
    def text(self):
        if self.multiline:
            return self.input_widget.toPlainText()
        return self.input_widget.text()

    def setText(self, text):
        if self.multiline:
            self.input_widget.setPlainText(text)
        else:
            self.input_widget.setText(text)

    def setPlaceholderText(self, text):
        if not self.multiline:
            self.input_widget.setPlaceholderText(text)
        # QTextEdit 没有 placeholder，可以拓展支持 QTextEdit placeholder hack

    def setEnabled(self, enabled):
        self.input_widget.setEnabled(enabled)

    def setReadOnly(self, readonly: bool = True):
        self.input_widget.setReadOnly(readonly)

    # QLabel
    def setLabelText(self, text):
        self.label.setText(text)

    # QPushButton
    def setButtonText(self, text):
        if self.button:
            self.button.setText(text)
