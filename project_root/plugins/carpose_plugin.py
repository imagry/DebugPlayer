import numpy as np
from data_classes.car_pose_class import CarPose
from functools import partial

class CarPosePlugin:        
    def __init__(self, file_path):
        self.file_path = file_path
        self.car_pose = CarPose(file_path)
        self.car_poses = {"x": self.car_pose.route['cp_x'], "y": self.car_pose.route['cp_y'], "theta": self.car_pose.df_car_pose['cp_yaw_deg']}
        self.car_pose_at_timestamp = lambda t: self.handle_car_pose_at_timestamp(t)
        route = self.car_pose.get_route() 
        self.signals = {
            "car_pose(t)": self.car_pose_at_timestamp,
            "route": {"x": route[:, 0], "y": route[:, 1]},
            "timestamps": self.car_pose.get_timestamps_milliseconds(),
            "car_poses": self.car_poses
        }
        self.timestamps = self.car_pose.get_timestamps_milliseconds() # Example timestamps                
        # TODO: Load real car pose data from a file
    
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
            elif signal_name == "route":
                return signal_data
            elif signal_name == "timestamps":
                return signal_data
            elif signal_name == "car_poses":
                return signal_data
        # TODO: can we squash all last three into return signal_data?





