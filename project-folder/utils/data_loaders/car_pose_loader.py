# car_pose_loader.py
import utils.data_loaders.misc_data_loader_pandas as misc_data_loader
import os
import pandas as pd
from scipy.interpolate import interp1d
from utils.data_loaders.data_converters import save_car_pose_as_pickle, load_car_pose_from_pickle

def prepare_car_pose_data(trip, interpolation=False, car_pose_file_name = 'car_pose.csv', options = None):
    """Prepare car pose data for the cross_analysis."""
    file_path = trip + '/' + car_pose_file_name
            
    # check if the file exists if not try to load file with suffix "_offline", if not return None
    if not os.path.exists(file_path):
        file_path = trip + '/' + car_pose_file_name[:-4] + '_offline.csv'
        if not os.path.exists(file_path):
            return None            
    
    # Check if the data exists as a pickle file
    pickle_path = file_path[:-4] + '.pkl'
    if os.path.exists(pickle_path):
        df_car_pose = load_car_pose_from_pickle(pickle_path)
        print(f"Loaded car pose data from {pickle_path}")
    else:
        # Load the car pose data
        df_car_pose = misc_data_loader.load_trip_car_pose_data(file_path)
        # Save the data as a pickle file
        save_car_pose_as_pickle(file_path, pickle_path)
        print(f"Loaded car pose data from {file_path} and saved to {pickle_path}")
          
    # change the columns names into: timestamp, cp_x, cp_y, cp_yaw_deg
    df_car_pose.columns = ['timestamp', 'cp_x', 'cp_y', 'cp_yaw_deg']
    
    df_car_pose['timestamp'] = pd.to_datetime(df_car_pose['timestamp'], unit='s')
    
    # remove duplicates 
    df_car_pose = df_car_pose.drop_duplicates(subset='timestamp')
    
    # Set the timestamp as the index
    df_car_pose.set_index('timestamp', inplace=True)
    # Reset the index
    # df.reset_index(inplace=True)

    return df_car_pose

class CarPose:
    ''' This class is used to handle the car pose data. The class initializes with the car pose data.
    
        Methods:
        - get_car_pose_at_timestamp(timestamp): Get the car pose at the given timestamp.
        - get_closest_car_pose(timestamp): Get the car pose closest to the given timestamp.
        - get_trajectory(): Get the car pose trajectory.
        - get_timestamps(): Get the timestamps.
        - set_car_pose_data(df_car_pose): Set the car pose data.
        - set_interpolation(): Prepare the interpolation objects for x,y, and the yaw.
    '''
    def __init__(self, df_car_pose = None): 
        if df_car_pose is not None:
            self.set_car_pose_data(df_car_pose)
        else:
            self.df_car_pose = None
            self.timestamps = None
            self.trejectory  = None            
    
    def set_interpolation(self):
        ''' Prepare the interpolation objects for x, y, and the yaw. '''
        if self.df_car_pose is not None:
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
            tuple: A tuple containing the car pose (x, y, yaw).
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
    
    def get_timestamps(self):
        ''' Get the timestamps.
        
            Returns:
            pandas.Series: The timestamps.
        '''
        return self.timestamps
    
    def get_trajectory(self):
        ''' Get the car pose trajectory.
        
            Returns:
            pandas.DataFrame: The car pose trajectory.
        '''
        trajectory = self.df_car_pose[['cp_x', 'cp_y']]
        return trajectory
    
    def set_car_pose_data(self, df_car_pose):
        ''' Set the car pose data.
        
            Parameters:
            df_car_pose (pandas.DataFrame): The car pose data.
        '''
        self.df_car_pose = df_car_pose
        # Check if the DataFrame index is already in Unix timestamp format
        if df_car_pose.index.dtype != 'int64':
            self.timestamps = df_car_pose.index.astype('int64') // 10**6
        else:
            self.timestamps = df_car_pose.index
            
        self.trejectory  = self.get_trajectory()
        self.set_interpolation()