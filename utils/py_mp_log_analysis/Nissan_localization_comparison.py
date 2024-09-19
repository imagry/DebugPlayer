#%% Import libraries
import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import socket
from matplotlib.widgets import Cursor
import mplcursors
import os
import webbrowser
import sys
import Localization_Utils.utils_LinearAlgebra as la
# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

import Data_Loader.utils_trip_data_handler as dh
import Steering_Analysis_Utils as sa_utils
import Localization_Utils.utils_geo as geo
from Data_Loader.path_loader import *
from py_utils.plot_helpers import my_plotter

# %% Print settings
pring_trip_map = 0

# %% Load data
machine_name = socket.gethostname()
if machine_name == 'thamam-XPS-8940':
    trips_dir = '/home/thamam/data/trips/'
else:
    trips_dir = '/home/thh3/data/trips/Nissan/'    

Nissan_odometry_folder = '/home/thh3/data/trips/Nissan/odometry_20240802/'

# Retrieve Trip name
# trip_name = 'trip_tau_0p5' 
# trip_name = 'trip_N2_60' 
trip_name = 'trip_default'

config_path = 'Data_Loader/trips_config.yaml'
trip_string = dh.get_trip_string(config_path, trip_name)
trip_name = trip_string
trip_path = trips_dir + trip_name
data_ds_factor = 1


# %%load gps and imu data from trip
X_gps_lng_lat, df_xyz_NED = dh.load_trip_gps_data(trip_path,coordinates_type="both", tangent_frame = "NED")


if pring_trip_map:
    # Plot on map 
    trip_latlong = np.fliplr(X_gps_lng_lat[0:2,:].T)
    map_name= 'map_' + trip_name
    m, map_nampe = geo.trip_view_on_map(trip_latlong,map_name)
    webbrowser.open_new_tab(map_nampe)
    
#%% Compose Poses
df_xyz = df_xyz_NED
df_imu = read_nissan_imu_data(trip_path)
yaw_deg = np.asarray(df_imu['yaw'])
ego_yaw_rad = np.deg2rad(yaw_deg)
t_ego_imu = np.asarray(df_imu['time_stamp'])
# %

ego_x = np.asanyarray(df_xyz['x'])
ego_y = np.asanyarray(df_xyz['y'])
t_ego_gps = np.asanyarray(df_xyz['time_stamp'])

# truncate t_ego if needed to align with the timesatmp of the imu data
# gps_imu_overlapping_inds = np.asanyarray([(t_ego_gps >= t_ego_imu[0]) & (t_ego_gps <= t_ego_imu[-1])]).squeeze()
# truncate t_ego if needed to align with the timesatmp of the imu data
# gps_imu_overlapping_inds = np.asanyarray([(t_ego_gps >= t_ego_imu[0]) & (t_ego_gps <= t_ego_imu[-1])]).squeeze()
# imu_gps_overlapping_inds = np.asanyarray([(t_ego_imu >= t_ego_gps[0]) & (t_ego_imu <= t_ego_gps[-1])]).squeeze()

ego_t = t_ego_gps
if t_ego_imu[0] < t_ego_gps[0]:
    ego_t = t_ego_gps[(t_ego_gps >= t_ego_imu[0])]
    ego_x = ego_x[(t_ego_gps >= t_ego_imu[0])]
    ego_y = ego_y[(t_ego_gps >= t_ego_imu[0])]
    ego_yaw_rad = ego_yaw_rad[(t_ego_gps >= t_ego_imu[0])]
    
if t_ego_imu[-1] > t_ego_gps[-1]:
    ego_t = ego_t[(ego_t <= t_ego_imu[-1])]
    ego_x = ego_x[(t_ego_gps <= t_ego_imu[-1])]
    ego_y = ego_y[(t_ego_gps <= t_ego_imu[-1])]
    ego_yaw_rad = ego_yaw_rad[(t_ego_gps <= t_ego_imu[-1])]
    
# convert time stamp to Nissan's format
t_ego_ms_nissan = (ego_t * 1e3) % 2**32

transform_from_CFA_to_COG=True
# if needed compose the se2 that translates from CFA to COG (pure trnaslation in this case)
if transform_from_CFA_to_COG:
    delta_x = 1.299
    delta_y = 0.0
    delta_yaw = 0.0
    T_CFA_to_COG = SE2(delta_x, delta_y, delta_yaw)
        
ego_taj = np.vstack((np.asarray(ego_x),np.asarray(ego_y))).T

# %% Load Nissan data

# retrieve all files names in Nissan odometry folder
nissan_files = os.listdir(Nissan_odometry_folder)

# sort nissan_files alphabetically
nissan_files.sort()

# go over each file in Nissan odometry folder and load the data and compare time frame with that of t_ego to find the corresponding data
# The timestamp included in the CSV is (original timestamp [milliseconds])%2^32. 
# For example, when original puth_pub.timestamp = 1722579623330[milliseconds], the timestamp included in CSV is 1722579623330 % 2^32 =  297737634 

file_found = 0

for file in nissan_files:
    
    if file_found == 1:
        break
    
    # if file has lock, skip it
    if 'lock' in file:
        continue
    
    nissan_data = sa_utils.load_data(Nissan_odometry_folder + file)
    
    Nissan_odometery_file_Header = {'controller_time', 'path_pub_timestamp', 'odometry_x', 'odometry_y', 'odometry_rz', 'SteeringWheelAngle_Req', 'SteeringWheelAngle', 'vehicle_speed'}  # 'odometry_rz' is the yaw angle --- rate of rotation around z-axis
    Header_units = {'controller_time': 's', 'path_pub_timestamp': 'ms', 'odometry_x': 'm', 'odometry_y': 'm', 'odometry_rz': 'deg', 'SteeringWheelAngle_Req': 'rad', 'SteeringWheelAngle': 'rad', 'vehicle_speed': 'm/s'}
    
    # convert Nissan's timestamp to our timestamp
    # nissan_data['path_pub_timestamp'] = nissan_data['path_pub_timestamp'] % 2**32
    nissan_time = nissan_data['path_pub_timestamp'].values
    
    # check if nissan_time has significant overlap t_ego_ms_nissan 
    if (nissan_time[-1] < t_ego_ms_nissan[0]) or (nissan_time[0] > t_ego_ms_nissan[-1]) :
        continue # No overlap    
       
    Nissan_selected_file = file
    
    file_found = 1
    
# %% Extract relevant columns from nissan data: steering command, steering angle, and vehicle speed, and x y and yaw
nissan_steering_cmd = nissan_data['SteeringWheelAngle_Req'].values
nissan_steering = nissan_data['SteeringWheelAngle'].values
nissan_speed = nissan_data['vehicle_speed'].values
nissan_pos_x = nissan_data['odometry_x'].values
nissan_pos_y = nissan_data['odometry_y'].values
nissan_yaw_deg = nissan_data['odometry_rz'].values
nissan_yaw_rad = np.deg2rad(nissan_yaw_deg)

# restrict t_ego_ms_nissan to the time frame of nissan data
time_overlapping_ind = np.asanyarray([(t_ego_ms_nissan >= nissan_time[0]) & (t_ego_ms_nissan <= nissan_time[-1])]).squeeze()
#%%
t_ego_ms_nissan = t_ego_ms_nissan[time_overlapping_ind]
ego_x = ego_x[time_overlapping_ind]
ego_y = ego_y[time_overlapping_ind]
ego_yaw_rad = ego_yaw_rad[time_overlapping_ind]
t_ego_imu = t_ego_imu[time_overlapping_ind]
ego_taj = ego_taj[time_overlapping_ind]

# %% Interpolate data

nissan_interp_x = sa_utils.interpolate_time_series(nissan_time, nissan_pos_x, t_ego_ms_nissan)
nissan_interp_y = sa_utils.interpolate_time_series(nissan_time, nissan_pos_y, t_ego_ms_nissan)
nissan_interp_yaw = sa_utils.interpolate_time_series(nissan_time, nissan_yaw_rad, t_ego_ms_nissan)

# nissan_steering_cmd_interp = sa_utils.interpolate_time_series(nissan_time, nissan_steering_cmd, t_ego_ms_nissan)
# nissan_steering_interp = sa_utils.interpolate_time_series(nissan_time, nissan_steering, t_ego_ms_nissan)
# nissan_speed_interp = sa_utils.interpolate_time_series(nissan_time, nissan_speed, t_ego_ms_nissan)

# synchornize the coordinate system of nissan with that of ego by applying procrustes transformation
# nissan_pos_x_interp_to_imagry_time, nissan_pos_y_interp_to_imagry_time = la.procurustes_tranasformation(ego_taj.T, np.vstack((nissan_pos_x_interp_to_imagry_time, nissan_pos_y_interp_to_imagry_time)))

# Align Nissan trajectory with that of ego trajectory by requiring the starting point of both to be the same and with the same yaw - i.e. apply SE2 transformation to nissan trajectory
# find the transformation that aligns the starting point of both trajectories
delta_x = nissan_interp_x[0] - ego_x[0]
delta_y = nissan_interp_y[0] - ego_y[0]
delta_yaw = nissan_interp_yaw[0] - ego_yaw_rad[0]

T_ego_2_nis = SE2(delta_x, delta_y, delta_yaw)
#  Apply the transformation to nissan trajectory
# arrange Nissan_pose_x_interp_to_imagry_time into a 

    # Create SE(2) matrices
Nissan_Pose_SE2 = []
for x, y, theta in zip(nissan_interp_x, nissan_interp_y, nissan_interp_yaw):
    SE2_matrix = np.array([
        [np.cos(theta), -np.sin(theta), x],
        [np.sin(theta), np.cos(theta), y],
        [0, 0, 1]
    ])
    Nissan_Pose_SE2.append(SE2_matrix)

Nissan_Pose_SE2_aligned = np.asarray(apply_se2_transform_to_series(T_ego_2_nis.A, Nissan_Pose_SE2))

#Extract x, y, and yaw from the aligned Nissan Pose
nissan_pos_x_aligned = Nissan_Pose_SE2_aligned[:,0,2]   
nissan_pos_y_aligned = Nissan_Pose_SE2_aligned[:,1,2]
nissan_yaw_aligned = np.arctan2(Nissan_Pose_SE2_aligned[:,1,0], Nissan_Pose_SE2_aligned[:,0,0]) 




# %% Plot the ego poistion of both on map without interpolation
# Plot the ego poistion of both on map without interpolation
plot_ego = 1    
if plot_ego:
    with plt.ioff():
        fig, (ax1) = plt.subplots(1, 1, figsize=(5, 2.7))
        my_plotter(ax1, ego_x, ego_y, {'color':'orange', 'linewidth':1, 'linestyle':'--','label':'ego'})
        my_plotter(ax1, nissan_pos_x_aligned, nissan_pos_y_aligned, {'color':'blue', 'linewidth':1, 'linestyle':'--','label':'nissan'})
        ax1.set_title('EgoPlot')
        ax1.set_aspect('equal', 'box')
    pan_handler = panhandler(fig)       
    plt.show()
    
def plot_se2_path(x_ego, y_ego, yaw):
    """
    Plots a series of oriented poses based on x, y, and yaw values.

    Parameters:
    x_ego (list of float): List of x coordinates.
    y_ego (list of float): List of y coordinates.
    yaw (list of float): List of yaw angles in degrees.
    """
    def draw_pose(ax, se2, length=0.5, **kwargs):
        """
        Draw a single SE(2) pose on the given axes.

        Parameters:
        ax (matplotlib.axes._axes.Axes): The axes on which to draw.
        se2 (SE2): The SE(2) transformation.
        length (float): Length of the coordinate axes to draw.
        kwargs: Additional keyword arguments for the plot.
        """
        
        
        origin = se2.t
        angle = se2.theta()
        trplot2( transl2(origin[0], origin[1])@trot2(angle),length = 3, width=1,rviz=True)        

    # Convert yaw angles from degrees to radians
    yaw_rad = np.deg2rad(yaw)

    # Set up the plot
    fig, ax = plt.subplots()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')

    # Plot the series of oriented poses
    for x, y, theta in zip(x_ego, y_ego, yaw_rad):
        se2_matrix = SE2(x, y, theta)
        draw_pose(ax, se2_matrix, length=0.5)
    
    # Plot the path
    plot_path = True
    if plot_path:
        path = np.array([[x, y] for x, y in zip(x_ego, y_ego)])
        ax.plot(path[:, 0], path[:, 1], 'k--', label='Path')

    plt.legend()
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Series of Oriented Poses')
    plt.show()