# Description: A utility function to read multiple log files to obtain vehicle state
import polars as pl
from datetime import datetime


import polars as pl

#  cruise_control.csv, driving_mode.csv, speed.csv, steering
def read_vehicle_state_logs(filepath, log_files_names = None):
    """
    Reads a CSV file with dynamic path_x and path_y columns, handling inconsistent row lengths.

    Parameters:
    filepath (str): The path to the directory containing the CSV file.

    Returns:
    tuple: A tuple containing the extracted data as two polars DataFrames.
    """
    files_to_read = []

    if log_files_names is None:
        log_files_names = ['cruise_control.csv', 'driving_mode.csv', 'speed.csv', 'steering.csv']
    
    try:
        for log_file in log_files_names:
            files_to_read.append(filepath + log_file)   
            
        for file in files_to_read:
            # Read the entire CSV file as a Polars DataFrame
            try:
                df = pl.read_csv(file, null_values=[""], truncate_ragged_lines=True)
                # Strip leading and trailing spaces from column names
                df.columns = [col.strip() for col in df.columns]
            except:
                print(f"Error: Could not read the log file {file}")
                df = None
            
            if file == files_to_read[0]:
                df_cruise_control = df
            elif file == files_to_read[1]:
                df_driving_mode = df
            elif file == files_to_read[2]:
                df_speed = df
            elif file == files_to_read[3]:
                df_steering = df
            else:
                print("Error: Could not read the log files")
                return None
    except:
        print("Error: Could not read the log files")
        return None 
    
    return df_cruise_control, df_driving_mode, df_speed, df_steering
    