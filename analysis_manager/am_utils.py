# utils.py
import os
import sys

# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

import numpy as np
import matplotlib.pyplot as plt
import utils.plot_helpers as plt_helper
from analysis_manager.DataClasses.Class_PathTrajectory import *
from config import ClassObjType

def update_plots(slider_val, cp_time_seconds, str_time_seconds, df_steering, ax_pose, marker_steering, marker_steering_rate, cp_x, cp_y, cp_yaw_deg, PathObj: PathTrajectory, PathExtractionObj: PathTrajectory, PathAdjustmentObj: PathTrajectory):
    """Update the plots and markers when the slider value changes."""

    if df_steering is not None:
        str_index = np.searchsorted(str_time_seconds, slider_val)
        marker_steering.set_data([str_time_seconds[str_index]], [df_steering['current_steering_deg'].iloc[str_index]])
        marker_steering_rate.set_data([str_time_seconds[str_index]], [df_steering['current_steering_rate'].iloc[str_index]])

    # Update car pose
    if cp_x is None or cp_y is None or cp_yaw_deg is None:
        pass
    else:
        cp_index = np.searchsorted(cp_time_seconds, slider_val)
        ax_pose.set_aspect('equal')

        
        # If this is the first time we plot then set the zoom to the current car pose
        if ax_pose.get_xlim() == (0.0, 1.0) and ax_pose.get_ylim() == (0.0, 1.0):   
            ax_pose.set_xlim(cp_x.iloc[cp_index] - 10, cp_x.iloc[cp_index] + 10)
            ax_pose.set_ylim(cp_y.iloc[cp_index] - 10, cp_y.iloc[cp_index] + 10)    
        
        
        # Save current axis limits
        xlim = ax_pose.get_xlim()
        ylim = ax_pose.get_ylim()
        
        ax_pose.clear()
        plt_helper.plot_ego_path(cp_x, cp_y, ax_=ax_pose)
        plt_helper.plot_se2_path(cp_x.iloc[cp_index], cp_y.iloc[cp_index], cp_yaw_deg.iloc[cp_index], ax_=ax_pose, plot_full_path=False)
        
        # Plot all the poses reading columns: w_car_pose_now_x, w_car_pose_now_y, w_car_pose_now_yaw_deg, 
        if 0:
            car_poxe_image_x_vector = PathObj.df_path['w_car_pose_image_x']
            car_poxe_image_y_vector = PathObj.df_path['w_car_pose_image_y']
            car_poxe_image_yaw_vector = PathObj.df_path['w_car_pose_image_yaw_rad']
            
            car_poxe_now_x_vector = PathObj.df_path['w_car_pose_now_x_']
            car_poxe_now_y_vector = PathObj.df_path['w_car_pose_now_y']
            car_poxe_now_yaw_vector = PathObj.df_path['w_car_pose_now_yaw_rad']
            
            ax_pose.scatter(car_poxe_image_x_vector, car_poxe_image_y_vector, color='blue', s=5, label='Image Car Pose')
            ax_pose.scatter(car_poxe_now_x_vector, car_poxe_now_y_vector, color='red', s=5, label='Now Car Pose')
            
            
            
        # Restore axis limits
        ax_pose.set_xlim(xlim)
        ax_pose.set_ylim(ylim)
        
    # Plot current path from current car pose 
    if PathObj is None:
        pass
    else:
        path_w = PathObj.get_path_in_world_coordinates(slider_val)    
        ax_pose.scatter(*path_w.T, color='green', s=5, label='Current Path')

    try:
        if PathExtractionObj is None:
            pass    
        else:
            path_extraction_w = PathExtractionObj.get_path_in_world_coordinates(slider_val)
            ax_pose.scatter(*path_extraction_w.T, color='red', s=5, label='Path Extraction')
    except AttributeError as e:
        print(f"Error: {e}")
        pass

    try:
        if PathAdjustmentObj is None:
            pass
        else:
            path_adjustment_w = PathAdjustmentObj.get_path_in_world_coordinates(slider_val)
            ax_pose.scatter(*path_adjustment_w.T, color='blue', s=5, label='Path Adjustment')

    except AttributeError as e:
        print(f"Error: {e}")
        pass
      
    # Refresh the plot
    plt.draw()
