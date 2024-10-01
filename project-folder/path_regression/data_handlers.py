# data_handlers.py
import pandas as pd
import os
import argparse
from PySide6 import QtWidgets
from PySide6.QtWidgets import QFileDialog
import  pickle
# add project-folder to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
from plot_functions import update_plot
import analysis_manager.data_preparation as dp
from DataClasses.PathRegressor import PathRegressor

def parse_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Main Analysis Manager")    
    # Add the --trip argument
    parser.add_argument('--trip1', type=str, help='Path to the first trip file')
    parser.add_argument('--trip2', type=str, default=None, help='Path to the second trip file')
    # Parse the command-line arguments
    args = parser.parse_args()    
    # Check if the --trip flag is provided
    if args.trip1 and args.trip2:
        return args.trip1, args.trip2
    elif args.trip1:
        return args.trip1, None
    else:
        raise ValueError("Please provide the paths to both trip files using the --trip1 and --trip2 flags")


def load_data(trip_path, caching_mode_enabled, CACHE_DIR ):
    """
    Load data from the trip file or from cached files if available.
    Args:
        trip_path (str): Path to the trip file.
    Returns:
        tuple: PathObj and df_car_pose DataFrames.
    """
    if (caching_mode_enabled):
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

    if (caching_mode_enabled):  # Save the data to the cache file if caching is enabled
        # Save the data to the cache file
        with open(CACHE_FILE_PATH, 'wb') as cache_file:
            pickle.dump((PathObj, df_car_pose), cache_file)
            print("Saved data to cache.")

    return PathObj, df_car_pose



def load_trip_path(prg_obj, ui_elements):
    """Open a file dialog to load a trip path."""
    trip_dir_path = QFileDialog.getExistingDirectory(None, 'Open Trip Folder', '') 

    if trip_dir_path:
        if prg_obj is not None:
            reset(prg_obj, ui_elements)    
        PathObj, df_car_pose = load_data(trip_dir_path, caching_mode_enabled=True, CACHE_DIR = ui_elements['CACHE_DIR'] )                
        prg_obj = PathRegressor(PathObj,os.path.basename(trip_dir_path),df_car_pose, CACHE_DIR = ui_elements['CACHE_DIR'] , 
                                delta_t_sec= ui_elements['delta_t_input'], pts_before=ui_elements['pts_before_spin'], pts_after=ui_elements['pts_after_spin'], max_workers=ui_elements['MAX_WORKERS']) 
    return prg_obj

def reset(prg_obj, ui_elements):
    """Reset the plot and settings to their default values."""
    plt = ui_elements['plt']
    prg_obj.PathObj = None
    prg_obj.df_car_pose = None
    plt.clear()
    
def create_path_regressors(ui_elements, PathObj1, trip_path1, df_car_pose1, PathObj2, trip_path2, df_car_pose2, CACHE_DIR, MAX_WORKERS):
    """Create PathRegressor objects and return them in a dictionary."""
    delta_t_sec = float(ui_elements['delta_t_input'].text())
    pts_before_val = ui_elements['pts_before_spin'].value()
    pts_after_val = ui_elements['pts_after_spin'].value()

    prg_obj1 = PathRegressor(PathObj1, os.path.basename(trip_path1), df_car_pose1, CACHE_DIR, delta_t_sec, pts_before_val, pts_after_val, max_workers=MAX_WORKERS)
    prg_obj2 = PathRegressor(PathObj2, os.path.basename(trip_path2), df_car_pose2, CACHE_DIR, delta_t_sec, pts_before_val, pts_after_val, max_workers=MAX_WORKERS)

    return {'prg_obj1': prg_obj1, 'prg_obj2': prg_obj2}
    