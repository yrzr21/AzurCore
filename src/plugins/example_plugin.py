from PySide6.QtGui import QAction


class Plugin:
    def __init__(self):
        self.name = "示例插件"

    def setup_menu(self, parent_menu):
        """向主菜单添加功能项"""
        # 添加菜单项
        action = QAction("运行功能", parent_menu)
        action.triggered.connect(self.run_feature)
        parent_menu.addAction(action)

    def run_feature(self):
        """核心功能实现"""
        print("执行插件功能...")
        # 这里添加你的具体功能代码
        # 例如打开文件、数据分析、网络请求等

    def cleanup(self):
        """插件卸载时清理资源"""
        pass
