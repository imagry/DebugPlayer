#%% Import libraries
import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.path_aux_utils import *
# check if the required packages are installed and install them if not
pre_required_install_check()

import matplotlib
matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'

import matplotlib.pyplot as plt
import numpy as np
import random
from typing import List, Union, Optional
from spatialmath import SE2
from scipy.interpolate import interp1d
from scipy import linalg
import math
import webbrowser
import pandas as pd

# Import custom modules
from utils.aidriver_logs_readers.path_loader import read_nissan_imu_data, read_path_data
import utils.aidriver_logs_readers.utils_trip_data_handler as dh
from utils.se2_function import get_interpolated_pose_SE2, apply_se2_transform
from utils.path_geom_utils import extract_valid_path
from utils.plot_helpers import my_plotter, plot_se2_path
from utils.utils_geo import trip_view_on_map
from path_merger.path_merger_utils import PathMergerOptions, path_merger_wrapper

#%% Path adjustments
def adjust_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.insert(0, parent_dir)


    
#%% Initialize settings and parameters
def initialize_parameters():
    params = {
        'lm1': 0.5,  # smoothing lambda
        'lm2': 0.5,  # derivative constraint lambda
        'w_inc': 4,  # weighing of p2 before i2 (larger value means faster decay)
        'merge_options': PathMergerOptions(lambda_1=0.5, lambda_2=0.5, w=4),
        'N2_meters': 2,  # blending region length in z
        'spline_ds': 0.1,  # spline interpolation step
        'trajectory_new_format': True, # True if the trajectory data is in the new format - path_trajectory.csv, in which all the pose data is included.
        'plot_settings': {
            'print_trip_map': False,
            'plot_poses': False,
            'plot_ego': False,
            'plot_after_merge': False,
        },
        'trip_settings': {
            'Run_alternative_trip': True,
            'alternative_trip_name': '2024-08-26T10_07_43',
            'trip_path': os.environ.get('OFFLINE_DATA_PATH_URBAN'),
            'data_ds_factor': 1,
            'transform_from_CFA_to_COG': False,
        },
        'T_CFA_to_COG': SE2(1.299, 0.0, 0.0),  # Transformation matrix
        'PathAssemblerOptions': {
            'path_start_ind': 0,
            'path_end_ind': 300,
            'delay': 0.35,
            'path_points_skip': 1,
            'path_length_to_eval': 100,
            'frames_skip': 0,
            'refractory_period_sec': 0.5
        },
    }
    return params

def load_path_trajectory_file(trip_path):
    # read data 
    trajectory_filepath =  trip_path +'/'+ 'path_trajectory.csv' 

    # Load path points
    points_num = 300 #number of points recorded per path sample
    df_path_ = pd.read_csv(trajectory_filepath, header=0)
    path_x_index = 11
    path_y_index = path_x_index + points_num
    path_x_indices = np.arange(path_x_index, path_y_index)
    path_y_indices = np.arange(path_y_index, path_y_index + points_num)

    x = df_path_.iloc[:, path_x_indices]
    y = df_path_.iloc[:, path_y_indices]

    # Load data timestamps
    timestamp_ind = 0
    data_timestamps = df_path_.iloc[:, timestamp_ind]
    if data_timestamps[0]>1e11:
        data_timestamps = data_timestamps / 1000

    # Load target speeds
    target_speed_ind = 2
    v = df_path_.iloc[:, target_speed_ind]

    # Load car pose x, y, yaw
    car_pose_now_x_ind = 4
    car_pose_now_y_ind = 5
    car_pose_now_yaw_ind = 6

    car_pose_now_x = df_path_.iloc[:, car_pose_now_x_ind]
    car_pose_now_y = df_path_.iloc[:, car_pose_now_y_ind]
    car_pose_now_yaw = df_path_.iloc[:, car_pose_now_yaw_ind]

    # Load now car pose timestamp
    car_pose_now_timestamp_ind = 7
    car_pose_now_timestamp = df_path_.iloc[:, car_pose_now_timestamp_ind]

    # Load car pose image x, y, yaw
    car_pose_image_x_ind = 8
    car_pose_image_y_ind = 9
    car_pose_image_yaw_ind = 10
    car_pose_image_x = df_path_.iloc[:, car_pose_image_x_ind]
    car_pose_image_y = df_path_.iloc[:, car_pose_image_y_ind]
    car_pose_image_yaw = df_path_.iloc[:, car_pose_image_yaw_ind]
    return x, y, data_timestamps, v, car_pose_image_x, car_pose_image_y, car_pose_image_yaw, car_pose_now_timestamp, car_pose_now_x, car_pose_now_y, car_pose_now_yaw
      

#%% Load trip data
def load_trip_data(trip_path, data_ds_factor):
    X_gps_lng_lat, df_xyz = dh.load_trip_gps_data(trip_path, coordinates_type="both",
                                                  sample_spacing=data_ds_factor, tangent_frame="NED")
    df_imu = read_nissan_imu_data(trip_path)
    yaw = np.asarray(df_imu['yaw'])
    t_yaw = np.asarray(df_imu['time_stamp'])
    return X_gps_lng_lat, df_xyz, yaw, t_yaw

#%% Plot trip map
def plot_trip_map(X_gps_lng_lat, trip_name):
    trip_latlong = np.fliplr(X_gps_lng_lat[0:2, :].T)
    map_name = 'map_' + trip_name
    m, map_nampe = trip_view_on_map(trip_latlong, map_name)
    webbrowser.open_new_tab(map_nampe)

#%% Plot ego path
def plot_ego_path(x_ego, y_ego):
    with plt.ioff():
        fig, ax = plt.subplots(1, 1, figsize=(5, 2.7))
        my_plotter(ax, x_ego, y_ego, {'color': 'orange', 'linewidth': 1, 'linestyle': '--', 'label': 'ego'})
        ax.set_title('EgoPlot')
        ax.set_aspect('equal', 'box')
    plt.show()

def plot_paths(p_i_merged_world, p_2_2, X_2_world, axs, fig, color_cnt, colors, trip_name):
    color = colors[color_cnt % (len(colors) - 1)]
    axs[1].scatter(*p_i_merged_world.T, color=color, s=5)
    axs[1].plot(*p_i_merged_world.T, '--', color=color)
    axs[1].set_aspect('equal')
    axs[1].grid()
    axs[1].set_title('Merged path in world frame')

    pi_world = apply_se2_transform(X_2_world, p_2_2)
    axs[0].scatter(*pi_world.T, color=color, s=5)
    axs[0].plot(*pi_world.T, '--', color=color)
    axs[0].set_aspect('equal')
    axs[0].grid()
    axs[0].set_title('Unmerged path in world frame')
    fig.suptitle('Path Assembler, %s' % (trip_name), fontsize=12, fontweight='bold')
#%% Get path from x_y
def get_path_from_x_y(x, y):
            p_ = np.vstack((x, y)).T
            p = extract_valid_path(p_, 3) # Remove padding zeros            
            return p
        
#%% Process and plot paths
def process_paths(params, SE2_matrices, t_path, x_path, y_path, trip_name, lambda_handler_ego):
    path_cnt = 0
    t_path_1 = None
    p_1_1_merged = None
    X_1_world = None
    path_print_points_skip = 6
    path_length_to_print = 50
    path_print_inds = np.arange(0, path_length_to_print, path_print_points_skip)
    colors = ['red', 'tab:brown', 'green', 'blue', 'yellow', 'tab:pink', 'black', 'tab:orange', 'purple', 'cyan', 'tab:olive']
    N2 = math.ceil(params['N2_meters'] / params['spline_ds'])

    fig, axs = plt.subplots(1, 2, figsize=(5, 15), sharex=True, sharey=True)
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)
    plt.ion()

    for i, X_2_world in enumerate(SE2_matrices):
        if i < params['PathAssemblerOptions']['path_start_ind'] or i > params['PathAssemblerOptions']['path_end_ind']:
            continue  # Skip values outside the range

        if i % (1 + params['PathAssemblerOptions']['frames_skip']) != 0:
            continue

        t_path_2 = t_path.iloc[i]  # Get the time stamp of the current path to check refractory period
        if path_cnt > 0 and (t_path_2 - t_path_1) < params['PathAssemblerOptions']['refractory_period_sec']:
            continue

        X_2_world = SE2(X_2_world)      
        p_2_2 = get_path_from_x_y(np.asarray(x_path.iloc[i, :]), np.asarray(y_path.iloc[i, :]))

        if params['trip_settings']['transform_from_CFA_to_COG']:
            p_2_2 = apply_se2_transform(params['T_CFA_to_COG'], p_2_2)

        if path_cnt == 0:  # First path - no merging
            p_2_2_merged = p_2_2
        else:  # Merge the paths            
            X_now_world = SE2(lambda_handler_ego(t_path[i] + params['PathAssemblerOptions']['delay']))
            T_1_to_2 = X_1_world.inv() * X_2_world
            p_1_2_merged = apply_se2_transform(T_1_to_2.inv(), p_1_1_merged)            
            p_2_2_merged = path_merger_wrapper(p_1_2_merged, p_2_2, X_1_world, X_2_world,
                                                    X_now_world, tau_1=0.2, N2=N2, options=params['merge_options'])
        
        p_2_world_merged = apply_se2_transform(X_2_world, p_2_2_merged)
   
        plot_paths(p_2_world_merged, p_2_2, X_2_world, axs, fig, path_cnt, colors, trip_name)
        
        p_1_1_merged = p_2_2_merged
        X_1_world = X_2_world
        path_cnt += 1
        t_path_1 = t_path_2

    # plt.ioff()
    plt.show(block=True)

def process_paths_known_car_pose_now(params, SE2_matrices, v_ego, t_path, x_path, y_path, trip_name, x_now, y_now, yaw_now):
    path_cnt = 0
    t_path_1 = None
    p_1_1_merged = None
    X_1_world = None       
    colors = ['red', 'tab:brown', 'green', 'blue', 'yellow', 'tab:pink', 'black', 'tab:orange', 'purple', 'cyan', 'tab:olive']
    N2 = math.ceil(params['N2_meters'] / params['spline_ds'])

    fig, axs = plt.subplots(1, 2, figsize=(5, 15), sharex=True, sharey=True)
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)
    plt.ion()

    #for i, X_2_world in enumerate(SE2_matrices):    
    for i in range(len(SE2_matrices)):
        X_2_world = SE2_matrices[i]
        if i < params['PathAssemblerOptions']['path_start_ind'] or i > params['PathAssemblerOptions']['path_end_ind']:
            continue  # Skip values outside the range

        if i % (1 + params['PathAssemblerOptions']['frames_skip']) != 0:
            continue

        t_path_2 = t_path.iloc[i]  # Get the time stamp of the current path to check refractory period
        if path_cnt > 0 and (t_path_2 - t_path_1) < params['PathAssemblerOptions']['refractory_period_sec']:
            continue

        X_2_world = SE2(X_2_world)      
        p_2_2 = get_path_from_x_y(np.asarray(x_path.iloc[i, :]), np.asarray(y_path.iloc[i, :]))

        if params['trip_settings']['transform_from_CFA_to_COG']:
            p_2_2 = apply_se2_transform(params['T_CFA_to_COG'], p_2_2)

        if path_cnt == 0:  # First path - no merging
            p_2_2_merged = p_2_2
        else:  # Merge the paths      
            X_now_world = SE2(x_now[i], y_now[i], yaw_now[i])      
            T_1_to_2 = X_1_world.inv() * X_2_world
            p_1_2_merged = apply_se2_transform(T_1_to_2.inv(), p_1_1_merged)            
            p_2_2_merged = path_merger_wrapper(p_1_2_merged, p_2_2, X_1_world, X_2_world,
                                                    X_now_world, tau_1=0.2, N2=N2, Vnow=v_ego[i], options=params['merge_options'])
        
        p_2_world_merged = apply_se2_transform(X_2_world, p_2_2_merged)
   
        plot_paths(p_2_world_merged, p_2_2, X_2_world, axs, fig, path_cnt, colors, trip_name)
        
        p_1_1_merged = p_2_2_merged
        X_1_world = X_2_world
        path_cnt += 1
        t_path_1 = t_path_2

    #plt.ioff()
    plt.show()

def execute_from_path_trajectory(params):    
    trip_path = params['trip_settings']['trip_path']
    if params['trip_settings']['Run_alternative_trip']:
        trip_name = params['trip_settings']['alternative_trip_name']
        trip_path = os.path.join('/'.join(trip_path.split('/')[:-1]), trip_name)
    else:
        trip_name = trip_path.split('/')[-1]

    # Load trajectory data
    x_path, y_path, t_path, v_path, x_ego, y_ego, yaw_ego, t_ego, x_now, y_now, yaw_now = load_path_trajectory_file(trip_path)
    # if params['plot_settings']['print_trip_map']:
    #     plot_trip_map(car_pose, trip_name)
    if params['plot_settings']['plot_ego']:
        plot_ego_path(x_ego, y_ego)

    # Construct SE2 matrices from car poses.
    SE2_matrices = []
    for i in range(len(yaw_ego)):
        SE2_matrices.append(SE2(x_ego[i], y_ego[i], yaw_ego[i]))
    
    if params['plot_settings']['plot_poses']:
        plot_se2_path(x_ego[::100], y_ego[::100], yaw_ego[::100])

    process_paths_known_car_pose_now(params, SE2_matrices, v_path, t_path, x_path, y_path, trip_name, x_now, y_now, yaw_now)


#%% Main function to execute the process
def main():    
    adjust_path()
    params = initialize_parameters()
    if params['trajectory_new_format']:
        execute_from_path_trajectory(params)
        plt.show(block=True)
        print('done')
        return
    
    trip_path = params['trip_settings']['trip_path']
    if params['trip_settings']['Run_alternative_trip']:
        trip_name = params['trip_settings']['alternative_trip_name']
        trip_path = os.path.join('/'.join(trip_path.split('/')[:-1]), trip_name)
    else:
        trip_name = trip_path.split('/')[-1]

    X_gps_lng_lat, df_xyz, yaw, t_yaw = load_trip_data(trip_path, params['trip_settings']['data_ds_factor'])
    x_ego = df_xyz['x']
    y_ego = df_xyz['y']
    t_ego = df_xyz['time_stamp']
    x_path, y_path, t_path, v_ego = read_path_data(trip_path)

    if params['plot_settings']['print_trip_map']:
        plot_trip_map(X_gps_lng_lat, trip_name)
    if params['plot_settings']['plot_ego']:
        plot_ego_path(x_ego, y_ego)

    SE2_matrices, lambda_handler_ego = get_interpolated_pose_SE2(t_path, yaw, t_yaw, x_ego, y_ego, t_ego)
    
    if params['plot_settings']['plot_poses']:
        plot_se2_path(x_ego[::100], y_ego[::100], yaw[::100])

    process_paths(params, SE2_matrices, t_path, x_path, y_path, trip_name, lambda_handler_ego)     

if __name__ == "__main__":
    main()
