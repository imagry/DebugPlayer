# data_preparation.py

import utils.time_series as time_series
import pandas as pd
import os
import utils.analysis_manager.data_loader as data_loader
from utils.analysis_manager.DataClasses.Class_PathTrajectory import PathTrajectory
from utils.analysis_manager.config import DataFrameType, ClassObjType
import utils.analysis_manager.data_preparation as data_preparation

def load_data_for_trip(trip_path):
    """
    Load data for a trip.

    Args:
        trip_path (str): The path to the trip data.

    Returns:
        tuple: A tuple containing two dictionaries:
            - df_list: A dictionary containing dataframes for different types of data.
            - ClassObjList: A dictionary containing objects for different classes of data.
    """
    df_list = {}
    ClassObjList={}
    
    # Load car pose data
    try:    
        df_car_pose = data_preparation.prepare_car_pose_data(trip_path, interpolation=False) 
        df_list[DataFrameType.CAR_POSE] = df_car_pose
    except:
        print("Car Pose data not found")
        
    
    # Load steering data
    try:
        df_steering = data_preparation.prepare_steering_data(trip_path, interpolation=False) 
        df_list[DataFrameType.STEERING] = df_steering
    except: 
        print("Steering data not found")    
        
    # Load path trajectory data
    try:
        PathObj = data_preparation.prepare_path_data(trip_path, interpolation=False) 
        ClassObjList[ClassObjType.PATH] = PathObj
    except:
        print("Path Trajectory data not found")

    # Load Path Extraction data
    try:
        PathExtractionObj = data_preparation.prepare_path_extraction_data(trip_path, interpolation=False)
        ClassObjList[ClassObjType.PATH_EXTRACTION] = PathExtractionObj
    except:
        print("Path Extraction data not found")

    # load path adjustment data
    try:
        path_adjustment = data_preparation.prepare_path_extraction_data(trip_path, path_file_name="path_adjustment.csv",
                                                                        interpolation=False)
        ClassObjList[ClassObjType.PATH_ADJUSTMENT] = path_adjustment
    except:
        print("Path Adjustment data not found")

    return df_list, ClassObjList
    
def merge_and_prepare_data(df_steering, df_car_pose, interpolation=False):
    """Merge the time series data of steering and car pose."""
    df = time_series.merge_time_series(df_steering, df_car_pose, interpolation=interpolation)
    return df

def prepare_time_data(df_steering, df_car_pose, zero_time=False):
    """Prepare time data by converting it to seconds, optionally zeroing it."""
    if zero_time:
        base_time = max(df_steering.index[0], df_car_pose.index[0])
        cp_time_seconds = (df_car_pose.index - base_time).total_seconds()
        str_time_seconds = (df_steering.index - base_time).total_seconds()
    else:
        if df_car_pose is not None:
            cp_time_seconds = (df_car_pose.index - pd.Timestamp(1970, 1, 1)).total_seconds()
        else:
            cp_time_seconds = None
        if df_steering is not None:
            str_time_seconds = (df_steering.index - pd.Timestamp(1970, 1, 1)).total_seconds()
        else:
            str_time_seconds = None        

    return cp_time_seconds, str_time_seconds

def prepare_path_data(trip_path, interpolation=False, path_file_name = 'path_trajectory.csv', options = None):
    """ Read path data from csv file and prepare it for the cross_analysis.
        Data is loaded and varified for the required columns.
        Time is handled for duplicates or bad lines and converted to seconds.
        All data is returned as a class object for further processing.
        
        Parameters:
        trip_path (str): The path to the trip folder.
        interpolation (bool): Whether to interpolate the data.
        path_file_name (str): The name of the path file.
        options (dict): A dictionary of options to pass to the path
            data loader.    
        
        Returns:
        PathData: A class object containing the path data.        
    """
    
    # load path data
    filepath = trip_path + '/' + path_file_name

    df_path_data, path_xy = data_loader.read_dynamic_path_data_by_rows(filepath)
    
    # convert path_data to pandas dataframe
    PathObj = PathTrajectory(df_path_data, path_xy)
    
    return PathObj    


def prepare_path_extraction_data(trip_path, interpolation=False, path_file_name = 'path_extraction.csv', options = None):
    """ Read path data from csv file and prepare it for the cross_analysis.
        Data is loaded and varified for the required columns.
        Time is handled for duplicates or bad lines and converted to seconds.
        All data is returned as a class object for further processing.
        
        Parameters:
        trip_path (str): The path to the trip folder.
        interpolation (bool): Whether to interpolate the data.
        path_file_name (str): The name of the path file.
        options (dict): A dictionary of options to pass to the path
            data loader.    
        
        Returns:
        PathData: A class object containing the path data.        
    """
    
    # load path data
    filepath = trip_path + '/' + path_file_name

    df_path_extraction_data, path_extraction_xy = data_loader.read_dynamic_path_data_by_rows(filepath)
    
    # convert path_data to pandas dataframe
    PathObj_extraction = PathTrajectory(df_path_extraction_data, path_extraction_xy)
    
    return PathObj_extraction   


def prepare_car_pose_data(trip, interpolation=False, car_pose_file_name = 'car_pose.csv', options = None):
    """Prepare car pose data for the cross_analysis."""
    file_path = trip + '/' + car_pose_file_name
            
    # check if the file exists if not try to load file with suffix "_offline", if not return None
    if not os.path.exists(file_path):
        file_path = trip + '/' + car_pose_file_name[:-4] + '_offline.csv'
        if not os.path.exists(file_path):
            return None            
    df_car_pose = data_loader.load_trip_car_pose_data(file_path)
          
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

def prepare_steering_data(trip_path, interpolation=False, cur_steer_file_name = 'steering.csv', cc_file_name = 'cruise_control.csv' ,options = None):
    """ take the target steering from df_cc and the current steering from df_str and plot them as well as their rate of change as function of time
    Convert the timestamp to datetime """
           
    # Load steering data
    # Check if steering.csv exist before attempting to read it
    if os.path.exists(os.path.join(trip_path, cur_steer_file_name)):
        str_file_path = os.path.join(trip_path, cur_steer_file_name)
        df_str = data_loader.load_trip_steering_data(str_file_path)    
    else:
        df_str = None
        
   
    # Check if the cruise control data is available at trip_path
    if os.path.exists(os.path.join(trip_path, cc_file_name)):
        df_cc = data_loader.load_trip_cruise_control_data(trip_path)
    else :
        df_cc = None
    
    
    
    ## Process the current steering data
    if df_str is not None:

        # Convert the timestamp to datetime
        df_str['timestamp'] = pd.to_datetime(df_str['timestamp'], unit='s')
            
        # remove duplicates
        df_str = df_str.drop_duplicates(subset='timestamp')
        
        # Todo: fix this check and make sure it is really necessary to move into time indexing
        # Set the timestamp as the index
        # df_str.set_index('timestamp', inplace=True)

        # Compute the rate of change of the current steering
            
        # Apply low-pass filter to the current steering before computing the rate of change
        df_str['current_steering_deg_smoohted'] = df_str['current_steering_deg'].rolling(window=10).mean()  
        
        # Compute the difference in timestamp and convert to total seconds
        df_str['timestamp'] = pd.to_datetime(df_str['timestamp'], unit='s')
        timestamp_diff = df_str['timestamp'].diff().dt.total_seconds()
        # Calculate the steer_command_rate
        # Compute the derivative (rate of change) of steer_command
        steer_command_diff = df_str['current_steering_deg_smoohted'].diff()
        df_str['current_steering_rate'] = steer_command_diff / timestamp_diff
        
        # compute second derivative        
        df_str['current_steering_acc'] = df_str['current_steering_rate'].diff() / timestamp_diff
        
        


    ## Process the cruise control data
    if df_cc is not None and  'steer_command' in df_cc.columns:               
        # Convert the timestamp to datetime
        df_cc['timestamp'] = pd.to_datetime(df_cc['timestamp'], unit='s')
        # remove duplicates
        df_cc = df_cc.drop_duplicates(subset='timestamp')

        # Todo: fix this check and make sure it is really necessary to move into time indexing                
        # Set the timestamp as the index
        # df_cc.set_index('timestamp', inplace=True)
        
        # Apply low-pass filter to the current steering before computing the rate of change
        df_cc['steer_command_smoohted'] = df_cc['steer_command'].rolling(window=10).mean()
        
        # Compute the derivative (rate of change) of steer_command
        steer_command_diff = df_cc['steer_command_smoohted'].diff()
        # Compute the difference in timestamp and convert to total seconds
        timestamp_diff = df_cc['timestamp'].diff().dt.total_seconds()
        # Calculate the steer_command_rate
        df_cc['steer_command_rate'] = steer_command_diff / timestamp_diff
        
        # compute second derivative        
        df_cc['steer_command_acc'] = df_cc['steer_command_rate'].diff() / timestamp_diff
        
        
    if df_str is not None:
        if df_cc is not None and 'steer_command' in df_cc.columns:
            # joint the steering data from both dataframes
            df_steering = time_series.merge_time_series(df_str, df_cc, interpolation=True)
        else:
            df_steering = df_str
            df_steering.set_index('timestamp', inplace=True)
    else:
        if df_cc is not None and 'steer_command' in df_cc.columns:
            df_steering = df_cc
            df_steering.set_index('timestamp', inplace=True)
        else:
            df_steering = None                     
                   
    return df_steering