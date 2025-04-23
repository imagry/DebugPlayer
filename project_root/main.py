from PySide6.QtWidgets import QApplication
from gui.main_window import create_main_window
from core.data_loader import parse_arguments
from core.plot_manager import PlotManager
from core.signal_registry import SignalRegistry
from core.view_manager import ViewManager
import os
import sys

def main():
    # Initialize QApplication
    app = QApplication([])
    
    # Initialize the PlotManager (which creates its own SignalRegistry internally)
    plot_manager = PlotManager()
    
    # Get the SignalRegistry from the PlotManager
    signal_registry = plot_manager.signal_registry
    
    # Initialize the ViewManager (which doesn't take a PlotManager parameter)
    view_manager = ViewManager()
    
    # Load plugins dynamically from the 'plugins/' directory
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    
    # Pass file path arguments as needed to the plugins
    trip_path = parse_arguments()
    if not trip_path:
        print("No trip path provided. Using demo data.")
        # If we're in development/testing mode, we can use demo data
        # This will be replaced with actual data loading in production
    
    plugin_args = {"file_path": trip_path}
    plot_manager.load_plugins_from_directory(plugin_dir, plugin_args=plugin_args)
    
    # Import view classes directly
    from views.temporal_view import TemporalView
    from views.spatial_view import SpatialView
    
    # Register view classes with the view manager
    view_manager.register_view_class("temporal_view", TemporalView)
    view_manager.register_view_class("spatial_view", SpatialView)
    
    # Create view templates
    view_manager.register_template("temporal_default", {
        "type": "temporal_view",
        "config": {"time_window": 10.0},
        "signals": []  # Will be populated later
    })
    
    view_manager.register_template("spatial_default", {
        "type": "spatial_view",
        "config": {"show_grid": True, "show_axes": True},
        "signals": []  # Will be populated later
    })
    
    # Create the main window (ViewManager is created inside create_main_window)
    win, plot_manager, view_manager = create_main_window(plot_manager=plot_manager)
    win.show()
    
    # Request initial data for timestamp 0
    try:
        # Try to get timestamps from a plugin
        timestamps = []
        for plugin_name, plugin in plot_manager.plugins.items():
            if hasattr(plugin, 'get_timestamps') and callable(plugin.get_timestamps):
                try:
                    timestamps = plugin.get_timestamps()
                    if timestamps and len(timestamps) > 0:
                        break
                except Exception as e:
                    print(f"Error getting timestamps from {plugin_name}: {str(e)}")
        
        # Fallback to legacy method
        if not timestamps and "CarPosePlugin" in plot_manager.plugins:
            if "timestamps" in plot_manager.plugins["CarPosePlugin"].signals:
                timestamps_func = plot_manager.plugins["CarPosePlugin"].signals["timestamps"].get("func")
                if timestamps_func and callable(timestamps_func):
                    timestamps = timestamps_func()
        
        if timestamps and len(timestamps) > 0:
            initial_timestamp = timestamps[0]
            plot_manager.request_data(initial_timestamp)
            print(f"Initialized with timestamp: {initial_timestamp}")
        else:
            print("No timestamps available. Using default timestamp 0.0")
            plot_manager.request_data(0.0)
    except Exception as e:
        print(f"Error initializing with timestamp: {str(e)}")
        print("Using default timestamp 0.0")
        plot_manager.request_data(0.0)
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
