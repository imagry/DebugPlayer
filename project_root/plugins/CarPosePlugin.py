import numpy as np
from data_classes.car_pose_class import CarPose
from functools import partial
from interfaces.PluginBase import PluginBase

class CarPosePlugin(PluginBase): 
               
    def __init__(self, file_path=None):
        super().__init__(file_path)
        
        if self.use_mock_data:
            print("Using mock data for CarPosePlugin")
            self._setup_mock_data()
        else:
            # Load real data from file
            try:
                self.car_pose = CarPose(file_path)
                self.car_poses = {"x": self.car_pose.route['cp_x'], "y": self.car_pose.route['cp_y'], "theta": self.car_pose.df_car_pose['cp_yaw_deg']}
                self.timestamps = self.car_pose.get_timestamps_milliseconds()
            except Exception as e:
                print(f"Error loading car pose data: {str(e)}. Using mock data instead.")
                self.use_mock_data = True
                self._setup_mock_data()
        
        # Define the signals provided by this plugin
        self.signals = {
            "car_pose(t)": {"func": self.handle_car_pose_at_timestamp, "type": "spatial"},
            "route": {"func": self.route_handler, "type": "spatial"},
            "timestamps": {"func": lambda: self.timestamps, "type": "temporal"},
            "car_poses": {"func": lambda: self.car_poses, "type": "spatial"}
        }
                
    def _setup_mock_data(self):
        """
        Set up mock data for the plugin when no file is provided.
        """
        # Create mock timestamps (0 to 100 seconds in 0.1s intervals)
        self.timestamps = np.arange(0, 100.1, 0.1)
        
        # Create mock route (a circular path)
        num_points = 200
        angles = np.linspace(0, 2 * np.pi, num_points)
        route_x = 100 * np.cos(angles)
        route_y = 100 * np.sin(angles)
        self.mock_route = np.column_stack((route_x, route_y))
        
        # Create mock car poses along the route
        num_poses = len(self.timestamps)
        pose_x = np.zeros(num_poses)
        pose_y = np.zeros(num_poses)
        pose_theta = np.zeros(num_poses)
        
        for i, t in enumerate(self.timestamps):
            # Car moves along the route based on time
            angle = (t / 10.0) % (2 * np.pi)
            radius = 100 - 5 * np.sin(t / 5.0)  # Slight variation in radius
            pose_x[i] = radius * np.cos(angle)
            pose_y[i] = radius * np.sin(angle)
            # Car points tangent to the circle
            pose_theta[i] = (angle + np.pi/2) * 180 / np.pi  # Convert to degrees
        
        # Store mock car poses for reference
        self.car_poses = {"x": pose_x, "y": pose_y, "theta": pose_theta}
    
    def route_handler(self):
        if self.use_mock_data:
            return {"x": self.mock_route[:, 0], "y": self.mock_route[:, 1]}
        else:
            route_ = self.car_pose.get_route()
            return {"x": route_[:, 0], "y": route_[:, 1]}
    
    def handle_car_pose_at_timestamp(self, timestamp):
        if self.use_mock_data:
            # Find the closest timestamp in our mock data
            closest_idx = np.argmin(np.abs(self.timestamps - timestamp))
            return {
                "x": float(self.car_poses["x"][closest_idx]),
                "y": float(self.car_poses["y"][closest_idx]),
                "theta": float(self.car_poses["theta"][closest_idx])
            }
        else:
            result = self.car_pose.get_car_pose_at_timestamp(timestamp)
            return {"x": result[0], "y": result[1], "theta": result[2]}
    
    def has_signal(self, signal):
        """Check if this plugin provides the requested signal."""
        return signal in self.signals
    
    def get_data_for_timestamp(self, signal, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal in self.signals:
            signal_info = self.signals[signal]
            signal_func = signal_info.get("func")
        
            if callable(signal_func):
                # Call the function with the timestamp if the signal is temporal
                if signal == "car_pose(t)":
                    return signal_func(timestamp)
                else:
                    # For signals like "timestamps", directly call without arguments
                    return signal_func()
            else:
                print(f"Error: Signal function for '{signal}' is not callable.")
        else:
            print(f"Error: Signal '{signal}' not found in CarPosePlugin.")
        return None

#Explicitly define which class is the plugin
plugin_class = CarPosePlugin


