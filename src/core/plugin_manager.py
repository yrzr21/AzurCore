import importlib
from pathlib import Path
from core.utils.config_manager import config
from core.utils.logger import logger


# todo：plugin 互相依赖


class PluginManager:
    def __init__(self):
        self.plugin_root_dir = config["plugins"]["directory"]
        self.enabled_plugins = config["plugins"]["enabled"]

        self.plugins = {}

    def items(self):
        return self.plugins.items()

    def load_plugins(self):
        """遍历所有非_开头的文件夹，作为插件加载"""
        iterdir = Path(self.plugin_root_dir).iterdir()
        for plugin_dir in iterdir:
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                self._load_plugin(plugin_dir)

    def _load_plugin(self, plugin_dir: Path):
        plugin_name = plugin_dir.name
        if plugin_name not in self.enabled_plugins:
            logger.info(f"跳过禁用插件: {plugin_name}")
            return

        entry_file = plugin_dir / "__init__.py"
        if not entry_file.exists():
            logger.error(f"在 {plugin_dir} 中找不到插件入口文件")
            return

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(plugin_name, entry_file)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            import traceback
            logger.error(f"加载插件 {plugin_dir} 失败: {e}\n{traceback.print_exc()}")
            return

        if not hasattr(module, "Plugin"):
            logger.error(f"在 {plugin_name} 中找不到属性 Plugin")
            return

        # 实例化并存储插件
        plugin_instance = getattr(module, "Plugin")()
        self.plugins[plugin_name] = plugin_instance

        logger.info(f"成功加载插件: {plugin_name}")


plugins = PluginManager()
