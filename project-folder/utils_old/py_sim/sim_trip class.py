#%% Import libraries
import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.path_aux_utils import *
from utils.init_utils import pre_required_install_check
# check if the required packages are installed and install them if not
pre_required_install_check()

import matplotlib
matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import random
from typing import List, Union, Optional
from spatialmath import SE2
from scipy.interpolate import interp1d
from scipy import linalg
import math
import webbrowser

from utils.aidriver_logs_readers.path_loader import read_nissan_imu_data, read_path_data
import utils.aidriver_logs_readers.utils_trip_data_handler as dh
from utils.se2_function import get_interpolated_pose_SE2, apply_se2_transform
from utils.path_geom_utils import extract_valid_path
from utils.plot_helpers import my_plotter, plot_se2_path
from utils.utils_geo import trip_view_on_map
from path_merger.path_merger_utils import PathMergerOptions, path_merger_wrapper
from path_merger.PathMerger import PathMerger
    
#%% Initialize settings and parameters
def initialize_parameters():
    params = {
        'lm1': 0.5,  # smoothing lambda
        'lm2': 0.5,  # derivative constraint lambda
        'w_inc': 4,  # weighing of p2 before i2 (larger value means faster decay)
        'merge_options': PathMergerOptions(lambda_1=0.5, lambda_2=0.5, w=4),
        'N2_meters': 2,  # blending region length in z
        'spline_ds': 0.1,  # spline interpolation step
        'spline_degree': 3,  # spline interpolation degree
        'plot_settings': {
            'print_trip_map': False,
            'plot_poses': False,
            'plot_ego': False,
            'plot_after_merge': False,
        },
        'trip_settings': {
            'Run_alternative_trip': True,
            'alternative_trip_name': '2024-07-18T11_29_56',
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
    
    # Instantiate the path merger class
    path_merger = PathMerger(tau_1_ms=0.2, N2=30, lambda_1=params['lm1'], lambda_2=params['lm2'], w=params['w_inc'], spline_degree=params['spline_degree'], DEBUG_MODE=True)

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
            X_now_world = X_2_world
            p_2_2_merged = path_merger.merge_with_new_path(p_2_2, X_2_world, X_now_world)
        else:  # Merge the paths            
            X_now_world = SE2(lambda_handler_ego(t_path[i] + params['PathAssemblerOptions']['delay']))
            p_2_2_merged = path_merger.merge_with_new_path(p_2_2, X_2_world, X_now_world)
         
        plot_paths(apply_se2_transform(X_2_world, p_2_2_merged), p_2_2, X_2_world, axs, fig, path_cnt, colors, trip_name)        
        path_cnt += 1
        t_path_1 = t_path_2

    plt.ioff()
    plt.show()

#%% Main function to execute the process
def main():
    params = initialize_parameters()
    
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
