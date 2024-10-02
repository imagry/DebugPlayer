# path_view_plugin.py
import pandas as pd
from plugins.plugin_api_interfaces import UserPluginInterface
from utils.data_loaders.path_handler_loader import prepare_path_data
from data_classes.PathTrajectory_pandas import PathTrajectory
class PathViewPlugin(UserPluginInterface):
    def __init__(self):
        self.trip_path = None  # Placeholder for the path to the trip data
        self.data = None  # Placeholder for the loaded CSV data
        self.current_paths = None  # Current paths at the selected timestamp
        self.path_obj = None  # Placeholder for the path object
        self.current_time_stamp = None  # Placeholder for the current timestamp

    def load_data(self, trip_path):
        """Load the CSV data."""
        self.trip_path = trip_path
        try:
            # Ensure the data is sorted by timestamp
            self.path_obj = prepare_path_data(trip_path , interpolation=False) 
            print(f"Loaded data from {trip_path}")
        except Exception as e:
            print(f"Failed to load from path file: {e}")  
            
    def get_data_with_timestamp(self, timestamp):
        """retrieve, store, and return the paths for the given timestamp."""
        if self.path_obj is not None:
            # Filter the data for the current timestamp            
            path_w = self.path_obj.get_path_in_world_coordinates(timestamp)   
            self.current_paths = path_w
            self.current_time_stamp = timestamp
            return path_w
        else:
            print("Data has not been loaded.")      


    # ToDo: allow returning data to plot such that plotting is handled from somewhere else, or allow inhertiing from a base class that handles plotting            
    def display(self, plot_widget, timestamp, plot_opts_dict):
        """Display the paths on the plot widget."""
        if self.current_paths is not None and not self.current_paths.empty:
            if timestamp == self.current_time_stamp:
                path_w = self.current_paths
            else:
                path_w = self.get_data_with_timestamp(timestamp)                          
            # Clear the plot and replot the current paths            
            plot_widget.plot(path_w['x'], path_w['y'], pen=None, symbol='o', symbolSize=5, symbolBrush='b')
        else:
            print("No paths available for the current timestamp.")
            
