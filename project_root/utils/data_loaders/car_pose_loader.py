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
