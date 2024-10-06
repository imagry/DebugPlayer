# path_handler_loader.py
import numpy as np
import pandas as pd
import os
import sys
from data_classes.PathTrajectory_pandas import PathTrajectory
import utils.data_loaders.path_handler_loader_pandas as pd_path_loader
from utils.data_loaders.data_converters import save_path_handler_data_as_pickle, load_path_handler_data_from_pickle

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

    # Check if the data exists as a pickle file
    pickle_path = filepath[:-4] + '.pkl'
    if os.path.exists(pickle_path):
        df_path_data, path_xy = load_path_handler_data_from_pickle(pickle_path)
        print(f"Loaded path data from {pickle_path}")
    else:
        # Read the path data
        df_path_data, path_xy = pd_path_loader.read_path_handler_data(filepath)
        # Save the data as a pickle file
        save_path_handler_data_as_pickle(filepath, pickle_path) 
        print(f"Loaded path data from {filepath} and saved to {pickle_path}")   
    
    # convert path_data to pandas dataframe
    PathObj = PathTrajectory(df_path_data, path_xy)
    
    return PathObj    