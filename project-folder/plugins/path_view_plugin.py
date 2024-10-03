# path_view_plugin.py
import pandas as pd
from plugins.plugin_api_interfaces import UserPluginInterface
from utils.data_loaders.path_handler_loader import prepare_path_data
from data_classes.PathTrajectory_pandas import PathTrajectory
class PathViewPlugin(UserPluginInterface):
    def __init__(self):
        self.trip_path = None  # Placeholder for the path to the trip data
        self.data = None  # Placeholder for the loaded CSV data
        self.current_path = None  # Current paths at the selected timestamp
        self.path_obj = None  # Placeholder for the path object
        self.current_time_stamp = None  # Placeholder for the current timestamp
        self.timestamps = None  # Placeholder for the timestamps
        self.plot_widget = None  # Store plot widget reference

    def load_data(self, trip_path):
        """Load the CSV data."""
        self.trip_path = trip_path
        try:
            # Ensure the data is sorted by timestamp
            self.path_obj = prepare_path_data(trip_path , interpolation=False) 
            
            # Check if the DataFrame index is already in Unix timestamp format
            timestamp_s = pd.to_datetime(self.path_obj.get_timestamps(), unit='s')
            if self.path_obj.get_timestamps().dtype != 'int64':
                self.timestamps = timestamp_s.view('int64') // 10**6 
            else:
                self.timestamps = self.path_obj.timestamps
                
            print(f"Loaded data from {trip_path}")
        except Exception as e:
            print(f"Failed to load from path file: {e}")  

    def sync_data_with_timestamp(self, timestamp):
        """retrieve, store, and return the paths for the given timestamp."""
        if self.path_obj is not None:
            # Filter the data for the current timestamp            
            cur_path, carpose_path = self.path_obj.get_path_in_world_coordinates(timestamp)
            self.current_path = cur_path
            self.current_time_stamp = timestamp
        else:
            print("Data has not been loaded.")    
            return
        
        # If we have a plot widget, update the plot with the new position
        if self.plot_widget is not None:
            self.update_plot()


    # ToDo: allow returning data to plot such that plotting is handled from somewhere else, or allow inhertiing from a base class that handles plotting            
    def set_display(self, plot_widget, timestamp, plot_opts_dict=None):
        """Store plot widget and set path display handle."""
        self.plot_widget = plot_widget  # Store the plot widget reference
        
        
        # Clear the plot and replot the current paths
        if plot_opts_dict is not None:
            self.plot_opts_dict = plot_opts_dict
            # define a lmabda function for the plot as fucntion of x and y path data
            self.plot_handle = lambda x, y: self.plot_widget.plot(x, y, pen=plot_opts_dict.get('pen', None), symbol=plot_opts_dict.get('symbol', 'o'), symbolSize=plot_opts_dict.get('symbolSize', 5), symbolBrush=plot_opts_dict.get('symbolBrush', 'b'))
        else:
            self.plot_handle = lambda x, y: self.plot_widget.plot(x, y, pen=None, symbol='o', symbolSize=5, symbolBrush='b')
            
    def update_plot(self):
        """Update the path at current slider timestamp."""
        if self.current_path is not None:
            path = self.current_path
            if path.shape[0] == 2:
                path = path.T
            x_data = path[0]
            y_data = path[1]
                
            self.plot_handle(x_data, y_data)
        else:
            print("No path data to plot.")   
                