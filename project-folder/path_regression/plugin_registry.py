# plugin_registry.py
from api_interfaces import UserPluginInterface

class PluginRegistry:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin: UserPluginInterface):
        self.plugins.append(plugin)

    def load_all_plugins(self, file_paths: dict):
        """Load data for all registered plugins."""
        for plugin, file_path in zip(self.plugins, file_paths.values()):
            plugin.load_data(file_path)

    def display_all_plugins(self, display_options: dict):
        """Display all registered plugins' data in the GUI."""
        for plugin, options in zip(self.plugins, display_options.values()):
            plugin.display_data(options)

    def sync_all_plugins(self, backbone_data: dict):
        """Sync all registered plugins' data with the backbone."""
        for plugin in self.plugins:
            plugin.sync_data(backbone_data)
