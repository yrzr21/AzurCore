import os
import base64
from typing import Union
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class SecureEncryptor:
    def __init__(self, password: str, iterations: int = 100_000, salt_size: int = 16):
        """
        初始化加密器
        :param password: 用户提供的任意长度密钥
        :param iterations: KDF迭代次数
        :param salt_size: 盐的长度
        """
        self.password = password.encode()
        self.iterations = iterations
        self.salt_size = salt_size

    def _derive_key(self, salt: bytes) -> bytes:
        """
        根据密码和盐派生密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        加密数据（支持字符串和字节）
        :return: 返回包含盐和密文的整体字节流
        """
        if isinstance(data, str):
            data = data.encode()

        salt = os.urandom(self.salt_size)
        key = self._derive_key(salt)
        fernet = Fernet(key)
        token = fernet.encrypt(data)

        # 将 salt + token 组合一起返回，方便解密时使用
        return base64.urlsafe_b64encode(salt + token)

    def decrypt(self, token: Union[str, bytes]) -> bytes:
        """
        解密数据（返回字节）
        """
        if isinstance(token, str):
            token = token.encode()

        decoded = base64.urlsafe_b64decode(token)
        salt = decoded[:self.salt_size]
        real_token = decoded[self.salt_size:]

        key = self._derive_key(salt)
        fernet = Fernet(key)
        return fernet.decrypt(real_token)

    def decrypt_to_string(self, token: Union[str, bytes]) -> str:
        """
        解密并返回字符串
        """
        return self.decrypt(token).decode()
