# main_analysis_manager.py

import argparse
# %% Import libraries
import os
import sys
import pyqtgraph as pg

from pyqtgraph.Qt import QtCore, QtWidgets
import pandas as pd
import numpy as np
# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
from init_utils import initialize_environment
# Initialize the environment
initialize_environment()
import data_preparation as dp 
import utils.plot_helpers as plt_helper
from DataClasses.PathTrajectory_pandas import PathTrajectory
from typing import TypeAlias

# Custom type alias for DataFrame with specific columns
PathDataFrame: TypeAlias = pd.DataFrame

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

def load_data(trip_path):         
    '''Run the path regression analysis'''
    # Load the data    
    PathObj = dp.prepare_path_data(trip_path, interpolation=False) 
    df_car_pose = dp.prepare_car_pose_data(trip_path, interpolation=False)     
    return PathObj, df_car_pose

def extract_path_points_at_timestamp(path: PathDataFrame, timestamp: float, speed: float, delta_t_sec: float = 0.1, pts_before: int = 0, pts_after: int = 0):
    """
    Extract path points at a specific timestamp.

    Args:
        path (pd.DataFrame): A DataFrame with columns 'timestamp', 'path_x_data', 'path_y_data'.
        timestamp (float): The timestamp at which to extract the path points.
        speed (float): The speed at the timestamp.

    Returns:
        pd.DataFrame: A DataFrame with the extracted path points.

    Algorithm Description:
        Based on delta_t_sec*v you find the midpoint that is closest to that arc_length distance, and then create a vector of path points from the indexes [mid_point_index - pts_before, mid_point_index, mid_point_index+pts_after].
    """
    # Ensure the DataFrame has the expected columns
    if not all(col in path.columns for col in ["timestamp", "path_x_data", "path_y_data"]):
        raise ValueError("DataFrame must contain 'timestamp', 'path_x_data', and 'path_y_data' columns")

    # Extract the path at the given timestamp
    path_at_timestamp = path[path['timestamp'] == timestamp]
    if path_at_timestamp.empty:
        raise ValueError(f"No path data available for timestamp {timestamp}")

    # Get the path points
    x_data = path_at_timestamp['path_x_data'].values[0]
    y_data = path_at_timestamp['path_y_data'].values[0]

    # Convert to numpy arrays
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    # Compute cumulative distances along the path
    distances = np.sqrt(np.diff(x_data)**2 + np.diff(y_data)**2)
    cumulative_distances = np.insert(np.cumsum(distances), 0, 0)

    # Compute delta_s
    delta_s = delta_t_sec * speed

    # Find the index where cumulative distance is closest to delta_s
    mid_point_index = np.argmin(np.abs(cumulative_distances - delta_s))

    # Collect points from mid_point_index - pts_before to mid_point_index + pts_after
    start_index = max(mid_point_index - pts_before, 0)
    end_index = min(mid_point_index + pts_after + 1, len(x_data))

    extracted_x = x_data[start_index:end_index]
    extracted_y = y_data[start_index:end_index]

    # Return as DataFrame
    extracted_points = pd.DataFrame({'x': extracted_x, 'y': extracted_y})

    return extracted_points

def extract_virtual_path(path: PathTrajectory, df_car_pose: pd.DataFrame, delta_t_sec: float = 0.1, pts_before: int = 0, pts_after: int = 0):
    """ 
    Go over the entire trip, for example, enumerating by timestamps, at each timestamp, obtain the relevant path, look at what the speed at that timepoint, and then extract the path points at that timepoint. Use the function extract_path_points_at_timestamp to extract path points for each timestamp in the path.

    Returns:
        pd.DataFrame df_virt_path: A DataFrame with the extracted path points per time stamp.
        np.array v_p: A Nx18 array of all the collected points concatenated, such that v_p[:,0] is the x coordinate, v_p[:,1] is the y coordinate, v_p[:,2] is an index to the timestamp, v_p[:,3] is the timestamp, v_p[:,4] is the speed at that timepoint, v_p[:,5] is the yaw angle at that timepoint, v_p[:,6] is the curvature at that timepoint, v_p[:,7] is the acceleration at that timepoint, v_p[:,8] is the jerk at that timepoint, v_p[:,9] is the longitudinal jerk at that timepoint, v_p[:,10] is the lateral jerk at that timepoint, v_p[:,11] is the longitudinal acceleration at that timepoint, v_p[:,12] is the lateral acceleration at that timepoint, v_p[:,13] is the longitudinal velocity at that timepoint, v_p[:,14] is the lateral velocity at that timepoint, v_p[:,15] is the longitudinal position at that timepoint, v_p[:,16] is the lateral position at that timepoint, v_p[:,17] is the longitudinal velocity at that timepoint.
    """
    import numpy as np

    # Initialize lists to collect data
    v_p_list = []
    df_virt_path_list = []

    # Get all timestamps from df_car_pose
    timestamps = df_car_pose['timestamp'].unique()

    # Loop over each timestamp
    for idx, timestamp in enumerate(timestamps):
        # Get speed and other parameters at the timestamp
        car_pose_row = df_car_pose[df_car_pose['timestamp'] == timestamp]
        if car_pose_row.empty:
            continue
        speed = car_pose_row['speed'].values[0]  # Assuming 'speed' column exists

        # Extract path points at the timestamp
        extracted_points = extract_path_points_at_timestamp(path, timestamp, speed, delta_t_sec, pts_before, pts_after)
        if extracted_points.empty:
            continue

        # Collect data for v_p
        for i in range(len(extracted_points)):
            x = extracted_points.iloc[i]['x']
            y = extracted_points.iloc[i]['y']
            # Collect other data (some of these might not be directly available)
            yaw_angle = car_pose_row['yaw_angle'].values[0] if 'yaw_angle' in car_pose_row.columns else np.nan
            curvature = car_pose_row['curvature'].values[0] if 'curvature' in car_pose_row.columns else np.nan
            acceleration = car_pose_row['acceleration'].values[0] if 'acceleration' in car_pose_row.columns else np.nan
            jerk = car_pose_row['jerk'].values[0] if 'jerk' in car_pose_row.columns else np.nan
            # ... and so on for other quantities

            v_p_entry = [
                x, y, idx, timestamp, speed, yaw_angle, curvature, acceleration,
                jerk,  # jerk
                np.nan,  # longitudinal jerk
                np.nan,  # lateral jerk
                np.nan,  # longitudinal acceleration
                np.nan,  # lateral acceleration
                np.nan,  # longitudinal velocity
                np.nan,  # lateral velocity
                np.nan,  # longitudinal position
                np.nan,  # lateral position
                np.nan,  # longitudinal velocity (again?)
            ]
            v_p_list.append(v_p_entry)

        # Add timestamp index to extracted_points
        extracted_points['timestamp_idx'] = idx
        extracted_points['timestamp'] = timestamp
        df_virt_path_list.append(extracted_points)

    # Convert lists to DataFrame and array
    df_virt_path = pd.concat(df_virt_path_list, ignore_index=True)
    v_p = np.array(v_p_list)

    return df_virt_path, v_p

# Set pyqtgraph GUI environment
app = pg.mkQApp("Path Regression Analysis")
win = pg.GraphicsLayoutWidget(show=True, title="2D Trajectory Plot")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: 2D Trajectory Plot')

# Add buttons and controls
layout = QtWidgets.QGridLayout()
widget = QtWidgets.QWidget()
widget.setLayout(layout)
win.addItem(widget)

# Controls for delta_t_sec
delta_t_label = QtWidgets.QLabel('delta_t_sec:')
delta_t_input = QtWidgets.QLineEdit('0.1')
layout.addWidget(delta_t_label, 0, 0)
layout.addWidget(delta_t_input, 0, 1)

# Controls for pts_before
pts_before_label = QtWidgets.QLabel('pts_before:')
pts_before_spin = QtWidgets.QSpinBox()
pts_before_spin.setRange(0, 100)
pts_before_spin.setValue(0)
layout.addWidget(pts_before_label, 1, 0)
layout.addWidget(pts_before_spin, 1, 1)

# Controls for pts_after
pts_after_label = QtWidgets.QLabel('pts_after:')
pts_after_spin = QtWidgets.QSpinBox()
pts_after_spin.setRange(0, 100)
pts_after_spin.setValue(0)
layout.addWidget(pts_after_label, 2, 0)
layout.addWidget(pts_after_spin, 2, 1)

# File load button
load_button = QtWidgets.QPushButton('Load Trip Path')
layout.addWidget(load_button, 3, 0)

# Save figure button
save_button = QtWidgets.QPushButton('Save Figure')
layout.addWidget(save_button, 3, 1)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
plt = win.addPlot(title="Parametric, grid enabled")

# Data Handling
# Parse the command-line arguments
trip_path = parse_arguments()
PathObj, df_car_pose = load_data(trip_path)
# Create a figure and axis and plot in it the trajectory of the car
cp_x = df_car_pose['cp_x']
cp_y = df_car_pose['cp_y']

# Plot Trajectory: Plot the entire path with line and markers that shows the data points
plt.plot(cp_x, cp_y, pen=pg.mkPen('b', width=2), symbol='o', symbolBrush='b')

# Evaluate extract_virtual_path function and plot the results
delta_t_sec = float(delta_t_input.text())
pts_before = pts_before_spin.value()
pts_after = pts_after_spin.value()

df_virt_path, v_p = extract_virtual_path(PathObj, df_car_pose, delta_t_sec, pts_before, pts_after)

# Virtual path plot (v_p): plot on the same figure with the car pose trajectory drawn
# Use different colors per the indexes of v_p[:,2] to show the path points extracted at each timepoint
if v_p.size > 0:
    x_vp = v_p[:,0]
    y_vp = v_p[:,1]
    timestamp_idxs = v_p[:,2]

    # Create a color map
    unique_idxs = np.unique(timestamp_idxs)
    colors = plt_helper.get_color_list(len(unique_idxs))

    for idx, color in zip(unique_idxs, colors):
        mask = timestamp_idxs == idx
        plt.plot(x_vp[mask], y_vp[mask], pen=None, symbol='o', symbolBrush=color)

# Function to update the plot when controls change
def update_plot():
    plt.clear()
    # Re-plot the car pose trajectory
    plt.plot(cp_x, cp_y, pen=pg.mkPen('b', width=2), symbol='o', symbolBrush='b')

    # Get updated values
    delta_t_sec = float(delta_t_input.text())
    pts_before = pts_before_spin.value()
    pts_after = pts_after_spin.value()

    # Recalculate virtual path
    df_virt_path, v_p = extract_virtual_path(PathObj, df_car_pose, delta_t_sec, pts_before, pts_after)

    # Re-plot virtual path points
    if v_p.size > 0:
        x_vp = v_p[:,0]
        y_vp = v_p[:,1]
        timestamp_idxs = v_p[:,2]

        unique_idxs = np.unique(timestamp_idxs)
        colors = plt_helper.get_color_list(len(unique_idxs))

        for idx, color in zip(unique_idxs, colors):
            mask = timestamp_idxs == idx
            plt.plot(x_vp[mask], y_vp[mask], pen=None, symbol='o', symbolBrush=color)

# Connect signals to update the plot
delta_t_input.editingFinished.connect(update_plot)
pts_before_spin.valueChanged.connect(update_plot)
pts_after_spin.valueChanged.connect(update_plot)

# Function to handle file loading
def load_trip_path():
    global trip_path, PathObj, df_car_pose, cp_x, cp_y
    file_dialog = QtWidgets.QFileDialog()
    trip_path, _ = file_dialog.getOpenFileName(None, 'Open Trip File', '', 'Trip Files (*.trip)')
    if trip_path:
        PathObj, df_car_pose = load_data(trip_path)
        cp_x = df_car_pose['cp_x']
        cp_y = df_car_pose['cp_y']
        update_plot()

load_button.clicked.connect(load_trip_path)

# Function to save the figure
def save_figure():
    exporter = pg.exporters.ImageExporter(plt.plotItem)
    exporter.parameters()['width'] = 1000   # (optional) set export width
    exporter.export('trajectory_plot.png')

save_button.clicked.connect(save_figure)

# Start the Qt event loop
if __name__ == '__main__':       
    pg.exec()




















# # main_analysis_manager.py

# # TBD: Go over all TBG, validate and remove
# # TBG = To be Filled by ChatGPT

# import argparse
# # %% Import libraries
# import os
# import sys
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore
# import pandas as pd
# # Adjust the path to import init_utils
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.insert(0, parent_dir)
# from init_utils import initialize_environment
# # Initialize the environment
# initialize_environment()
# import data_preparation as dp 
# import utils.plot_helpers as plt_helper
# from DataClasses.PathTrajectory_pandas import PathTrajectory
# from typing import TypeAlias


# # Custom type alias for DataFrame with specific columns
# PathDataFrame: TypeAlias = pd.DataFrame

# def parse_arguments():
#     # Create an argument parser
#     parser = argparse.ArgumentParser(description="Main Analysis Manager")    
#     # Add the --trip argument
#     parser.add_argument('--trip', type=str, help='Path to the trip file')    
#     # Parse the command-line arguments
#     args = parser.parse_args()    
#     # Check if the --trip flag is provided
#     if args.trip:
#         return args.trip   
#     else:
#         raise ValueError("Please provide the path to the trip file using the --trip flag")
            

# def load_data(trip_path):         
#     '''Run the path regression analysis'''
#     # # Load the data    
#     PathObj = dp.prepare_path_data(trip_path, interpolation=False) 
#     df_car_pose = dp.prepare_car_pose_data(trip_path, interpolation=False)     
    
#     return PathObj, df_car_pose

   
# def extract_path_points_at_timestamp(path: PathDataFrame, timestamp: float, delta_t_sec: float = 0.1, pts_before: int = 0, pts_after: int = 0):
#     """
#     Extract path points at a specific timestamp.

#     Args:
#         path (pd.DataFrame): A DataFrame with columns 'path_x_data' and 'path_y_data'.
#         timestamp (float): The timestamp at which to extract the path points.

#     Returns:
#         pd.DataFrame: A DataFrame with the extracted path points.
    
#     Algorithm Description:
#         Based on delta_t_sec*v you find the midpoint that is closest to that arc_length distance, and then create a vector of path poitns form the indexes [mid_point_index - pts_before, mid_point_index, mid_point_index+pts_after].
    
#     """
#     # Ensure the DataFrame has the expected columns
#     if not all(col in path.columns for col in ["path_x_data", "path_y_data"]):
#         raise ValueError("DataFrame must contain 'path_x_data' and 'path_y_data' columns")

#     # Your function implementation here
#     # # For example, filter the DataFrame based on the timestamp
#     # extracted_points = path[path['timestamp'] == timestamp]
#     TBG - Implement the function to extract path points at a specific timestamp

#     return extracted_points

# def extract_virtual_path(path: PathTrajectory, delta_t_sec: float = 0.1, pts_before: int = 0, pts_after: int = 0, TBG - additional inputs):
#     """ Go over the entire trip, for example, enumerating by timestamps, at each time stamp, obtain the relevant path, look at what the speed at that timepoint, and then extract the path points at that timepoint. Use the function extract_path_points_at_timestamp to extract path points for each timestamp in the path.
#     Returns:
#         pd.DataFrame df_virt_path: A DataFrame with the extracted path points per time stamp.
#         np.array v_p: A Nx18 array of all the coolected points concatenated, such that v_p[:,0] is the x coordinate, v_p[:,1] is the y coordinate, v_p[:,2] is an index to the timestamp, v_p[:,3] is the timestamp, v_p[:,4] is the speed at that timepoint, v_p[:,5] is the yaw angle at that timepoint, v_p[:,6] is the curvature at that timepoint, v_p[:,7] is the acceleration at that timepoint, v_p[:,8] is the jerk at that timepoint, v_p[:,9] is the longitudinal jerk at that timepoint, v_p[:,10] is the lateral jerk at that timepoint, v_p[:,11] is the longitudinal acceleration at that timepoint, v_p[:,12] is the lateral acceleration at that timepoint, v_p[:,13] is the longitudinal velocity at that timepoint, v_p[:,14] is the lateral velocity at that timepoint, v_p[:,15] is the longitudinal position at that timepoint, v_p[:,16] is the lateral position at that timepoint, v_p[:,17] is the longitudinal velocity at that timepoint. 
        
#     """
#     TBG - Implement the function here

# # Set pgqt gui envrionment
# app = pg.mkQApp("Path Regression Analysis")
# win = pg.GraphicsLayoutWidget(show=True, title="2D Trajectory Plot")
# win.resize(1000,600)
# win.setWindowTitle('pyqtgraph example: 2D Trajectory Plot')

# Add Buttons to support:
#     delta_t_sec - free text (float)
#     pts_before - up-down in [0, max_off_set_pots]- integer 
#     pts_after -  up-down in [0, max_off_set_pots]- integer 
#     File - load trip_path
#     Save - save current figure as jpg  
    

# # Enable antialiasing for prettier plots
# pg.setConfigOptions(antialias=True)
# plt = win.addPlot(title="Parametric, grid enabled")

# # Data Handling
# # Parse the command-line arguments
# trip_path = parse_arguments()
# PathObj, df_car_pose = load_data(trip_path)
# # Create a figure and axis and plot in it the trajectory of the car
# cp_x = df_car_pose['cp_x']
# cp_y = df_car_pose['cp_y']


# # Plot the entire car pose trajectory with line and markers that shows the data poitns
# TBG - Plot Trajectory: Plot the entire path with line and markers that shows the data poitns


# TBG - Evaluate extract_virtual_path function and plot the results

# TBG - virtual path plot (v_p):  plot on the same figure with the car pose trajectory drawn. Use different colors per the indexes of v_p[:,2] to show the path points extracted at each timepoint.

# On buttons chaneg - reevaluate v_p and update the plot

# # Start the Qt event loop
# if __name__ == '__main__':       
#     pg.exec()
    
    