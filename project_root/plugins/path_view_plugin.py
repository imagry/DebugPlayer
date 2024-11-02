import numpy as np
from data_classes.PathTrajectory_pandas import PathTrajectoryPandas
from data_classes.PathTrajectory_polars import PathTrajectoryPolars
from interfaces.PluginBase import PluginBase

class PathViewPlugin(PluginBase):
    def __init__(self, file_path, path_type = 'path_trajectory.csv', path_loader_type='polars'):
        super().__init__(file_path)
        """
        Initialize the PathViewPlugin with the appropriate PathTrajectory object.

        Parameters:
        file_path (str): The path to the data file.
        path_type (str): The type of path data ('pandas' or 'polars').
        """
        self.path_type = path_loader_type

        if path_loader_type == 'pandas':
            self.path_trajectory = PathTrajectoryPandas(file_path + path_type)
        elif path_loader_type == 'polars':
            self.path_trajectory = PathTrajectoryPolars(file_path + path_type)
        else:
            raise ValueError("Invalid path_type. Must be 'pandas' or 'polars'.")

        self.signals = {
            "path_in_world_coordinates(t)": {"func": self.get_path_world_at_timestamp, "type": "spatial"},
            "car_pose_at_path_timestamp(t)": {"func": self.get_car_pose_at_timestamp, "type": "spatial"},
            "timestamps": {"func": lambda: self.path_trajectory.get_timestamps_ms(), "type": "temporal"}
        }
        

    def get_path_in_world_coordinates_at_timestamp(self, timestamp):
        """
        Get the path in world coordinates for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to fetch the path for.

        Returns:
        dict: A dictionary containing the path and car pose in world coordinates.
        """
        path_world, car_pose = self.path_trajectory.get_path_in_world_coordinates(timestamp)
        return {
            "path_world": path_world,
            "car_pose": car_pose
        }

    def get_path_world_at_timestamp(self, timestamp):
        results = self.get_path_in_world_coordinates_at_timestamp(timestamp)
        return results["path_world"]

    def get_car_pose_at_timestamp(self, timestamp):
        results = self.get_path_in_world_coordinates_at_timestamp(timestamp)
        return results["car_pose"]
    
    def has_signal(self, signal):
        """
        Check if this plugin provides the requested signal.

        Parameters:
        signal (str): The name of the signal.

        Returns:
        bool: True if the signal is provided, False otherwise.
        """
        return signal in self.signals

    def get_data_for_timestamp(self, signal, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal in self.signals:
            signal_info = self.signals[signal]
            signal_func = signal_info.get("func")
            
            if callable(signal_func):       
                # Call the function with the timestamp if required        
                if signal in ["path_in_world_coordinates(t)", "car_pose_at_path_timestamp(t)"]:
                    return signal_func(timestamp)
                else:
                    # Directly call the lambda to retrieve data
                    return signal_func()
            else:
                raise ValueError(f"Signal function for '{signal}' is not callable.")
        else:
            raise ValueError(f"Signal '{signal}' not found.")
#Explicitly define which class is the plugin
plugin_class = PathViewPlugin        