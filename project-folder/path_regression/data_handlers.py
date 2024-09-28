# data_handlers.py
import pandas as pd
import os
import argparse
from PySide6 import QtWidgets
import  pickle
# add project-folder to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
from plot_functions import update_plot
import analysis_manager.data_preparation as dp


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

def load_trip_path(prg_obj, ui_elements):
    """Open a file dialog to load a trip path."""
    file_dialog = QtWidgets.QFileDialog()
    file_in_trip_path, _ = file_dialog.getOpenFileName(None, 'Open Trip File', '', 'Trip Files (*.csv)')
    if file_in_trip_path:
        reset(prg_obj, ui_elements)
        trip_dir_path = os.path.dirname(file_in_trip_path)
        PathObj, df_car_pose = load_data(trip_dir_path, caching_mode_enabled=True, CACHE_DIR="cache")
        prg_obj.PathObj = PathObj
        prg_obj.df_car_pose = df_car_pose
        update_plot(ui_elements, prg_obj)


def reset(prg_obj, ui_elements):
    """Reset the plot and settings to their default values."""
    plt = ui_elements['plt']
    prg_obj.PathObj = None
    prg_obj.df_car_pose = None
    plt.clear()