import dask.dataframe as dd
from dask.distributed import LocalCluster, Client
from dask import delayed, compute
import csv

def read_path_handler_data(file_path):
    # Read the file using dask dataframe
    df = dd.read_csv(file_path, header=0)

    # Example: Compute the length of each row and process it
    # row_lengths = df.apply(lambda row: row.dropna().shape[0], axis=1, meta=(None, 'int'))
    # row_lengths.compute()
    
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
    df_fixed = df[fixed_columns]
    
    # Check the dtype of 'data_timestamp_sec' and cast if necessary
    if df_fixed['data_timestamp_sec'].dtype != dd.Float64:
        df_fixed = df_fixed.with_columns([dd.col('data_timestamp_sec').cast(dd.Float64)])
    
    # Extract path_x and path_y data and convert to polars DataFrames
    df_path_x = df.select(path_x_columns)
    df_path_y = df.select(path_y_columns)
    
    # Construct the output DataFrames and dictionaries
    path_xy = {
        'path_x_data': df_path_x,
        'path_y_data': df_path_y
    }
    
    return df_fixed, path_xy

    
def dask_by_rows(file_path):
    
    # Define your functions to load and process each line
    def load_line(filename, line_number):
        """Loads a specific line from the file."""
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                if i == line_number:
                    return line.strip()
        return None
    
    def process_line(line):
        """Processes a line, for example by splitting and performing some operations."""
        # Example processing: Splitting the line into values and converting to int
        values = line.split(',')
        # Perform any processing needed
        processed_values = [int(v) for v in values if v.isdigit()]
        return processed_values

    # Create a local Dask cluster and client
    cluster = LocalCluster()
    client = Client(cluster)

    # File details
    filename = 'your_file.csv'

    # Get the total number of lines in the file (if known beforehand, otherwise, calculate it)
    with open(filename, 'r') as f:
        total_lines = sum(1 for _ in f)

    # Create a list of delayed tasks for each line
    tasks = []
    for line_number in range(total_lines):
        # Delay the loading and processing of each line
        delayed_line = delayed(load_line)(filename, line_number)
        delayed_result = delayed(process_line)(delayed_line)
        tasks.append(delayed_result)

    # Compute the tasks in parallel
    results = compute(*tasks)

    return results

from dask.distributed import LocalCluster, Client
from dask import delayed, compute
import csv