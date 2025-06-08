import os

from plugins.shortcut_creator.shortcut_creator_task import ShortcutCreationTask
from core.base.base_service import BaseService


class ShortcutCreatorService(BaseService):
    """负责处理业务逻辑协调、任务管理和结果处理"""

    def __init__(self):
        super().__init__("ShortcutCreatorService")

    def create_shortcuts(self, target_dir, file_paths):
        """创建快捷方式任务"""
        print("ShortcutCreatorService")
        task = ShortcutCreationTask(target_dir, file_paths)
        self.deliver(task)

    def validate_input(self, target_dir, file_paths):
        """业务逻辑验证"""
        if not target_dir:
            self.error_occurred.emit("目标目录不能为空", "")
            return False

        if not os.path.exists(target_dir) and os.path.isdir(target_dir):
            self.error_occurred.emit(f"{target_dir}不存在或不是文件夹", "")
            return False

        if not file_paths:
            self.error_occurred.emit("请选择至少一个文件", "")
            return False

        missing_files = [f for f in file_paths if not os.path.exists(f)]
        if missing_files:
            self.error_occurred.emit(
                f"以下文件不存在: {', '.join(missing_files[:3])}{'等' if len(missing_files) > 3 else ''}",
                ""
            )
            return False

        return True
