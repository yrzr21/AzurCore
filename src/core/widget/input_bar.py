from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton


class InputBar(QWidget):
    """QLabel + QLineEdit + QPushButton"""

    def __init__(self, label_text="", button_text="Click", input_changed_handler=None, button_handler=None):
        super().__init__()
        self.main_layout = QHBoxLayout(self)

        self.label = QLabel(label_text)
        self.line_edit = QLineEdit()
        self.button = QPushButton(button_text)

        self.button.clicked.connect(button_handler)
        self.line_edit.textChanged.connect(input_changed_handler)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addWidget(self.button)

    # QLineEdit
    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

    def setPlaceholderText(self, text):
        self.line_edit.setPlaceholderText(text)

    def setEnabled(self, enabled):
        self.line_edit.setEnabled(enabled)

    # QLabel
    def setLabelText(self, text):
        self.label.setText(text)

    # QPushButton
    def setButtonText(self, text):
        self.button.setText(text)
