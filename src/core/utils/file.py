import os

from PySide6.QtWidgets import QFileDialog, QWidget

from core.utils.logger import logger


def valid_dir(path):
    """检查路径是否是有效的文件夹"""
    return os.path.exists(path) and os.path.isdir(path)


def browse_folder(parent: QWidget, title, start_path="~"):
    """打开目录选择对话框，选择一个目录并返回其路径"""
    return _open_dialog(parent, QFileDialog.getExistingDirectory, title, start_path)


def open_files(parent: QWidget, title, start_path="~"):
    """打开文件选择对话框"，选择一个或多个文件并返回其路径列表"""
    files, _ = _open_dialog(parent, QFileDialog.getOpenFileNames, title, start_path)
    logger.debug(f"选择的文件: {files},_={_}")
    return files or []


def _open_dialog(self, dialog_func, title, start_path):
    """
    通用对话框打开方法
    不指定父控件可能导致：
        对话框失去焦点后难以找回
        在某些系统上显示在错误位置
        对话框独立于应用之外（在任务栏单独显示）
        用户可能忽略对话框继续操作主窗口
    """
    start_path = os.path.expanduser(start_path)
    result = dialog_func(self, title, start_path)
    return result if result else None


def scan_folder_files(folder_path, max_depth=0):
    """
    扫描文件夹,返回其中文件路径和文件夹路径列表
    max_depth: 最大扫描深度,默认为0,即只扫描当前目录的文件
    """

    file_list, folder_list = scan_folder(folder_path)

    if max_depth > 0:
        for folder in folder_list:
            sub_file_list = scan_folder_files(folder, max_depth - 1)[0]
            file_list.extend(sub_file_list)

    return file_list, []


def scan_folder(folder_path):
    """扫描文件夹中的文件,返回其中文件路径和文件夹路径列表"""
    if not valid_dir(folder_path):
        raise ValueError("Invalid folder path")

    file_list = []
    dir_list = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            file_list.append(entry.path)
        else:
            dir_list.append(entry.path)

    return file_list, dir_list
