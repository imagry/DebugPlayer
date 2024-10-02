#main_class.py
from plugins.plugin_registry import PluginRegistry
from path_regression.slider import TimestampSlider


class MainPathRegression:
    def __init__(self):
        # Initialize the plugin registry and backbone data
        self.plugin_registry = PluginRegistry()
        self.backbone_data = {}

        # Initialize the slider with a dummy range, min_time and max_time can be adjusted
        self.timestamp_slider = TimestampSlider(min_time=0, max_time=1000)  
        # Connect the slider's sync mechanism to the sync function in the backbone
        self.timestamp_slider.sync_data = self.sync_plugins_with_timestamp


    def load_plugins(self, plugins):
        """Register user plugins."""
        for plugin in plugins:
            self.plugin_registry.register_plugin(plugin)

    def load_trip(self, trip_path):
        """Pass the trip path to each plugin to load its own data."""
        for plugin in self.plugin_registry.plugins:
            plugin.load_data

                       
    def sync_plugins_with_timestamp(self, timestamp):
        """Sync all plugins with the current timestamp."""
        # self.plugin_registry.sync_all_plugins(self.backbone_data)
        pass

    def run(self, trip_path, plot_widget):
        """Main execution method to load plugins and display data."""
        # Load plugins (using the registry's method)
        self.load_trip(trip_path)

        # Sync and display plugins for the initial timestamp
        self.sync_plugins_with_timestamp(0)
        #  self.plugin_registry.display_all_plugins(plot_widget)
        
        