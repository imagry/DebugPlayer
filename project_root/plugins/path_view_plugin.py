import numpy as np
from data_classes.PathTrajectory_pandas import PathTrajectoryPandas
from data_classes.PathTrajectory_polars import PathTrajectoryPolars
from interfaces.PluginBase import PluginBase

class PathViewPlugin(PluginBase):
    def __init__(self, file_path=None, path_type='path_trajectory.csv', path_loader_type='polars'):
        super().__init__(file_path)
        """
        Initialize the PathViewPlugin with the appropriate PathTrajectory object.

        Parameters:
        file_path (str, optional): The path to the data file. If None, mock data will be used.
        path_type (str): The type of path data file.
        path_loader_type (str): The data loader type ('pandas' or 'polars').
        """
        self.path_type = path_loader_type
        self.use_mock_data = (file_path is None)
        
        if self.use_mock_data:
            print("Using mock data for PathViewPlugin")
            # Set up mock data instead of loading from file
            self._setup_mock_data()
        else:
            # Load data from file
            try:
                if path_loader_type == 'pandas':
                    self.path_trajectory = PathTrajectoryPandas(file_path + path_type)
                elif path_loader_type == 'polars':
                    self.path_trajectory = PathTrajectoryPolars(file_path + path_type)
                else:
                    raise ValueError("Invalid path_type. Must be 'pandas' or 'polars'.")
            except Exception as e:
                print(f"Error loading path data: {str(e)}. Using mock data instead.")
                self.use_mock_data = True
                self._setup_mock_data()
        
        # Define the signals provided by this plugin
        self.signals = {
            "path_in_world_coordinates(t)": {"func": self.get_path_world_at_timestamp, "type": "spatial"},
            "car_pose_at_path_timestamp(t)": {"func": self.get_car_pose_at_timestamp, "type": "spatial"},
            "timestamps": {"func": self.get_timestamps, "type": "temporal"}
        }
        

    def _setup_mock_data(self):
        """
        Set up mock data for the plugin when no file is provided.
        """
        # Create a mock timestamps array (0 to 100 seconds in 0.1s intervals)
        self.mock_timestamps = np.arange(0, 100.1, 0.1)
        
        # Generator functions for mock path data
        def create_mock_path(t):
            # Create a circular path that changes with time
            radius = 50 + 10 * np.sin(t / 5.0)  # Radius varies between 40 and 60
            num_points = 100
            angles = np.linspace(0, 2 * np.pi, num_points)
            x = radius * np.cos(angles)
            y = radius * np.sin(angles)
            return np.column_stack((x, y))
        
        def create_mock_pose(t):
            # Car position changes with time around the path
            angle = (t / 10.0) % (2 * np.pi)
            radius = 50 + 5 * np.sin(t / 5.0)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            # Car heading points tangential to the circle
            heading = angle + np.pi/2
            return np.array([x, y, heading])
            
        self.create_mock_path = create_mock_path
        self.create_mock_pose = create_mock_pose
        
    def get_timestamps(self):
        """
        Get all available timestamps.
        
        Returns:
            Array of timestamps.
        """
        if self.use_mock_data:
            return self.mock_timestamps
        else:
            return self.path_trajectory.get_timestamps_ms()
    
    def get_path_in_world_coordinates_at_timestamp(self, timestamp):
        """
        Get the path in world coordinates for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to fetch the path for.

        Returns:
        dict: A dictionary containing the path and car pose in world coordinates.
        """
        if self.use_mock_data:
            # Generate mock path and car pose based on timestamp
            path_world = self.create_mock_path(timestamp)
            car_pose = self.create_mock_pose(timestamp)
        else:
            # Use real data from the path trajectory
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