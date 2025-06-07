import os
import sys
import win32com.client  # 仅Windows需要
from pathlib import Path
from PySide6.QtCore import QThread, Signal

'''
继承自QThread，用于在后台执行耗时操作
使用信号（Signal）与主线程通信
run()方法是线程的入口点，执行实际工作
create_shortcut()是核心方法，根据操作系统创建快捷方式
提供取消功能，避免长时间操作无法中断
'''


class ShortcutCreatorWorker(QThread):
    """后台线程处理快捷方式创建"""
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)

    def __init__(self, target_dir, file_paths, create_desktop_shortcut):
        super().__init__()

        self.target_dir = Path(target_dir)
        self.file_paths = file_paths

        # 这俩是干啥的？
        self.create_desktop_shortcut = create_desktop_shortcut
        self.desktop_dir = Path(os.path.join(os.environ['USERPROFILE'], 'Desktop'))

        self.n_files = len(file_paths)

        # 线程终止
        self.canceled = False

    def run(self):
        try:
            # 确保目标目录存在
            self.target_dir.mkdir(parents=True, exist_ok=True)

            for i, file_path in enumerate(self.file_paths):
                if self.canceled:
                    break

                src_path = Path(file_path)
                if not src_path.exists():
                    self.error.emit(f"文件不存在: {src_path}")
                    continue

                # 创建主目录下的快捷方式
                self.create_shortcut(src_path, self.target_dir)

                # 如果勾选桌面创建选项
                if self.create_desktop_shortcut:
                    self.create_shortcut(src_path, self.desktop_dir)

                # 更新进度
                self.progress.emit(int((i + 1) * 100 / self.n_files))

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def create_shortcut(self, src_path, target_dir):
        """实际创建快捷方式的方法（平台兼容处理）"""
        target_path = target_dir / (src_path.stem + ".lnk")

        if sys.platform == 'win32':
            # Windows平台使用WScript
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(target_path))
            shortcut.Targetpath = str(src_path.resolve())
            shortcut.WorkingDirectory = str(src_path.parent.resolve())
            shortcut.save()
        else:
            # 非Windows平台创建符号链接
            target_path.symlink_to(src_path.resolve())

    def cancel(self):
        self.canceled = True
