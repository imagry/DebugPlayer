# plugin_registry.py
from plugins.plugin_api_interfaces import UserPluginInterface

class PluginRegistry:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        """Register a user plugin."""
        self.plugins.append(plugin)

    def set_display_all_plugins(self, plot_widget, timestamp, disp_opt_dict=None):
        """Display all registered plugins' data in the GUI."""
        for plugin in self.plugins:
            plugin.set_display(plot_widget, timestamp)
            
    def sync_all_plugins(self, timestamp):
        """Sync all registered plugins with the given timestamp."""
        for plugin in self.plugins:
            plugin.sync_data_with_timestamp(timestamp)
            
    def load_trip(self, trip_path):
        """Load the trip data for all plugins."""
        for plugin in self.plugins:
            plugin.load_data(trip_path)
            
    def get_plugin(self, plugin_name):
        """Get a plugin by name."""
        for plugin in self.plugins:
            if plugin.__class__.__name__ == plugin_name:
                return plugin
        return None     
    
    
    

