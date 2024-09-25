# test_data_loading.py

# from datetime import time
import time  # Correct import for perf_counter
import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

# # Ensure the parent directory is in the path to locate analysis_manager
# analysis_manager_dir = os.path.abspath(os.path.join(parent_dir, 'analysis_manager'))
# sys.path.insert(0, analysis_manager_dir)

# Ensure the utils directory is in the path
# utils_dir = os.path.abspath(os.path.join(parent_dir, 'utils'))
# sys.path.insert(0, utils_dir)


import pandas_data_loader as  pd_data_loader
import polars_data_loader as pl_data_loader
import dask_data_loader as dask_data_loader
import dask.dataframe as dd

def tic_toc(func):
    def wrapper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        toc = time.perf_counter()
        print(f"{func.__name__} took {toc - tic:0.4f} seconds")
        return result
    return wrapper


@tic_toc
def dask_load_data(filepath):
    return dask_data_loader.dask_by_rows(filepath)

@tic_toc
def pd_load_data(filepath):
    return pd_data_loader.read_path_handler_data(filepath)

@tic_toc
def pl_load_data(filepath):
    return pl_data_loader.read_path_handler_data(filepath)

    
# trip_path = 'Example_Trips/2024-09-11T15_55_30' # '/home/thh3/dev/DebugPlayer/Example_Trips'
# trip_path = '/home/thh3/data/trips/Nissan/12_09_2024/2024-09-12T11_15_25/'
trip_path = '/home/thamam/data/trips/nissan_rtl_bug/2024-09-20T13_43_59/'
path_file_name = 'path_trajectory.csv'
filepath = os.path.join(trip_path, path_file_name)

results_dask = dask_load_data(filepath)
results_pd = pd_load_data(filepath)
results_pl = pl_load_data(filepath)


if __name__ == '__main__':
                freeze_support()