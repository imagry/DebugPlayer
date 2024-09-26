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

# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
# Ensure the DataClasses directory is in the path
data_classes_dir = os.path.abspath(os.path.join(parent_dir, 'DataClasses'))
sys.path.insert(0, data_classes_dir)
# Ensure the utils directory is in the path
utils_dir = os.path.abspath(os.path.join(parent_dir, 'utils'))
sys.path.insert(0, utils_dir)

import data_preparation as dp 
import utils.plot_helpers as plt_helper
from analysis_manager.DataClasses.PathTrajectory_pandas import PathTrajectory
from typing import TypeAlias
from analysis_manager.DataClasses.PathRegressor import PathRegressor

from pathreg_utils import load_trip_path, get_color_list, parse_arguments, load_data, update_plot, prepare_plot_data

# Global settings
cpu_num = multiprocessing.cpu_count() 
MAX_WORKERS = np.floor(cpu_num * 0.8)
PathDataFrame: TypeAlias = pd.DataFrame
CACHE_DIR = "cache"
cachine_mode_enabled = True  # Set to False to disable caching - Data will always be loaded from the trip file

# GUI - Set up the application and main window
app = pg.mkQApp("Path Regression Analysis")

# Create the main window widget
main_win = QtWidgets.QWidget()
main_layout = QtWidgets.QVBoxLayout()
main_win.setLayout(main_layout)
main_win.setWindowTitle('Path Regression Analysis')
main_win.resize(1000, 600)

# Create a horizontal layout for controls and plot
h_layout = QtWidgets.QHBoxLayout()
main_layout.addLayout(h_layout)

# Create a vertical layout for controls
controls_layout = QtWidgets.QVBoxLayout()
h_layout.addLayout(controls_layout)

# Add buttons and controls
# Controls for delta_t_sec
delta_t_label = QtWidgets.QLabel('delta_t_sec:')
delta_t_input = QtWidgets.QLineEdit('0.1')
controls_layout.addWidget(delta_t_label)
controls_layout.addWidget(delta_t_input)

# Controls for pts_before
pts_before_label = QtWidgets.QLabel('pts_before:')
pts_before_spin = QtWidgets.QSpinBox()
pts_before_spin.setRange(0, 100)
pts_before_spin.setValue(0)
controls_layout.addWidget(pts_before_label)
controls_layout.addWidget(pts_before_spin)

# Controls for pts_after
pts_after_label = QtWidgets.QLabel('pts_after:')
pts_after_spin = QtWidgets.QSpinBox()
pts_after_spin.setRange(0, 100)
pts_after_spin.setValue(0)
controls_layout.addWidget(pts_after_label)
controls_layout.addWidget(pts_after_spin)

# File load button
load_button = QtWidgets.QPushButton('Load Trip Path')
controls_layout.addWidget(load_button)

# Save figure button
save_button = QtWidgets.QPushButton('Save Figure')
controls_layout.addWidget(save_button)

# Add spacer to push widgets to the top
controls_layout.addStretch()

# Create the pyqtgraph plot widget
plt = pg.PlotWidget(title="2D Trajectory Plot")
h_layout.addWidget(plt)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Data Handling
# Parse the command-line arguments
trip_path = parse_arguments()
PathObj, df_car_pose = load_data(trip_path)

# Evaluate extract_virtual_path function and plot the results
delta_t_sec_val = float(delta_t_input.text())
pts_before_val = pts_before_spin.value()
pts_after_val = pts_after_spin.value()
prg_obj = PathRegressor(PathObj, df_car_pose, delta_t_sec_val, pts_before_val, pts_after_val,max_workers= MAX_WORKERS)


# Initial plot
# initial_plot()
def plot_virtual_path_parallel(x_vp, y_vp, timestamp_idxs):
    """
    Parallelized data preparation for plotting and then plotting in the main thread.
    """
    # Create a color map
    unique_idxs = np.unique(timestamp_idxs)
    colors = get_color_list(len(unique_idxs))
    
    # Parallel preparation of plot data
    plot_data = []
    with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers as needed
        futures = [
            executor.submit(prepare_plot_data, idx, timestamp_idxs, x_vp, y_vp, color)
            for idx, color in zip(unique_idxs, colors)
        ]
        
        # Collect the prepared data
        for future in futures:
            plot_data.append(future.result())

    # Plot the data sequentially in the main thread
    for x_data, y_data, color in plot_data:
        plt.plot(x_data, y_data, linestyle='-', marker='o', color=color)
        
        
# Function to update the plot when controls change
def update_plot():
    plt.clear()
    # Re-plot the car pose trajectory
    plt.plot(df_car_pose['cp_x'], df_car_pose['cp_y'], pen=None, symbol='o', symbolBrush='b')

    # Get updated values
    delta_t_sec_val = float(delta_t_input.text())
    pts_before_val = pts_before_spin.value()
    pts_after_val = pts_after_spin.value()

    # Update the PathRegressor object
    prg_obj.update_params(delta_t_sec_val, pts_before_val, pts_after_val)

    # Recalculate virtual path
    df_virt_path, v_p = prg_obj.get_virtual_path()

    # Re-plot virtual path points
    if v_p.size > 0:
        x_vp = v_p[:,0]
        y_vp = v_p[:,1]
        timestamp_idxs = v_p[:,2]
        
        plt.plot(x_vp, y_vp, pen=None, symbol='o', symbolBrush='r')
        # plot_virtual_path_parallel(x_vp, y_vp, timestamp_idxs)

# Connect signals to update the plot
delta_t_input.editingFinished.connect(update_plot)
pts_before_spin.valueChanged.connect(update_plot)
pts_after_spin.valueChanged.connect(update_plot)


load_button.clicked.connect(load_trip_path)


        
# Function to save the figure
def save_figure():
    exporter = pg.exporters.ImageExporter(plt.plotItem)
    exporter.parameters()['width'] = 1000   # (optional) set export width
    exporter.export('trajectory_plot.png')

save_button.clicked.connect(save_figure)

# Show the main window
main_win.show()

# Start the Qt event loop
if __name__ == '__main__':
    pg.exec()




# Todo:
# - Add saving to pickle files 
