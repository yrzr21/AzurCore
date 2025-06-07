from plugins.shortcut_creator._shortcut_creator_window import ShortcutCreatorWindow


# 在 target_dir 下为 file_paths 中的每个文件创建快捷方式
# target_dir、file_paths 任一不存在则报错，并清除已创建的快捷方式，即原子操作
class Plugin:
    def __init__(self):
        self.name = "快捷方式创建器"
        self.version = "1.0"
        self.description = "在指定目录批量创建文件的快捷方式"
        self.author = "你的名字"

    def setup_menu(self, parent_menu):
        """向主菜单添加功能项"""
        self.action = parent_menu.addAction("批量创建快捷方式")
        self.action.triggered.connect(self.show_ui)

    def run_feature(self):
        """核心功能实现"""
        print("执行插件功能...")
        # 这里添加你的具体功能代码
        # 例如打开文件、数据分析、网络请求等

    def cleanup(self):
        """插件卸载时清理资源"""
        pass

    def show_ui(self):
        """
        显示插件UI
        当用户点击菜单项时，显示插件的主界面
        """
        self.window = ShortcutCreatorWindow()
        self.window.show()
