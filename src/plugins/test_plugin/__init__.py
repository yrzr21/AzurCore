from plugins.test_plugin.test_plugin_widget import TestPluginWidget


class Plugin:
    def get_widget(self):
        return TestPluginWidget()
