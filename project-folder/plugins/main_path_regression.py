#main_path_regression.py: MainPathRegression
from plugins.plugin_registry import PluginRegistry
from path_regression.slider import TimestampSlider
from PySide6.QtWidgets import QWidget


class MainPathRegression(QWidget):
    def __init__(self, slider_docker):
        super().__init__()
        # Initialize the plugin registry and backbone data
        self.plugin_registry = PluginRegistry()
        self.backbone_data = {}
        self.slider_docker = slider_docker
        self.timestamp_slider = None    
        # self.parent_widget = QWidget()  # Create a QWidget instance to use as the parent


    def load_plugins(self, plugins):
        """Register user plugins."""
        for plugin in plugins:
            self.plugin_registry.register_plugin(plugin)

    def load_plugins_data(self, trip_path):
        """Pass the trip path to each plugin to load its own data."""
        self.plugin_registry.load_trip(trip_path)
        
        # for plugin in self.plugin_registry.plugins:
        #     plugin.load_data(trip_path)

    def run(self, trip_path, plot_widget):
        """Main execution method to load plugins and display data."""
        
        # Load plugins (using the registry's method)
        self.load_plugins_data(trip_path)               
                
        # Get min and max timestamps from the loaded data
        car_pose_plugin = self.plugin_registry.plugins[0]  # Assuming CarPosePlugin is the second registered plugin
        timestamps = car_pose_plugin.timestamps
                       
        # Create the timestamp slider with the loaded timestamps
        self.timestamp_slider = TimestampSlider(timestamps,  self.plugin_registry)

        # Add the timestamp slider to the UI
        self.slider_docker.addWidget(self.timestamp_slider)    
  
        # Display the initial state of plugins
        self.plugin_registry.set_display_all_plugins(plot_widget, self.timestamp_slider.value())
        
        # sync all plugins with the initial timestamp
        self.plugin_registry.sync_all_plugins(self.timestamp_slider.value())

        
         
        