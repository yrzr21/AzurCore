from core.base.base_task import BaseTask
from core.utils.SecureEncryptor import SecureEncryptor

"""service 只返回 str 给 controller"""


class EncryptTask(BaseTask):
    def __init__(self, password, data):
        super().__init__("EncryptTask")
        self.encryptor = SecureEncryptor(password)
        self.data = data  # 可以是 str 或 bytes
        self.result = None

    def execute(self):
        self.result = self.encryptor.encrypt(self.data)
        return self.result.decode()


class DecryptTask(BaseTask):
    def __init__(self, password, encrypted_data):
        super().__init__("DecryptTask")
        self.encryptor = SecureEncryptor(password)
        self.data = encrypted_data  # base64编码后的加密数据
        self.result = None

    def execute(self):
        try:
            decrypted = self.encryptor.decrypt_to_string(self.data)
            self.result = decrypted
            return self.result
        except Exception as e:
            print(f"解密失败: {e}")
            return None
