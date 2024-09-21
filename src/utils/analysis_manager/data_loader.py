# data_loader.py
import numpy as np
import pandas as pd
import os
from aidriver_logs_readers.path_loader import read_nissan_imu_data, read_path_data
import aidriver_logs_readers.utils_trip_data_handler as dh
import pandas as pd

def general_read_dynamic_path_data_by_rows(filepath, columns=None):
    """
    Reads a CSV file with dynamic path_x and path_y columns, handling inconsistent row lengths.

    Parameters:
    filepath (str): The path to the CSV file.
    columns (list, optional): List of column names. If not provided, inferred from the first line of the CSV file.

    Returns:
    tuple: A tuple containing a DataFrame with fixed columns and a dictionary with path_x and path_y DataFrames.
    """
    # Initialize containers for the extracted data
    data = {}
    path_x_columns = []
    path_y_columns = []

    # Read the file line by line and split it into columns
    with open(filepath, 'r') as file:
        # Infer columns from the first line if not provided
        if columns is None:
            columns = [col.strip() for col in file.readline().strip().split(',')]
        else:
            file.readline()  # Skip the header line

        # Initialize data dictionary with empty lists for each column
        for col in columns:
            data[col] = []

        # Identify dynamic path_x and path_y columns
        path_x_columns = [col for col in columns if col.startswith('path_x_')]
        path_y_columns = [col for col in columns if col.startswith('path_y_')]

        # Ensure the number of path_x and path_y columns are the same
        assert len(path_x_columns) == len(path_y_columns), "Mismatch in number of path_x and path_y columns"

        # Read each line, split into columns, and populate the data
        for line in file:
            row = line.strip().split(',')

            # Append data for each column
            for col in columns:
                index = columns.index(col)
                data[col].append(row[index] if index < len(row) else None)

    # Convert lists of lists into DataFrames for path_x_data and path_y_data
    path_x_df = pd.DataFrame(data[path_x_columns], columns=path_x_columns)
    path_y_df = pd.DataFrame(data[path_y_columns], columns=path_y_columns)

    # Convert the data_timestamp_sec to numeric
    if 'data_timestamp_sec' in data:
        data['data_timestamp_sec'] = pd.to_numeric(data['data_timestamp_sec'])

    # Create a dictionary for fixed columns excluding path_x and path_y columns
    fixed_columns = {col: pd.Series(pd.to_numeric(data[col])) if col != 'turn_signal_state' else pd.Series(data[col])
                     for col in columns if col not in path_x_columns + path_y_columns}

    # Convert fixed columns dictionary into a DataFrame
    df_path_data = pd.DataFrame(fixed_columns)

    # Define a dictionary for path_x and path_y DataFrames
    path_xy = {
        'path_x_data': path_x_df,
        'path_y_data': path_y_df
    }

    return df_path_data, path_xy

def read_dynamic_path_data_by_rows(filepath):
    """
    Reads a CSV file with dynamic path_x and path_y columns, handling inconsistent row lengths.

    Parameters:
    trip_path (str): The path to the directory containing the CSV file.

    Returns:
    dict: A dictionary containing the extracted data.
    """
   
    # Initialize containers for the extracted data
    data = {
        'data_timestamp_sec': [],
        'current_speed_mps': [],
        'target_speed_mps': [],
        'turn_signal_state': [],
        'w_car_pose_now_x': [],
        'w_car_pose_now_y': [],
        'w_car_pose_now_yaw_rad': [],
        'car_pose_now_timestamp': [],
        'w_car_pose_image_x': [],
        'w_car_pose_image_y': [],
        'w_car_pose_image_yaw_rad': [],
        'car_pose_image_timestamp_sec': [],
        'path_x_data': [],
        'path_y_data': []
    }

    # Read the file line by line and split it into columns
    with open(filepath, 'r') as file:
        # header = file.readline().strip().split(',')
        header = [col.strip() for col in file.readline().strip().split(',')]

        # Find the indexes of fixed columns
        fixed_columns = [
            'data_timestamp_sec', 'current_speed_mps', 'target_speed_mps', 'turn_signal_state',
            'w_car_pose_now_x_', 'w_car_pose_now_y', 'w_car_pose_now_yaw_rad', 'car_pose_now_timestamp',
            'w_car_pose_image_x', 'w_car_pose_image_y', 'w_car_pose_image_yaw_rad', 'car_pose_image_timestamp_sec'
        ]
        fixed_indices = [header.index(col) for col in fixed_columns]

        # Extract the dynamic path_x_ and path_y_ columns from the header
        path_x_columns = [col for col in header if col.startswith('path_x_')]
        path_y_columns = [col for col in header if col.startswith('path_y_')]
        
        # Ensure the number of path_x and path_y columns are the same
        assert len(path_x_columns) == len(path_y_columns), "Mismatch in number of path_x and path_y columns"

        # Read each line, split into columns, and populate the data
        for line in file:
            row = line.strip().split(',')
            
            # Append data for fixed columns
            data['data_timestamp_sec'].append(row[fixed_indices[0]])
            data['current_speed_mps'].append(row[fixed_indices[1]])
            data['target_speed_mps'].append(row[fixed_indices[2]])
            data['turn_signal_state'].append(row[fixed_indices[3]])
            data['w_car_pose_now_x'].append(row[fixed_indices[4]])
            data['w_car_pose_now_y'].append(row[fixed_indices[5]])
            data['w_car_pose_now_yaw_rad'].append(row[fixed_indices[6]])
            data['car_pose_now_timestamp'].append(row[fixed_indices[7]])
            data['w_car_pose_image_x'].append(row[fixed_indices[8]])
            data['w_car_pose_image_y'].append(row[fixed_indices[9]])
            data['w_car_pose_image_yaw_rad'].append(row[fixed_indices[10]])
            data['car_pose_image_timestamp_sec'].append(row[fixed_indices[11]])

            # Append data for dynamic path_x and path_y columns (ensure column count matches)
            path_x_data = [row[header.index(col)] if header.index(col) < len(row) else None for col in path_x_columns]
            path_y_data = [row[header.index(col)] if header.index(col) < len(row) else None for col in path_y_columns]
            
            data['path_x_data'].append(path_x_data)
            data['path_y_data'].append(path_y_data)

    # Convert lists of lists into DataFrames for path_x_data and path_y_data
    path_x_df = pd.DataFrame(data['path_x_data'], columns=path_x_columns)
    path_y_df = pd.DataFrame(data['path_y_data'], columns=path_y_columns)
    
    # Convert the data_timestamp_sec to datetime
    data['data_timestamp_sec'] = pd.to_numeric(data['data_timestamp_sec'])
    
    # Return the extracted data as a dictionary
    path_dict =  {
        'data_timestamp_sec': pd.Series(data['data_timestamp_sec']),
        'current_speed_mps': pd.Series(pd.to_numeric(data['current_speed_mps'])),
        'target_speed_mps': pd.Series(pd.to_numeric(data['target_speed_mps'])),
        'turn_signal_state': pd.Series(data['turn_signal_state']),
        'w_car_pose_now_x': pd.Series(pd.to_numeric(data['w_car_pose_now_x'])),
        'w_car_pose_now_y': pd.Series(pd.to_numeric(data['w_car_pose_now_y'])),
        'w_car_pose_now_yaw_rad': pd.Series(pd.to_numeric(data['w_car_pose_now_yaw_rad'])),
        'car_pose_now_timestamp': pd.Series(pd.to_numeric(data['car_pose_now_timestamp'])),
        'w_car_pose_image_x': pd.Series(pd.to_numeric(data['w_car_pose_image_x'])),
        'w_car_pose_image_y': pd.Series(pd.to_numeric(data['w_car_pose_image_y'])),
        'w_car_pose_image_yaw_rad': pd.Series(pd.to_numeric(data['w_car_pose_image_yaw_rad'])),
        'car_pose_image_timestamp_sec': pd.Series(data['car_pose_image_timestamp_sec']),
    }
    
    # convert path_dict into dataframe excluding x,y values
    df_path_data = pd.concat([path_dict['data_timestamp_sec'], path_dict['current_speed_mps'], path_dict['target_speed_mps'], path_dict['turn_signal_state'], path_dict['w_car_pose_now_x'], path_dict['w_car_pose_now_y'], path_dict['w_car_pose_now_yaw_rad'], path_dict['car_pose_now_timestamp'], path_dict['w_car_pose_image_x'], path_dict['w_car_pose_image_y'], path_dict['w_car_pose_image_yaw_rad'], path_dict['car_pose_image_timestamp_sec']], axis=1)
    
    # set the names of the dataframe columns
    df_path_data.columns = ['data_timestamp_sec', 'current_speed_mps', 'target_speed_mps', 'turn_signal_state', 'w_car_pose_now_x_', 'w_car_pose_now_y', 'w_car_pose_now_yaw_rad', 'car_pose_now_timestamp', 'w_car_pose_image_x', 'w_car_pose_image_y', 'w_car_pose_image_yaw_rad', 'car_pose_image_timestamp_sec']
    
    # define a nested list p such that p[i] is [N_i x 2] array of 2d points of the path  defined by (path_x_df container for the x and y values
    path_xy = {'path_x_data': path_x_df,
               'path_y_data': path_y_df}
    
    
    return df_path_data, path_xy

def read_dynamic_path_data(trip_path):
    """
    Reads a CSV file with dynamic path_x and path_y columns.

    Parameters:
    filepath (str): The path to the CSV file.

    Returns:
    dict: A dictionary containing the extracted data.
    """
    # Read the CSV file
    filepath =  trip_path +'/'+ 'path_trajectory.csv' 

    df = pd.read_csv(filepath, header=0, engine='python')
    df = pd.read_csv(filepath, header=0, engine='python', error_bad_lines=False, warn_bad_lines=True)

    # Extract fixed columns
    data_timestamp_sec = df['data_timestamp_sec']
    current_speed_mps = df['current_speed_mps']
    target_speed_mps = df['target_speed_mps']
    turn_signal_state = df['turn_signal_state']
    w_car_pose_now_x = df['w_car_pose_now_x_']
    w_car_pose_now_y = df['w_car_pose_now_y']
    w_car_pose_now_yaw_rad = df['w_car_pose_now_yaw_rad']
    car_pose_now_timestamp = df['car_pose_now_timestamp']
    w_car_pose_image_x = df['w_car_pose_image_x']
    w_car_pose_image_y = df['w_car_pose_image_y']
    w_car_pose_image_yaw_rad = df['w_car_pose_image_yaw_rad']
    car_pose_image_timestamp_sec = df['car_pose_image_timestamp_sec']

    # Determine the number of path_x and path_y pairs
    path_columns = [col for col in df.columns if col.startswith('path_x_') or col.startswith('path_y_')]
    path_x_columns = [col for col in path_columns if col.startswith('path_x_')]
    path_y_columns = [col for col in path_columns if col.startswith('path_y_')]

    # Ensure the number of path_x and path_y columns are the same
    assert len(path_x_columns) == len(path_y_columns), "Mismatch in number of path_x and path_y columns"

    # Extract path_x and path_y data
    path_x_data = df[path_x_columns]
    path_y_data = df[path_y_columns]

    # Return the extracted data as a dictionary
    return {
        'data_timestamp_sec': data_timestamp_sec,
        'current_speed_mps': current_speed_mps,
        'target_speed_mps': target_speed_mps,
        'turn_signal_state': turn_signal_state,
        'w_car_pose_now_x': w_car_pose_now_x,
        'w_car_pose_now_y': w_car_pose_now_y,
        'w_car_pose_now_yaw_rad': w_car_pose_now_yaw_rad,
        'car_pose_now_timestamp': car_pose_now_timestamp,
        'w_car_pose_image_x': w_car_pose_image_x,
        'w_car_pose_image_y': w_car_pose_image_y,
        'w_car_pose_image_yaw_rad': w_car_pose_image_yaw_rad,
        'car_pose_image_timestamp_sec': car_pose_image_timestamp_sec,
        'path_x_data': path_x_data,
        'path_y_data': path_y_data
    }

def load_trip_data(trip_path, data_ds_factor):
    X_gps_lng_lat, df_xyz = dh.load_trip_gps_data(trip_path, coordinates_type="both",
                                                  sample_spacing=data_ds_factor, tangent_frame="NED")
    df_imu = read_nissan_imu_data(trip_path)
    yaw = np.asarray(df_imu['yaw'])
    t_yaw = np.asarray(df_imu['time_stamp'])
    return X_gps_lng_lat, df_xyz, yaw, t_yaw

def load_trip_cruise_control_data(trip_path):
    cc_file = trip_path + r"/cruise_control.csv"
    df_cc = pd.read_csv(cc_file)
    return df_cc

def load_trip_car_pose_data(car_pose_file):    
    df_car_pose = pd.read_csv(car_pose_file)
    return df_car_pose
    
def load_trip_steering_data(steering_file_path):    
    df_steering = pd.read_csv(steering_file_path)
    # change the column name of the steering data from data_value to "current_steering_deg"
    df_steering.rename(columns={'data_value': 'current_steering_deg'}, inplace=True)
    # change the column name of "time_stamp" to "timestamp"
    df_steering.rename(columns={'time_stamp': 'timestamp'}, inplace=True)
    
    return df_steering


