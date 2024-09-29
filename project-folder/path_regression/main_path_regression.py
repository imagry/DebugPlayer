# main_path_regression.py

# main_analysis_manager.py
import os
import sys
import sys
import os
# Add the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import pyqtgraph as pg
from PySide6 import QtWidgets, QtCore
import pandas as pd
import numpy as np
import multiprocessing

from data_handlers import load_data, parse_arguments
from ui_components import create_main_window, connect_signals
from plot_functions import save_figure
from DataClasses.PathRegressor import PathRegressor


# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def main():    
    # Global settings
    cpu_num = multiprocessing.cpu_count() 
    MAX_WORKERS = np.floor(cpu_num * 0.8)
    # set CAHCE_DIR to the cache directory in personal-folder by appending 'personal-folder' to os.dir_name 0f parent_dir
    CACHE_DIR = os.path.join(os.path.dirname(parent_dir), "personal-folder", "cache")
    caching_mode_enabled = True

    # GUI - Set up the application and main window
    app = pg.mkQApp("Path Regression Analysis")

    # Create the main window widget and UI elements
    main_win, run_button, load_button1, load_button2, update_plot_button, save_button, ui_elements, ui_display_elements = create_main_window()

    # Data Handling
    trip_path1, trip_path2 = parse_arguments()
    PathObj1, df_car_pose1 = load_data(trip_path1, caching_mode_enabled, CACHE_DIR)
    if trip_path2 is not None:
        PathObj2, df_car_pose2 = load_data(trip_path2, caching_mode_enabled, CACHE_DIR)
    else:    
        PathObj2 = None
        df_car_pose2 = None
        print("Only one trip is loaded.")

    # Path Regressor
    delta_t_sec = float(ui_elements['delta_t_input'].text())
    pts_before_val = ui_elements['pts_before_spin'].value()
    pts_after_val = ui_elements['pts_after_spin'].value()
    prg_obj1 = PathRegressor(PathObj1, os.path.basename(trip_path1) ,df_car_pose1, CACHE_DIR, delta_t_sec, pts_before_val, pts_after_val, max_workers=MAX_WORKERS)
    prg_obj2 = PathRegressor(PathObj2, os.path.basename(trip_path2) ,df_car_pose2, CACHE_DIR, delta_t_sec, pts_before_val, pts_after_val, max_workers=MAX_WORKERS)

    # add to ui elements the item CACHE_DIR with value CACHE_DIR
    ui_elements['CACHE_DIR'] = CACHE_DIR
    ui_elements['MAX_WORKERS'] = MAX_WORKERS
    
    # Dictionary to hold variables in the main scope
    main_scope = {'prg_obj1': prg_obj1, 'prg_obj2': prg_obj2} 
    
    # Connect signals to the functions
    display_trips1_checkbox_button = ui_display_elements['display_trips1_checkbox']
    display_trips2_checkbox_button = ui_display_elements['display_trips2_checkbox']
    display_carpose_checkbox_button = ui_display_elements['display_carpose_checkbox']
    
    connect_signals(run_button, load_button1,load_button2, update_plot_button, save_button, ui_elements,
                    main_scope, ui_display_elements, display_trips1_checkbox_button, display_trips2_checkbox_button, display_carpose_checkbox_button)

    # Show the main window
    main_win.show()
    app.exec()
    
    # Access the calculated result after the event loop
    calculated_result = main_scope.get('calculated_result')
    if calculated_result is not None:
        print("Calculated Result:", calculated_result)


# Start the Qt event loop
if __name__ == '__main__':
    main()
    # pg.exec()
