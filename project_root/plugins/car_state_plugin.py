import numpy as np
from data_classes.car_state_class import CarStateInfo
from functools import partial
from interfaces.PluginBase import PluginBase

class CarStatePlugin(PluginBase): 
               
    def __init__(self, file_path):
        super().__init__(file_path)
        self.CarStateInfo = CarStateInfo(file_path)        
        self.signals = {
            "current_steering": partial(self.CarStateInfo.get_current_steering_angle),
            "current_speed": partial(self.CarStateInfo.get_speed_at_timestamp),
            "driving_mode": partial(self.CarStateInfo.get_driving_mode_at_timestamp),
            "target_speed": partial(self.CarStateInfo.get_target_speed_at_timestamp),
            "target_steering_angle": partial(self.CarStateInfo.get_target_steering_angle_at_timestamp)
        }        
        
    def has_signal(self, signal_name):
        """Check if this plugin provides the requested signal."""
        return signal_name in self.signals
    
    def get_data_for_timestamp(self, signal_name, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal_name in self.signals:
            signal_data = self.signals[signal_name]
            # Call the partial function with the timestamp
            timestamp_in_sec = timestamp/1000
            return signal_data(timestamp_in_sec)
        else:
            return None
            print(f"Error: Signal {signal_name} not found in CarStatePlugin")        

#Explicitly define which class is the plugin
plugin_class = CarStatePlugin


