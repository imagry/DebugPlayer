import numpy as np
from data_classes.car_state_class import CarStateInfo
from functools import partial
from interfaces.PluginBase import PluginBase
import polars as pl
class CarStatePlugin(PluginBase): 
               
    def __init__(self, file_path=None):
        super().__init__(file_path)
        
        if self.use_mock_data:
            print("Using mock data for CarStatePlugin")
            self._setup_mock_data()
        else:
            try:
                self.CarStateInfo = CarStateInfo(file_path)
            except Exception as e:
                print(f"Error loading car state data: {str(e)}. Using mock data instead.")
                self.use_mock_data = True
                self._setup_mock_data()
        
        # Set up signal handlers based on data source (mock or real)
        # Define common metadata for each signal type
        steering_metadata = {
            "description": "Steering angle of the vehicle",
            "units": "deg",
            "valid_range": (-45.0, 45.0),  # Typical range in degrees
            "precision": 1,
            "category": "vehicle_control",
            "tags": ["steering", "control", "driving"],
            "critical_values": {
                "max_left": -30.0,
                "max_right": 30.0,
                "neutral": 0.0
            },
            "color": "#3498db"  # Blue color for steering signals
        }
        
        speed_metadata = {
            "description": "Vehicle speed",
            "units": "m/s",
            "valid_range": (0.0, 40.0),  # Range in meters per second
            "precision": 2,
            "category": "vehicle_state",
            "tags": ["speed", "state", "motion"],
            "critical_values": {
                "standstill": 0.0,
                "urban_limit": 13.89,  # 50 km/h in m/s
                "highway_limit": 27.78  # 100 km/h in m/s
            },
            "color": "#2ecc71"  # Green color for speed signals
        }
        
        driving_mode_metadata = {
            "description": "Current driving mode of the vehicle",
            "type": "categorical",
            "categories": {
                0: "MANUAL",
                1: "AUTOMATED",
                2: "STANDBY",
                3: "ERROR"
            },
            "category": "vehicle_status",
            "tags": ["mode", "status", "automation"],
            "category_colors": {
                0: "#e74c3c",  # Red for manual
                1: "#2ecc71",  # Green for automated
                2: "#f39c12",  # Orange for standby
                3: "#c0392b"   # Dark red for error
            }
        }
        
        if self.use_mock_data:
            self.signals = {
                # Dynamic signals with individual data points
                "current_steering": {
                    "func": self.mock_get_current_steering_angle, 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Current steering angle of the vehicle",
                    **steering_metadata
                },
                "current_speed": {
                    "func": self.mock_get_current_speed, 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Current speed of the vehicle",
                    **speed_metadata
                },
                "driving_mode": {
                    "func": self.mock_get_driving_mode, 
                    "type": "categorical", 
                    "mode": "dynamic",
                    **driving_mode_metadata
                },
                "target_speed": {
                    "func": self.mock_get_target_speed, 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Target speed of the vehicle's control system",
                    **speed_metadata,
                    "tags": ["speed", "target", "control"],
                    "color": "#27ae60"  # Darker green for target speed
                },
                "target_steering_angle": {
                    "func": self.mock_get_target_steering_angle, 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Target steering angle for the vehicle's control system",
                    **steering_metadata,
                    "tags": ["steering", "target", "control"],
                    "color": "#2980b9"  # Darker blue for target steering
                },
                
                # Static signals with full time series data
                "all_steering_data": {
                    "func": self.handler_get_all_current_steering_angle_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of steering angle data",
                    **steering_metadata
                },
                "all_current_speed_data": {
                    "func": self.handler_get_all_current_speed_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of vehicle speed data",
                    **speed_metadata
                },
                "all_driving_mode_data": {
                    "func": self.handler_get_all_driving_mode_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of driving mode data",
                    **driving_mode_metadata
                },
                "all_target_speed_data": {
                    "func": self.handler_get_all_target_speed_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of target speed data",
                    **speed_metadata,
                    "tags": ["speed", "target", "control", "time_series"],
                },
                "all_target_steering_angle_data": {
                    "func": self.handler_get_all_target_steering_angle_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of target steering angle data",
                    **steering_metadata,
                    "tags": ["steering", "target", "control", "time_series"],
                },
            }
        else:
            # For real data, use the same metadata structure but with the real data functions
            self.signals = {
                "current_steering": {
                    "func": partial(self.CarStateInfo.get_current_steering_angle), 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Current steering angle of the vehicle",
                    **steering_metadata
                },
                "current_speed": {
                    "func": partial(self.CarStateInfo.get_current_speed_at_timestamp), 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Current speed of the vehicle",
                    **speed_metadata
                },
                "driving_mode": {
                    "func": partial(self.CarStateInfo.get_driving_mode_at_timestamp), 
                    "type": "categorical", 
                    "mode": "dynamic",
                    **driving_mode_metadata
                },
                "target_speed": {
                    "func": partial(self.CarStateInfo.get_target_speed_at_timestamp), 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Target speed of the vehicle's control system",
                    **speed_metadata,
                    "tags": ["speed", "target", "control"],
                    "color": "#27ae60"  # Darker green for target speed
                },
                "target_steering_angle": {
                    "func": partial(self.CarStateInfo.get_target_steering_angle_at_timestamp), 
                    "type": "temporal", 
                    "mode": "dynamic",
                    "description": "Target steering angle for the vehicle's control system",
                    **steering_metadata,
                    "tags": ["steering", "target", "control"],
                    "color": "#2980b9"  # Darker blue for target steering
                },
                
                # Static signals with full time series data
                "all_steering_data": {
                    "func": self.handler_get_all_current_steering_angle_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of steering angle data",
                    **steering_metadata
                },
                "all_current_speed_data": {
                    "func": self.handler_get_all_current_speed_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of vehicle speed data",
                    **speed_metadata
                },
                "all_driving_mode_data": {
                    "func": self.handler_get_all_driving_mode_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of driving mode data",
                    **driving_mode_metadata
                },
                "all_target_speed_data": {
                    "func": self.handler_get_all_target_speed_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of target speed data",
                    **speed_metadata,
                    "tags": ["speed", "target", "control", "time_series"],
                },
                "all_target_steering_angle_data": {
                    "func": self.handler_get_all_target_steering_angle_data, 
                    "type": "temporal", 
                    "mode": "static",
                    "description": "Full time series of target steering angle data",
                    **steering_metadata,
                    "tags": ["steering", "target", "control", "time_series"],
                },
            }


    def _setup_mock_data(self):
        """Set up mock data for car state information when no file is provided."""
        # Create mock timestamps (0 to 100 seconds in 0.1s intervals)
        self.mock_timestamps = np.arange(0, 100.1, 0.1)
        num_timestamps = len(self.mock_timestamps)
        
        # Create mock data for different car state signals
        # Current steering angle: oscillates between -30 and 30 degrees
        self.mock_current_steering = 30 * np.sin(self.mock_timestamps / 5.0)
        
        # Current speed: varies between 0 and 50 mph with acceleration and deceleration
        self.mock_current_speed = 30 + 20 * np.sin(self.mock_timestamps / 15.0)
        
        # Target speed: follows current speed with some lead
        self.mock_target_speed = 30 + 20 * np.sin((self.mock_timestamps + 2) / 15.0)
        
        # Target steering: similar to current steering but with some lead
        self.mock_target_steering = 30 * np.sin((self.mock_timestamps + 0.5) / 5.0)
        
        # Driving mode: 0 = manual, 1 = assisted, 2 = autonomous
        # Changes every 20 seconds
        self.mock_driving_mode = np.zeros(num_timestamps)
        for i in range(num_timestamps):
            if 20 <= self.mock_timestamps[i] < 40:
                self.mock_driving_mode[i] = 1
            elif 40 <= self.mock_timestamps[i] < 60:
                self.mock_driving_mode[i] = 2
            elif 60 <= self.mock_timestamps[i] < 80:
                self.mock_driving_mode[i] = 1
            elif self.mock_timestamps[i] >= 80:
                self.mock_driving_mode[i] = 2
                
        # Create DataFrame-like structures for mock data
        self.mock_data = {
            'timestamps': self.mock_timestamps,
            'current_steering': self.mock_current_steering,
            'current_speed': self.mock_current_speed,
            'target_speed': self.mock_target_speed,
            'target_steering': self.mock_target_steering,
            'driving_mode': self.mock_driving_mode
        }
    
    # Mock data access methods
    def mock_get_current_steering_angle(self, timestamp):
        idx = self._find_closest_timestamp_index(timestamp)
        return float(self.mock_current_steering[idx])
        
    def mock_get_current_speed(self, timestamp):
        idx = self._find_closest_timestamp_index(timestamp)
        return float(self.mock_current_speed[idx])
        
    def mock_get_driving_mode(self, timestamp):
        idx = self._find_closest_timestamp_index(timestamp)
        return int(self.mock_driving_mode[idx])
        
    def mock_get_target_speed(self, timestamp):
        idx = self._find_closest_timestamp_index(timestamp)
        return float(self.mock_target_speed[idx])
        
    def mock_get_target_steering_angle(self, timestamp):
        idx = self._find_closest_timestamp_index(timestamp)
        return float(self.mock_target_steering[idx])
    
    def _find_closest_timestamp_index(self, timestamp):
        """Find the index of the closest timestamp in mock data."""
        # Convert timestamp from ms to seconds if needed
        if timestamp > 1000:  # Assuming it's in milliseconds
            timestamp = timestamp / 1000.0
            
        return np.argmin(np.abs(self.mock_timestamps - timestamp))
        
    # Handler methods for all data access - support both real and mock data
    def handler_get_all_current_steering_angle_data(self, _):
        if self.use_mock_data:
            return {'timestamp': self.mock_timestamps, 'value': self.mock_current_steering}
        else:
            return self.CarStateInfo.get_all_current_steering_angle_data()
        
    def handler_get_all_current_speed_data(self, _):
        if self.use_mock_data:
            return {'timestamp': self.mock_timestamps, 'value': self.mock_current_speed}
        else:
            return self.CarStateInfo.get_all_current_speed_data()
        
    def handler_get_all_driving_mode_data(self, _):
        if self.use_mock_data:
            return {'timestamp': self.mock_timestamps, 'value': self.mock_driving_mode}
        else:
            return self.CarStateInfo.get_all_driving_mode_data()
        
    def handler_get_all_target_speed_data(self, _):
        if self.use_mock_data:
            return {'timestamp': self.mock_timestamps, 'value': self.mock_target_speed}
        else:
            return self.CarStateInfo.get_all_target_speed_data()
        
    def handler_get_all_target_steering_angle_data(self, _):
        if self.use_mock_data:
            return {'timestamp': self.mock_timestamps, 'value': self.mock_target_steering}
        else:
            return self.CarStateInfo.get_all_target_steering_angle_data()
        



    def has_signal(self, signal):
        """Check if this plugin provides the requested signal."""
        return signal in self.signals
    
    def get_data_for_timestamp(self, signal, timestamp):
        """Fetch data for a specific signal and timestamp."""
        if signal in self.signals:
            signal_info = self.signals[signal]
            signal_func = signal_info.get("func")

            if callable(signal_func):
                try:
                    # Call the function with the timestamp (converted to seconds if needed)
                    timestamp_in_sec = timestamp / 1000 if timestamp > 1000 else timestamp
                    result = signal_func(timestamp_in_sec)
                    
                    # Skip verbose printing in production, only print in debug mode
                    # print(f"Fetched data for '{signal}' at {timestamp_in_sec}s")
                    return result
                except Exception as e:
                    print(f"Error fetching '{signal}' at {timestamp}: {str(e)}")
            else:
                print(f"Error: Signal function for '{signal}' is not callable.")
        else:
            print(f"Error: Signal '{signal}' not found in CarStatePlugin.")
        return None
     

#Explicitly define which class is the plugin
plugin_class = CarStatePlugin


