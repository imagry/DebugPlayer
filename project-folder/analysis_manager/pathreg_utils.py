# main_analysis_manager.py
import os
import sys
from init_utils import initialize_environment
# Initialize the environment
initialize_environment()
import argparse
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import pickle
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

import data_preparation as dp 
import utils.plotting.plot_helpers as plt_helper
from data_classes.PathTrajectory_pandas import PathTrajectory
from typing import TypeAlias
from data_classes.PathRegressor import PathRegressor



# Some general helper functions
def get_color_list(n_colors):
    # Generate n_colors distinct colors
    import matplotlib.pyplot as plt
    cmap = plt.get_cmap('hsv')
    return [pg.mkColor(cmap(i / n_colors)) for i in range(n_colors)]

def parse_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Main Analysis Manager")    
    # Add the --trip argument
    parser.add_argument('--trip', type=str, help='Path to the trip file')    
    # Parse the command-line arguments
    args = parser.parse_args()    
    # Check if the --trip flag is provided
    if args.trip:
        return args.trip   
    else:
        raise ValueError("Please provide the path to the trip file using the --trip flag")

def load_data(trip_path, cachine_mode_enabled, CACHE_DIR ):
    """
    Load data from the trip file or from cached files if available.
    Args:
        trip_path (str): Path to the trip file.
    Returns:
        tuple: PathObj and df_car_pose DataFrames.
    """
    if (cachine_mode_enabled):
        # Extract trip name
        trip_name = os.path.basename(os.path.normpath(trip_path))
        CACHE_FILE_PATH = f"{CACHE_DIR}/{trip_name}.pkl"

        # Ensure the cache directory exists
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        # Check if the cached file exists
        if os.path.exists(CACHE_FILE_PATH):
            with open(CACHE_FILE_PATH, 'rb') as cache_file:
                PathObj, df_car_pose = pickle.load(cache_file)
                print("Loaded data from cache.")
                return PathObj, df_car_pose

    # Load data from the trip file
    PathObj = dp.prepare_path_data(trip_path, interpolation=False)
    df_car_pose = dp.prepare_car_pose_data(trip_path, interpolation=False)

    if (cachine_mode_enabled):  # Save the data to the cache file if caching is enabled
        # Save the data to the cache file
        with open(CACHE_FILE_PATH, 'wb') as cache_file:
            pickle.dump((PathObj, df_car_pose), cache_file)
            print("Saved data to cache.")

    return PathObj, df_car_pose

def prepare_plot_data(idx, timestamp_idx, x_vp, y_vp, color):
    """
    Prepare the data for a given timestamp index.
    This function returns the mask and the color.
    """
    mask = timestamp_idx == idx
    return (x_vp[mask], y_vp[mask], color)

    
    



        
# Plot Trajectory: Plot the entire path with line and markers that shows the data points
# def initial_plot(plt):
#     plt.clear()
#     plt.plot(cp_x, cp_y, pen=None, symbol='o', symbolBrush='b')

#     # Evaluate extract_virtual_path function and plot the results
#     delta_t_sec_val = float(delta_t_input.text())
#     pts_before_val = pts_before_spin.value()
#     pts_after_val = pts_after_spin.value()


#     # Todo: Instantiate the new class PathRegressor
#     prg = PathRegressor(PathObj, df_car_pose, delta_t_sec_val, pts_before_val, pts_after_val,max_workers= MAX_WORKERS)
    
#     v_p = prg.get_virtual_path()
    
#     df_virt_path, v_p 

#     # Virtual path plot (v_p): plot on the same figure with the car pose trajectory drawn
#     # Use different colors per the indexes of v_p[:,2] to show the path points extracted at each timepoint
#     if v_p.size > 0:
#         x_vp = v_p[:,0]
#         y_vp = v_p[:,1]
#         timestamp_idxs = v_p[:,2]
        
#         plt.plot(x_vp, y_vp, pen=None, symbol='o', symbolBrush='r')
#         # plot_virtual_path_parallel(x_vp, y_vp, timestamp_idxs)        