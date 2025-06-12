from plugins.shortcut_creator.shortcut_creator_controller import ShortcutCreatorController
from plugins.shortcut_creator.shortcut_creator_service import ShortcutCreatorService
from plugins.shortcut_creator.shortcut_creator_view import ShortcutCreatorView
from core.utils.config_manager import config


# 在 target_dir 下为 file_paths 中的每个文件创建快捷方式
# target_dir、file_paths 任一不存在则报错，并清除已创建的快捷方式，即原子操作
class Plugin:
    def __init__(self):
        self.name = "快捷方式创建器"
        self.version = "1.0"
        self.description = "在指定目录批量创建文件的快捷方式"
        self.author = "你的名字"

        default_selected_dir = config["plugins"]["shortcut_creator"]["default_selected_dir"]
        default_target_dir = config["plugins"]["shortcut_creator"]["default_target_dir"]

        self.view = ShortcutCreatorView(default_selected_dir, default_target_dir)
        self.service = ShortcutCreatorService()
        self.controller = ShortcutCreatorController(self.view, self.service)

    def get_widget(self):
        return self.view
