from scipy.interpolate import interp1d
import pandas as pd
from utils.data_loaders.car_pose_loader import prepare_car_pose_data


class CarPose:
    ''' This class is used to handle the car pose data. The class initializes with the car pose data.
    
        Methods:
        - get_car_pose_at_timestamp(timestamp): Get the car pose at the given timestamp.
        - get_closest_car_pose(timestamp): Get the car pose closest to the given timestamp.
        - get_trajectory(): Get the car pose trajectory.
        - get_timestamps(): Get the timestamps.
        - set_interpolation(): Prepare the interpolation objects for x,y, and the yaw.
    '''
    def __init__(self, trip_path): 
        self.trip_path = trip_path
        self.df_car_pose = prepare_car_pose_data(trip_path)        
        self.timestamps = self.df_car_pose.index
        self.route  = self.df_car_pose[['cp_x', 'cp_y']]    
        # Prepare the interpolation objects
        self.set_interpolation()        
    
    def set_interpolation(self):
        ''' Prepare the interpolation objects for x, y, and the yaw. '''
        if self.df_car_pose is not None:
            # TODO: handle robustley time units
            # Check if the DataFrame index is already in Unix timestamp format
            if self.df_car_pose.index.dtype != 'int64':
                timestamps = self.df_car_pose.index.astype('int64') // 10**6
            else:
                timestamps = self.df_car_pose.index                      
            # define the interpolation objects
            self.x_interp = interp1d(timestamps, self.df_car_pose['cp_x'], fill_value='extrapolate')
            self.y_interp = interp1d(timestamps, self.df_car_pose['cp_y'], fill_value='extrapolate')
            self.yaw_interp = interp1d(timestamps, self.df_car_pose['cp_yaw_deg'], fill_value='extrapolate')
            
            # prepare a lambda function that does the interpolation for time stamp and store it in the class
            self.interpolate = lambda t: (self.x_interp(t), self.y_interp(t), self.yaw_interp(t))
        else:
            print("No car pose data available.")
                        
    def get_car_pose_at_timestamp(self, timestamp, interpolation = True):
        ''' Get the car pose at the given timestamp.
        
            Parameters:
            timestamp (float): The timestamp to get the car pose.
            
            Returns:
            tuple: A tuple containing the car pose (x, y, theta).
        '''
        if self.df_car_pose is not None:
            if interpolation:
                return self.interpolate(timestamp)
            else:
                return self.get_closest_car_pose(timestamp)
        else:
            print("No car pose data available.")
            return None
        
    def get_closest_car_pose(self, timestamp):
        ''' Get the car pose closest to the given timestamp.
        
            Parameters:
            timestamp (float): The timestamp to get the car pose.
            
            Returns:
            tuple: A tuple containing the car pose (x, y, yaw).
        '''
        if self.df_car_pose is not None:
            closest_timestamp = self.timestamps[self.timestamps.get_loc(timestamp, method='nearest')]
            car_pose = self.df_car_pose.loc[closest_timestamp]
            return (car_pose['cp_x'], car_pose['cp_y'], car_pose['cp_yaw_deg'])
        else:
            print("No car pose data available.")
            return None
    
    # Implement several get_timestamps methods for common used units
    
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
    
    def get_route(self):
        ''' Get the car pose trajectory.
            Returns:
            pandas.DataFrame: The car pose trajectory.
        '''        
        return self.route.values