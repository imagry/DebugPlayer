# path_handler_loader_pandas.py
import pandas as pd
import os
from utils.data_loaders.data_converters import save_path_handler_data_as_pickle, load_path_handler_data_from_pickle


def read_path_handler_data(filepath):
    """
    Reads a CSV file with dynamic path_x and path_y columns, handling inconsistent row lengths.

    Parameters:
    trip_path (str): The path to the directory containing the CSV file.

    Returns:
    dict: A dictionary containing the extracted data.
    """
    
    # Check if the data exists as a pickle file
    pickle_path = filepath[:-4] + '.pkl'
    if os.path.exists(pickle_path):
        df_path_data, path_xy = load_path_handler_data_from_pickle(pickle_path)
        print(f"Loaded path data from {pickle_path}")
        return df_path_data, path_xy
      
    #### If we don't have a pickle file, read the CSV file
    
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
        
    # Save the data as a pickle file for future readings
    save_path_handler_data_as_pickle(filepath, pickle_path, (df_path_data, path_xy)) 
    print(f"Loaded path data from {filepath} and saved to {pickle_path}") 
    
    return df_path_data, path_xy