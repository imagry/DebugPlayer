# path_handler_loader.py
import numpy as np
import pandas as pd
import os
import sys
from data_classes.PathTrajectory_pandas import PathTrajectory
from 
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.insert(0, f"{parent_dir}/utils")

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

    df_path_data, path_xy = pd_path_loader.read_path_handler_data(filepath)
    
    # convert path_data to pandas dataframe
    PathObj = PathTrajectory_pandas.PathTrajectory(df_path_data, path_xy)
    
    return PathObj    