# from datetime import time
import time  # Correct import for perf_counter
import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

# Ensure the parent directory is in the path to locate analysis_manager
analysis_manager_dir = os.path.abspath(os.path.join(parent_dir, 'analysis_manager'))
sys.path.insert(0, analysis_manager_dir)

from utils.data_loader import read_dynamic_path_data_by_rows
import utils.new_data_loader as new_data_loader
    

def tic_toc(func):
    def wrapper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        toc = time.perf_counter()
        print(f"{func.__name__} took {toc - tic:0.4f} seconds")
        return result
    return wrapper


@tic_toc
def load_data(filepath):
    return read_dynamic_path_data_by_rows(filepath)

@tic_toc
def load_new_data(filepath):
    return new_data_loader.pl_read_dynamic_path_data_by_rows(filepath)

    
# trip_path = 'Example_Trips/2024-09-11T15_55_30' # '/home/thh3/dev/DebugPlayer/Example_Trips'
trip_path = '/home/thh3/data/trips/Nissan/12_09_2024/2024-09-12T11_15_25/'
path_file_name = 'path_trajectory.csv'
filepath = os.path.join(trip_path, path_file_name)

df_path_data, path_xy = load_data(filepath)
df_path_data_pl, path_xy_pl = load_new_data(filepath)

df_path_data, path_xy = load_data(filepath)
df_path_data_pl, path_xy_pl = load_new_data(filepath)

df_path_data, path_xy = load_data(filepath)
df_path_data_pl, path_xy_pl = load_new_data(filepath)

# Optional: Verify that both dataframes contain the same data structure and content
assert df_path_data.shape == df_path_data_pl.shape, "DataFrame shapes do not match!"
assert all(df_path_data.columns == df_path_data_pl.columns), "Column names do not match!"