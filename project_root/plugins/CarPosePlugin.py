import numpy as np
from data_classes.car_pose_class import CarPose
from functools import partial
from interfaces.PluginBase import PluginBase

class CarPosePlugin(PluginBase): 
               
    def __init__(self, file_path):
        super().__init__(file_path)
        self.car_pose = CarPose(file_path)
        self.car_poses = {"x": self.car_pose.route['cp_x'], "y": self.car_pose.route['cp_y'], "theta": self.car_pose.df_car_pose['cp_yaw_deg']}
        self.timestamps = self.car_pose.get_timestamps_milliseconds() # Example timestamps                
        # self.car_pose_at_timestamp = lambda t: self.handle_car_pose_at_timestamp(t)
        # route = self.car_pose.get_route() 
        self.signals = {
            "car_pose(t)": self.handle_car_pose_at_timestamp,
            "route": self.route_handler,
            "timestamps":lambda: self.timestamps,
            "car_poses": lambda: self.car_poses
        }
        # TODO: Load real car pose data from a file   
        
    def route_handler(self):
        route_ = self.car_pose.get_route()
        return {"x": route_[:, 0], "y": route_[:, 1]}
    
    def handle_car_pose_at_timestamp(self, timestamp):
        result = self.car_pose.get_car_pose_at_timestamp(timestamp)
        return {"x": result[0], "y": result[1], "theta": result[2]} 
    
    def has_signal(self, signal_name):
        """Check if this plugin provides the requested signal."""
        return signal_name in self.signals
    
    def get_data_for_timestamp(self, signal_name, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal_name in self.signals:
            signal_data = self.signals[signal_name]
            # For the route signal, return the entire path            
            if signal_name == "car_pose(t)":
                return signal_data(timestamp)
            else:
                # Directly call the lambda to retrieve data
                return signal_data()
        else:
            print(f"Error: Signal '{signal_name}' not found in CarPosePlugin.")

#Explicitly define which class is the plugin
plugin_class = CarPosePlugin


