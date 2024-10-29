import numpy as np
from data_classes.car_state_class import CarStateInfo
from functools import partial
from interfaces.PluginBase import PluginBase

class CarStatePlugin(PluginBase): 
               
    def __init__(self, file_path):
        super().__init__(file_path)
        self.CarStateInfo = CarStateInfo(file_path)        
        self.signals = {
            "current_steering": {"func": partial(self.CarStateInfo.get_current_steering_angle), "type": "temporal", "mode": "dynamic"},
            "current_speed": {"func": partial(self.CarStateInfo.get_current_speed_at_timestamp), "type": "temporal","mode": "dynamic"},
            "driving_mode": {"func": partial(self.CarStateInfo.get_driving_mode_at_timestamp), "type": "temporal","mode": "dynamic"},
            "target_speed": {"func": partial(self.CarStateInfo.get_target_speed_at_timestamp), "type": "temporal","mode": "dynamic"},
            "target_steering_angle": {"func": partial(self.CarStateInfo.get_target_steering_angle_at_timestamp), "type": "temporal","mode": "dynamic"},
            "all_steering_data": {"func": self.handler_get_all_current_steering_angle_data, "type": "temporal", "mode": "static"},
            "all_current_speed_data": {"func": self.handler_get_all_current_speed_data, "type": "temporal", "mode": "static"},
            "all_driving_mode_data": {"func": self.handler_get_all_driving_mode_data, "type": "temporal", "mode": "static"},
            "all_target_speed_data": {"func": self.handler_get_all_target_speed_data, "type": "temporal", "mode": "static"},
            "all_target_steering_angle_data": {"func": self.handler_get_all_target_steering_angle_data, "type": "temporal", "mode": "static"},            
        }


    def handler_get_all_current_steering_angle_data(self, _ ):
        return self.CarStateInfo.get_all_current_steering_angle_data()
        
    def handler_get_all_current_speed_data(self, _):
        return self.CarStateInfo.get_all_current_speed_data()
        
    def handler_get_all_driving_mode_data(self, _):
        return self.CarStateInfo.get_all_driving_mode_data()
        
    def handler_get_all_target_speed_data(self, _):
        return self.CarStateInfo.get_all_target_speed_data()
        
    def handler_get_all_target_steering_angle_data(self, _):
        return self.CarStateInfo.get_all_target_steering_angle_data()
        



    def has_signal(self, signal_name):
        """Check if this plugin provides the requested signal."""
        return signal_name in self.signals
    
    def get_data_for_timestamp(self, signal_name, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal_name in self.signals:
            signal_info = self.signals[signal_name]
            signal_func = signal_info.get("func")

            if callable(signal_func):
                # Call the partial function with the timestamp (converted to seconds)
                timestamp_in_sec = timestamp / 1000
                result = signal_func(timestamp_in_sec)
                print(f"Fetched data for '{signal_name}' at {timestamp_in_sec}s: {result}")
                return result
            else:
                print(f"Error: Signal function for '{signal_name}' is not callable.")
        else:
            print(f"Error: Signal '{signal_name}' not found in CarStatePlugin.")
        return None
     

#Explicitly define which class is the plugin
plugin_class = CarStatePlugin


