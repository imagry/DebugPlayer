from scipy.interpolate import interp1d
import pandas as pd
from utils.data_loaders.vehicle_states_multi_file_reader import read_vehicle_state_logs


class CarStateInfo:
    ''' This class is used to handle the car pose data. The class initializes with the car pose data.
    
        Methods:
        - get_car_pose_at_timestamp(timestamp): Get the car pose at the given timestamp.
        - get_closest_car_pose(timestamp): Get the car pose closest to the given timestamp.
        - get_trajectory(): Get the car pose trajectory.
        - get_timestamps(): Get the timestamps.
        - set_interpolation(): Prepare the interpolation objects for x,y, and the yaw.
    '''
    def __init__(self, trip_path, interpolation = True): 
        self.trip_path = trip_path
        car_info = read_vehicle_state_logs(trip_path)
        df_cruise_control, df_driving_mode, df_speed, df_steering = car_info
        
        if df_cruise_control is not None:
            self.df_cruise_control = df_cruise_control
            
        if df_driving_mode is not None:
            self.df_driving_mode = df_driving_mode
            
        if df_speed is not None:
            self.df_speed = df_speed
            
        if df_steering is not None:
            self.df_steering = df_steering                    

    def get_speed_at_timestamp(self, timestamp):
        ''' Get the speed at the given timestamp.
        
            Args:
            timestamp (int): The timestamp.
            
            Returns:
            float: The speed at the given timestamp.
        '''
        if self.df_speed is not None:
            closest_idx = (self.df_speed['time_stamp'] - timestamp).abs().arg_min()
            return self.df_speed.select('data_value')[closest_idx]
        else:
            print("Error: speed data not availalbe")
            return None
        
    
    def get_current_steering_angle(self, timestamp):
        ''' Get the current steering angle at the given timestamp.
        
            Args:
            timestamp (int): The timestamp.
            
            Returns:
            float: The steering angle at the given timestamp.
        '''
        if self.df_steering is not None:
            closest_idx = (self.df_steering['time_stamp'] - timestamp).abs().arg_min()
            return self.df_steering.select('data_value')[closest_idx]
        else:
            print("Error: steering data not availalbe")
            return None
    
    def get_driving_mode_at_timestamp(self, timestamp):
        ''' Get the driving mode at the given timestamp.
        
            Args:
            timestamp (int): The timestamp.
            
            Returns:
            str: The driving mode at the given timestamp.
        '''
        if self.df_driving_mode is not None:
            closest_idx = (self.df_driving_mode['time_stamp']-timestamp).abs().arg_min()
            return self.df_driving_mode.select('data_value')[closest_idx]
        else:
            print("Error: driving mode data not availalbe")
            return None
        
    
    def get_target_speed_at_timestamp(self, timestamp):
        ''' Get the target speed at the given timestamp.
        
            Args:
            timestamp (int): The timestamp.
            
            Returns:
            float: The target speed at the given timestamp.
        '''
        if self.df_cruise_control is not None:
            closest_idx = (self.df_cruise_control['timestamp'] - timestamp).abs().arg_min()
            return self.df_cruise_control.select('target_speed')[closest_idx]

        else:
            print("Error: cruise control data not availalbe")
            return None
        
    
    def get_target_steering_angle_at_timestamp (self, timestamp):
        ''' Get the target steering angle at the given timestamp.
        
            Args:
            timestamp (int): The timestamp.
            
            Returns:
            float: The target steering angle at the given timestamp.
        '''
        if self.df_cruise_control is not None:
            closest_idx = (self.df_cruise_control['timestamp'] - timestamp).abs().arg_min()
            return self.df_cruise_control.loc[closest_idx, 'steer_command']
            return self.df_cruise_control.select('target_speed')[closest_idx]

        else:
            print("Error: cruise control data not availalbe")
            return None
                
        
    def get_timestamps_seconds(self):
        ''' Get the timestamps in seconds.
        
            Returns:
            pandas.Series: The timestamps in seconds.
        '''
        return self.timestamps.astype('int64') // 10**9
    
    def get_timestamps_milliseconds(self):
        ''' Get the timestamps in milliseconds.
        
            Returns:
            pandas.Series: The timestamps in milliseconds.
        '''
        return self.timestamps.astype('int64') // 10**6
    
    def get_timestamps_datetime(self):
        ''' Get the timestamps as datetime.
        
            Returns:
            pandas.Series: The timestamps as datetime.
        '''
        return pd.to_datetime(self.timestamps, unit='ms')            
    
    def get_timestamps(self):
        ''' Get the timestamps.
        
            Returns:
            pandas.Series: The timestamps.
        '''
        return self.timestamps