# new_data_loader.py

import polars as pl
from datetime import datetime


import polars as pl

def pl_read_dynamic_path_data_by_rows(filepath):
    """
    Reads a CSV file with dynamic path_x and path_y columns, handling inconsistent row lengths.

    Parameters:
    filepath (str): The path to the directory containing the CSV file.

    Returns:
    tuple: A tuple containing the extracted data as two polars DataFrames.
    """
   
    # Read the entire CSV file as a Polars DataFrame
    # df = pl.read_csv(filepath, infer_schema_length=1, null_values=[""])
    df = pl.read_csv(filepath, infer_schema_length=1, null_values=[""], truncate_ragged_lines=True)

    # Strip leading and trailing spaces from column names
    df.columns = [col.strip() for col in df.columns]
    
    # Define the list of fixed columns
    fixed_columns = [
        'data_timestamp_sec', 'current_speed_mps', 'target_speed_mps', 'turn_signal_state',
        'w_car_pose_now_x_', 'w_car_pose_now_y', 'w_car_pose_now_yaw_rad', 'car_pose_now_timestamp',
        'w_car_pose_image_x', 'w_car_pose_image_y', 'w_car_pose_image_yaw_rad', 'car_pose_image_timestamp_sec'
    ]
    
    # Extract dynamic path_x and path_y columns
    path_x_columns = [col for col in df.columns if col.startswith('path_x_')]
    path_y_columns = [col for col in df.columns if col.startswith('path_y_')]
    
    # Ensure the number of path_x and path_y columns are the same
    assert len(path_x_columns) == len(path_y_columns), "Mismatch in number of path_x and path_y columns"

    # Select the fixed columns and convert to polars DataFrame
    df_fixed = df.select(fixed_columns)
    
    # Check the dtype of 'data_timestamp_sec' and cast if necessary
    if df_fixed['data_timestamp_sec'].dtype != pl.Float64:
        df_fixed = df_fixed.with_columns([pl.col('data_timestamp_sec').cast(pl.Float64)])
    
    # Extract path_x and path_y data and convert to polars DataFrames
    df_path_x = df.select(path_x_columns)
    df_path_y = df.select(path_y_columns)
    
    # Construct the output DataFrames and dictionaries
    path_xy = {
        'path_x_data': df_path_x,
        'path_y_data': df_path_y
    }
    
    return df_fixed, path_xy

# Example usage:
# df_path_data, path_xy = read_dynamic_path_data_by_rows('path_to_file.csv')


def read_path_data(path):
    """
    Reads path data from a CSV file and returns a DataFrame.
    """
    df = pl.read_csv(path)
    
    # scan columns and sort them into : columns that has path_x in col to path_x_columns, and path_y_columns to columns with path_y in col, and fixed_columns to all other columns
    
    
    # Extract fixed columns - no 'path_x_' or 'path_y_' prefix
    fixed_columns = [col for col in df.columns if not 'path_x' in col and not 'path_y' in col]
    
    
    return df



# Add a test for the read_path_data function here
if __name__ == "__main__":
    
    if 0:
        # Assuming df is your Polars DataFrame
        df = pl.DataFrame({
            'path_x1': [1, 2, 3],
            'path_y1': [4, 5, 6],
            'other': [7, 8, 9]
        })

        # Use lazy API to filter columns
        lazy_df = df.lazy()

        path_x_columns = lazy_df.select(pl.col('*path_x*')).collect()
        path_y_columns = lazy_df.select(pl.col('*path_y*')).collect()
        fixed_columns = lazy_df.select(pl.exclude(['*path_x*', '*path_y*'])).collect()

        # Convert back to lists of column names if needed
        path_x_columns = path_x_columns.columns
        path_y_columns = path_y_columns.columns
        fixed_columns = fixed_columns.columns


        path = 'ExampleData/path_trajectory.csv'
        df = read_path_data(path)
        # print(df)