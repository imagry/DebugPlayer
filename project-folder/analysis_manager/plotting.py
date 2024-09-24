# plotting.py

from utils.plot_helpers import plot_ego_path, plot_se2_path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from config import W, L, wb, b_f, b_r, arm

def setup_figure():
    """Setup the figure and subplots using GridSpec."""
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(3, 2, figure=fig)

    # Subplots for time series on the left side
    ax_steering = fig.add_subplot(gs[0, 0])
    ax_steering_rate = fig.add_subplot(gs[1, 0], sharex=ax_steering)
    ax_speed = fig.add_subplot(gs[2, 0], sharex=ax_steering)

    # Subplot for car pose on the right side
    ax_pose = fig.add_subplot(gs[:, 1])  # Full right-hand side (spanning all rows)
    
    return fig, ax_steering, ax_steering_rate, ax_speed, ax_pose

def plot_time_series(ax_steering, ax_steering_rate, df_steering, str_time_seconds):
    """Plot the time-series data for steering and steering rate."""
    # Steering plot
    if df_steering is not None:
        if 'current_steering_deg' in df_steering.columns:
            ax_steering.plot(str_time_seconds, df_steering['current_steering_deg'], label='Current Steering', color='blue')
        if 'steer_command' in df_steering.columns:
            ax_steering.plot(str_time_seconds, df_steering['steer_command'], label='Target Steering', linestyle='--', color = 'red')
        ax_steering.set_title('Steering over Time')
        ax_steering.set_ylabel('Steering [deg]')
        ax_steering.set_xlabel('Time')
        ax_steering.legend()

    # Steering rate plot
    if df_steering is not None:
        if 'current_steering_rate' in df_steering.columns:
            ax_steering_rate.plot(str_time_seconds, df_steering['current_steering_rate'], label='Current Steering Rate', linestyle='-', color='blue')
        if 'steer_command_rate' in df_steering.columns:
            ax_steering_rate.plot(str_time_seconds, df_steering['steer_command_rate'], label='Target Steering Rate', linestyle='--', color='red')
        ax_steering_rate.set_title('Steering Rate over Time')
        ax_steering_rate.set_ylabel('Steering Rate [deg/s]')
        ax_steering_rate.set_xlabel('Time')
        ax_steering_rate.legend()

def plot_car_pose(ax_pose, cp_x, cp_y, cp_time_seconds, slider_val, cp_yaw_deg):
    """Plot the car's pose at the current time."""
    ax_pose.clear()
    plot_ego_path(cp_x, cp_y, ax_=ax_pose)
    cp_index = np.searchsorted(cp_time_seconds, slider_val)
    plot_se2_path(cp_x.iloc[cp_index], cp_y.iloc[cp_index], cp_yaw_deg.iloc[cp_index], ax_=ax_pose, plot_full_path=False)
    
    # Calculate the corners of the rectangular box
    # The car pose corresponds to the center of the front axle
    yaw = np.deg2rad( cp_yaw_deg.iloc)
    x = cp_x.iloc[cp_index]
    y = cp_y.iloc[cp_index]
    
    front_axle_x = x + b_f * np.cos(yaw)
    front_axle_y = y + b_f * np.sin(yaw)
    # Calculate the center of the car box
    center_x = front_axle_x - arm * np.cos(yaw)
    center_y = front_axle_y - arm * np.sin(yaw)
        # Calculate the corners of the box
    corners = np.array([
        [b_f, W / 2],
        [b_f, -W / 2],
        [-b_r, -W / 2],
        [-b_r, W / 2]
    ])
        
    # Rotate and translate the corners
    rotation_matrix = np.array([
        [np.cos(yaw), -np.sin(yaw)],
        [np.sin(yaw), np.cos(yaw)]
    ])
    rotated_corners = np.dot(corners, rotation_matrix.T)
    translated_corners = rotated_corners + np.array([center_x, center_y])
    
    # Plot the rectangular box
    car_box = plt.Polygon(translated_corners, closed=True, edgecolor='r', facecolor='none')
    ax_pose.add_patch(car_box)
        
    # Optionally, plot the center of the front axle
    ax_pose.plot(front_axle_x, front_axle_y, 'bo')  # Blue dot for the front axle center
