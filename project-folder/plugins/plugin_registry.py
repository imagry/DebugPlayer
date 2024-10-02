# plugin_registry.py
from plugins.plugin_api_interfaces import UserPluginInterface

class PluginRegistry:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        """Register a user plugin."""
        self.plugins.append(plugin)

    def sync_all_plugins(self, timestamp, data):
        """Sync all registered plugins' data with the given timestamp."""
        for plugin in self.plugins:
            plugin.sync_data_with_timestamp(timestamp, data)

    def display_all_plugins(self, plot_widget):
        """Display all registered plugins' data in the GUI."""
        for plugin in self.plugins:
            plugin.display(plot_widget)

