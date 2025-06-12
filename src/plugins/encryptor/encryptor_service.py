from core.base.base_service import BatchedService
from core.utils.logger import logger
from plugins.encryptor.encryptor_task import EncryptTask, DecryptTask


class EncryptorService(BatchedService):
    """目前只支持 utf-8 字符串加密，todo：支持其他类型数据的加密"""

    def __init__(self, interval, max_load):
        super().__init__("EncryptorService", interval, max_load)

    def encrypt_string(self, password: str, data: str):
        """加密数据，返回 key 和加密后的数据"""
        logger.debug(f"password={password}, data={data}")
        task = EncryptTask(password, data)
        self.deliver(task)

    def decrypt_string(self, password: str, encrypted_data: str):
        """解密数据，返回解密后的数据"""
        logger.debug(f"password={password}, data={encrypted_data}")
        task = DecryptTask(password, encrypted_data)
        self.deliver(task)

    def load_size(self, task):
        # todo: 更智能化的评估方式
        return 10