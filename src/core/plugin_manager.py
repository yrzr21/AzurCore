import importlib
from pathlib import Path


class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.plugin_dirs = {}  # 存储插件路径

    def load_plugins(self, plugin_root_dir):
        """加载指定目录下所有的插件文件夹"""
        plugins_path = Path(plugin_root_dir)

        # 遍历所有子目录
        for plugin_dir in plugins_path.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                self._load_plugin(plugin_dir)

    def _load_plugin(self, plugin_dir):
        """加载单个插件文件夹"""
        plugin_name = plugin_dir.name

        try:
            # 查找插件入口文件
            entry_file = None
            possible_files = ["__init__.py", "plugin.py", plugin_name + ".py"]

            for file in possible_files:
                candidate = plugin_dir / file
                if candidate.exists():
                    entry_file = candidate
                    break

            if not entry_file:
                print(f"在 {plugin_dir} 中找不到插件入口文件")
                return

            # 动态导入插件模块
            module_name = f"plugins.{plugin_name}"  # 使用相对导入路径
            spec = importlib.util.spec_from_file_location(module_name, entry_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 实例化插件主类
            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class()

            # 存储插件实例及其目录路径
            self.plugins[plugin_name] = plugin_instance
            self.plugin_dirs[plugin_name] = plugin_dir

            print(f"成功加载插件: {plugin_name}")

        except Exception as e:
            print(f"加载插件{plugin_dir}失败: {e}")

    def get_plugin_resource(self, plugin_name, resource_path):
        """获取插件资源文件路径"""
        if plugin_name in self.plugin_dirs:
            return str(self.plugin_dirs[plugin_name] / "resources" / resource_path)
        return None