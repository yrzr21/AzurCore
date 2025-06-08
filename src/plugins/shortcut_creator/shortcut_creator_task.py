import os

import pythoncom
import win32com.client

from core.base.base_task import BaseTask


class ShortcutCreationTask(BaseTask):
    """任务实体"""

    def __init__(self, target_dir, file_paths):
        super().__init__("ShortcutCreationTask")
        self.target_dir = os.path.abspath(target_dir)
        self.file_paths = [os.path.abspath(p) for p in file_paths]
        self.created_files = []

    def execute(self):
        """执行创建任务"""
        print("execute ShortcutCreationTask")
        pythoncom.CoInitialize()

        total_files = len(self.file_paths)
        try:
            for i, file_path in enumerate(self.file_paths):
                if self._is_canceled:
                    self._cleanup()
                    total_files = 0
                    break

                self._create_single_shortcut(file_path, self.target_dir)
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)

        finally:
            # 保证一定执行这里
            pythoncom.CoUninitialize()

        return total_files

    # helpers
    def _create_single_shortcut(self, target_path, output_dir):
        """在 output_dir 下创建 target_path 的快捷方式"""
        file_name = os.path.basename(target_path)
        lnk_name = f"{os.path.splitext(file_name)[0]}.lnk"
        lnk_path = os.path.join(output_dir, lnk_name)

        # 生成唯一文件名
        if os.path.exists(lnk_path):
            counter = 1
            while os.path.exists(lnk_path):
                lnk_name = f"{os.path.splitext(file_name)[0]}_{counter}.lnk"
                lnk_path = os.path.join(output_dir, lnk_name)
                counter += 1

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.Save()
            self.created_files.append(lnk_path)
            return lnk_path
        except Exception as e:
            import traceback
            print(f"创建快捷方式失败: {file_name}\n{traceback.format_exc()}")
            raise RuntimeError(f"创建快捷方式失败: {file_name}") from e

    def _cleanup(self):
        """清理已创建的文件（业务逻辑）"""
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        self.created_files = []
