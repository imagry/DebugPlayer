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
    
# Global settings
cpu_num = multiprocessing.cpu_count() 
MAX_WORKERS = np.floor(cpu_num * 0.8)
# set CAHCE_DIR to the cache directory in personal-folder by appending 'personal-folder' to os.dir_name 0f parent_dir
CACHE_DIR = os.path.join(os.path.dirname(parent_dir), "personal-folder", "cache")
caching_mode_enabled = True

# GUI - Set up the application and main window
app = pg.mkQApp("Path Regression Analysis")

# Create the main window widget and UI elements
main_win, run_button, load_button, update_plot_button, save_button, ui_elements = create_main_window()

# Data Handling
trip_path = parse_arguments()
PathObj, df_car_pose = load_data(trip_path, caching_mode_enabled, CACHE_DIR)

# Path Regressor
delta_t_sec = float(ui_elements['delta_t_input'].text())
pts_before_val = ui_elements['pts_before_spin'].value()
pts_after_val = ui_elements['pts_after_spin'].value()
prg_obj = PathRegressor(PathObj, df_car_pose, CACHE_DIR, delta_t_sec, pts_before_val, pts_after_val, max_workers=MAX_WORKERS)

# Connect signals to the functions
connect_signals(run_button, load_button, update_plot_button, save_button, prg_obj, ui_elements)

# Show the main window
main_win.show()

# Start the Qt event loop
if __name__ == '__main__':
    pg.exec()

