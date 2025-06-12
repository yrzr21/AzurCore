from PySide6.QtCore import QObject

from plugins.encryptor.encryptor_service import EncryptorService
from plugins.encryptor.encryptor_view import EncryptorView


class EncryptorController(QObject):
    def __init__(self, view: EncryptorView, service: EncryptorService):
        super().__init__()
        self.view = view
        self.service = service

        self.view.encrypt_requested.connect(self.handle_encrypt)
        self.view.decrypt_requested.connect(self.handle_decrypt)

        self.service.task_completed.connect(self._on_task_finished)
        self.service.error_occurred.connect(self._on_task_failed)

    def handle_encrypt(self, password, data):
        if not password or not data:
            self.view.show_error("请输入密码和数据")
            return
        self.service.encrypt_string(password, data)

    def handle_decrypt(self, password, data):
        if not password or not data:
            self.view.show_error("请输入密码和加密数据")
            return
        self.service.decrypt_string(password, data)

    def _on_task_finished(self, task, result):
        self.view.show_result(result)

    def _on_task_failed(self, task, error):
        self.view.show_error(str(error))
