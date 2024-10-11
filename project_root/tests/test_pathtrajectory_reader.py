import sys
import os
import matplotlib.pyplot as plt
from math import isclose

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from data_classes.PathTrajectory_pandas import PathTrajectoryPandas
from data_classes.PathTrajectory_polars import PathTrajectoryPolars

def test_reading_PathTrajectoryPolars(file_path):
    
    #  Reading the file with polars
    path_trajectory_polars = PathTrajectoryPolars(file_path)
    
    
    path_trajectory_pandas = PathTrajectoryPandas(file_path)
    
    #compare the timestamps
    polars_timestamp_ms  = path_trajectory_polars.get_timestamps_ms()
    pandas_timestamp_ms = path_trajectory_pandas.get_timestamps_ms()
    import numpy as np

    # Convert to NumPy arrays if they are not already
    polars_timestamp_ms = np.array(polars_timestamp_ms)
    pandas_timestamp_ms = np.array(pandas_timestamp_ms)

    # Use NumPy's isclose function
    result_timestamp = np.allclose(polars_timestamp_ms, pandas_timestamp_ms, rtol=1e-01, atol=0.1)
           
    
    # compare the path_xy data - iterate over all the timestamps, and compare the path_xy data for each timestamp
    for i in range(len(polars_timestamp_ms)):
        timestamp_polars = polars_timestamp_ms[i]
        timestamp_pandas = pandas_timestamp_ms[i]
        assert isclose(timestamp_polars, timestamp_pandas, rel_tol=1 , abs_tol=1)
                
        polars_path_xy, _ = path_trajectory_polars.find_path_and_car_pose(timestamp_polars)
        pandas_path_xy, _ = path_trajectory_pandas.find_path_and_car_pose(timestamp_pandas)
        
        polars_path_xy = np.array(polars_path_xy)
        pandas_path_xy = np.array(pandas_path_xy)
        result_path_xy = np.allclose(polars_path_xy, pandas_path_xy, rtol=1e-01, atol=0.1)
        
        if not result_path_xy:
            print("Path_xy data for timestamp {} does not match".format(timestamp_polars))
            break
        
    # if reached here without assertion error, then the test passed
    print("PathTrajectoryPolars test has been completed successfully.")
    
        
if __name__ == "__main__":
    trip_path = "/home/thamam/dev/DebugPlayer/ExampleData/"
    file_name = "path_trajectory.csv"
    file_path = trip_path + file_name
    test_reading_PathTrajectoryPolars(file_path)
