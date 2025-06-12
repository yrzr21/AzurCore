from plugins.encryptor.encryptor_controller import EncryptorController
from plugins.encryptor.encryptor_service import EncryptorService
from plugins.encryptor.encryptor_view import EncryptorView
from core.utils.config_manager import config


class Plugin:
    def __init__(self):
        self.name = "加密解密器"
        self.version = "1.0"

        interval = config["plugins"]["encryptor"]["interval"]
        max_load = config["plugins"]["encryptor"]["max_load"]

        self.service = EncryptorService(interval, max_load)
        self.view = EncryptorView()
        self.controller = EncryptorController(self.view, self.service)

    def get_widget(self):
        return self.view
