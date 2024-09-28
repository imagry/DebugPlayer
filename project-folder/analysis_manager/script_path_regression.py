# script_path_regression.py
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
from DataClasses.PathTrajectory_pandas import PathTrajectory
from typing import TypeAlias
from DataClasses.PathRegressor import PathRegressor        
from pathreg_utils import get_color_list, parse_arguments, load_data, prepare_plot_data

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

### Subsection for plot settings
plot_settings_label = QtWidgets.QLabel('Plot Settings')
plot_settings_label.setStyleSheet("font-weight: bold;")
controls_layout.addWidget(plot_settings_label)

# Controls for line width
line_width_label = QtWidgets.QLabel('Line Width:')
line_width_spin = QtWidgets.QSpinBox()
line_width_spin.setRange(1, 10)
line_width_spin.setValue(1)
controls_layout.addWidget(line_width_label)
controls_layout.addWidget(line_width_spin)

# Controls for marker size
marker_size_label = QtWidgets.QLabel('Marker Size:')
marker_size_spin = QtWidgets.QSpinBox()
marker_size_spin.setRange(1, 20)
marker_size_spin.setValue(5)
controls_layout.addWidget(marker_size_label)
controls_layout.addWidget(marker_size_spin)

# Controls for colors_num
colors_num_label = QtWidgets.QLabel('colors_num:')
colors_num_spin = QtWidgets.QSpinBox()
colors_num_spin.setRange(1, 8)
colors_num_spin.setValue(1)
controls_layout.addWidget(colors_num_label)
controls_layout.addWidget(colors_num_spin)

# Add option to choose colors in the palette per the number of colors selected
colors_palette_label = QtWidgets.QLabel('Colors Palette:')
colors_palette_list = QtWidgets.QListWidget()
colors_palette_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
colors_palette_list.addItems(['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
controls_layout.addWidget(colors_palette_label)
controls_layout.addWidget(colors_palette_list)

# Add button to update the plot 
update_plot_button = QtWidgets.QPushButton('Update Plot')
controls_layout.addWidget(update_plot_button)


# # Add spacer to push widgets to the top
controls_layout.addStretch()


### Subsection for virtual path extraction
virtual_path_label = QtWidgets.QLabel('Virtual Path Extraction')
virtual_path_label.setStyleSheet("font-weight: bold;")
controls_layout.addWidget(virtual_path_label)

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

# Run button
run_button = QtWidgets.QPushButton('Run')
controls_layout.addWidget(run_button)

# # Add spacer to push widgets to the top
controls_layout.addStretch()

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

# Set stretch factors to make the plot larger
h_layout.setStretchFactor(controls_layout, 1)
h_layout.setStretchFactor(plt, 4)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Data Handling
# Parse the command-line arguments
trip_path = parse_arguments()
PathObj, df_car_pose = load_data(trip_path, cachine_mode_enabled, CACHE_DIR)

# Evaluate extract_virtual_path function and plot the results
delta_t_sec_val = float(delta_t_input.text())
pts_before_val = pts_before_spin.value()
pts_after_val = pts_after_spin.value()
 
prg_obj = PathRegressor(PathObj, df_car_pose, CACHE_DIR, delta_t_sec_val, pts_before_val, pts_after_val,max_workers= MAX_WORKERS)


def plot_path_with_colors(x, y, colors_num = 1, pallet = {'r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'}, line_width = 1, marker_size = 5):
    """
    Plot the path with separating colors according to the number of colors selected.
    E.g., assume that the path is comprised by selecting two points from each timestamp: path = [A A, B, B, C C, D D ...]
    then if we chose colors_num = 2, then the first 2 colors from the pallet will be used to color the points A, C, E, ... in once color and B, D, F, ... in another color.         
    """
    # Create a color map
    if colors_num > 1:
        colors = get_color_list(colors_num)
    
    if colors_num > len(pallet):
        colors_num = len(pallet)
        print(f"Number of colors exceeds the pallet size. Using {colors_num} colors.")        
    
    colors = list(pallet)[:colors_num]

    # prepare list of colors masks according to the number of colors selected.
    # if colors = {'r', 'g', 'b' }, then it follows that 
    # Red Mask: mask[0] = {0,3,6,9, ...}
    # Green Mask: mask[1] = {1,4,7,10, ...}
    # Blue Mask: mask[2] = {2,5,8,11, ...}
    color_masks = []
    for i in range(colors_num):
        mask = np.arange(i, len(x), colors_num)
        color_masks.append(mask)
        plt.plot(x[mask], y[mask], pen=pg.mkPen(width=line_width), symbol='o', symbolSize=marker_size, symbolBrush=colors[i])
                  
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
        
def reset():
    # Reset the plot and settings to their default values
    global PathObj, df_car_pose, cp_x, cp_y
    PathObj = None
    df_car_pose = None
    cp_x = None
    cp_y = None
    plt.clear()


def calculate_virtual_path():
    # Get updated values
    delta_t_sec_val = float(delta_t_input.text())
    pts_before_val = pts_before_spin.value()
    pts_after_val = pts_after_spin.value()
    colors_num = colors_num_spin.value()
    
    # Update the PathRegressor object
    params_dict = {'delta_t_sec': delta_t_sec_val, 'pts_before': pts_before_val, 'pts_after': pts_after_val}
    prg_obj.update_params(params_dict)
    prg_obj.eval()
    
    # Recalculate virtual path
    v_p = prg_obj.get_virtual_path()

    update_plot()      
                        
# Function to update the plot when controls change
def update_plot():
    plt.clear()
    # Re-plot the car pose trajectory
    plt.plot(df_car_pose['cp_x'], df_car_pose['cp_y'], pen=pg.mkPen(width=1), symbol='star', symbolBrush='b')

    # Get plot settings 
    line_width = line_width_spin.value()
    marker_size = marker_size_spin.value()
    colors_num = colors_num_spin.value()    
    palette = [item.text() for item in colors_palette_list.selectedItems()]
    if len(palette) == 0:
        palette = {'r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'}
        
    # Recalculate virtual path
    df_virt_path, v_p = prg_obj.get_virtual_path()

    if v_p is None: # If the virtual path is not calculated, return
        return
    
    # Re-plot virtual path points
    if v_p.size > 0:
        x_vp = v_p[:,0]
        y_vp = v_p[:,1]
        timestamp_idxs = v_p[:,2]
        
        plot_path_with_colors(x_vp, y_vp, colors_num, palette, line_width, marker_size)

# Function to handle file loading
def load_trip_path():
    global trip_path, PathObj, df_car_pose, cp_x, cp_y
    file_dialog = QtWidgets.QFileDialog()
    file_in_trip_path, _ = file_dialog.getOpenFileName(None, 'Open Trip File', '', 'Trip Files (*.csv)')
    if file_in_trip_path:
        reset()
        trip_dir_path = os.path.dirname(file_in_trip_path)
        PathObj, df_car_pose = load_data(trip_dir_path, cachine_mode_enabled, CACHE_DIR)
        cp_x = df_car_pose['cp_x']
        cp_y = df_car_pose['cp_y']
        update_plot()
        
        
# Connect signals to update the plot
run_button.clicked.connect(calculate_virtual_path)
load_button.clicked.connect(load_trip_path)
update_plot_button.clicked.connect(update_plot)

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
