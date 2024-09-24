import numpy as np
import matplotlib.pyplot as plt
from spatialmath import SE2
from se2_function import *
import webbrowser

import sys
import subprocess
import pkg_resources
import matplotlib.patches as patches

# Check if mpl_interactions is installed, if not install it
package_name = 'mpl_interactions'
try:
    pkg_resources.get_distribution(package_name)
except pkg_resources.DistributionNotFound:
    print(f"{package_name} is not installed. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

from mpl_interactions import ioff, panhandler, zoom_factory
from utils_geo import trip_view_on_map

def path_merger_plot_cpp(X_1_world, X_2_world, X_now_world, p1_world, p2_world, p2_merged_world):
    #%% Plots
    fig = plt.figure(figsize=(10, 10))
    fig.suptitle('Path Merger Results')
    # Plotting in the World coordinates
    plt.plot(*p2_merged_world.T, '--', color='black', label='solution')
    plt.scatter(*p1_world.T, color='tab:blue',s=10)
    plt.scatter(*p2_world.T, color='tab:orange',s=10)    
    plt.scatter(X_now_world.t[0],X_now_world.t[1], color='tab:blue',marker='x', label='X_(now)')
    plt.gca().set_aspect('equal')        
    plt.grid()
    plt.legend()
    plt.title('World Coordinates Results')    
    plt.show()
    
def path_merger_plot(X_1_world, X_2_world, X_now_world, p1_world, p2_world, p2_merged_world, i0, i1, i12, i2, p2_merged_ego_p2_truncated, p1_ego_p2, p2_ego_p2):
    #%% Plots
    p2_merged_ego_p2 = apply_se2_transform(X_2_world.inv(), p2_merged_world)
    p2_ego_p1 = apply_se2_transform(X_1_world.inv(), p2_world)
    X2_ego_p1 = X_1_world.inv() * X_2_world
    X1_ego_p2 = X_2_world.inv() * X_1_world
    X2_ego_p2 = SE2()
    X1_ego_p1 = SE2()
    p1_ego_p2 = apply_se2_transform(X_2_world.inv(), p1_world)
    p1_ego_p1 = apply_se2_transform(X_1_world.inv(), p1_world)
    
    # Plotting in the World coordinates
    plt.subplot(2, 2, 1)
    plt.plot(*p2_merged_world.T, '--', color='black', label='solution')
    plt.scatter(*p1_world.T, color='tab:blue',s=10)
    plt.scatter(*p2_world.T, color='tab:orange',s=10)
    plt.scatter(*p2_world[i2], color='tab:red', label='i2', marker='s',alpha = 0.45, s= 100)
    plt.scatter(*p2_world[i12], color='tab:brown', label='i12',marker='s',alpha = 0.45, s= 100)
    plt.scatter(*p1_world[i0], color='tab:purple', label='i0',marker='s',alpha = 0.45, s= 100)
    plt.scatter(*p1_world[i1], color='tab:green', label='i1',marker='s',alpha = 0.45, s= 100)
    plt.scatter(X_now_world.t[0],X_now_world.t[1], color='tab:blue',marker='x', label='X_(now)')
    plt.gca().set_aspect('equal')        
    plt.grid()
    plt.legend()
    plt.title('World Coordinates')
    
    # plotting in the ego coordinates of p2    
    plt.subplot(2, 2, 3)
    plt.plot(*p2_merged_ego_p2.T, '--', color='black', label='p2_merged_ego_p2')
    plt.plot(*p2_merged_ego_p2_truncated.T,':' ,color='tab:green',
             label='p2_merged_ego_p2_truncated', linewidth = 4)
    plt.scatter(*p1_ego_p2.T, color='tab:blue',s=10, label='p1_ego_p2')
    plt.scatter(*p2_ego_p2.T, color='tab:orange',s=10, label='p2_ego_p2')     
    plt.scatter(X1_ego_p2.t[0],X1_ego_p2.t[1], color='tab:purple',marker='x', label='X1_ego2')
    plt.gca().set_aspect('equal')        
    plt.grid()
    # move legend outside the plot
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.legend()

    plt.title('Ego Coordinates of p2')
    # plt.show()
    
    # Plotting p1 and p2 in p1_ego coordinates   
    plt.subplot(2, 2, 2) 
    plt.plot(*p1_ego_p1.T, '--', color='black', label='p1_ego_p1')
    plt.plot(*p2_ego_p1.T,':' ,color='tab:orange', label='p2_ego_p1', linewidth = 4)
    plt.scatter(X2_ego_p1.t[0],X2_ego_p1.t[1], color='tab:purple',marker='x', label='X2_ego_p1',s = 100)    
    plt.scatter(X1_ego_p1.t[0],X1_ego_p1.t[1], color='tab:red',marker='x', label='X1_ego_p1',s = 100)    
    plt.gca().set_aspect('equal')        
    plt.grid()
    # move legend outside the plot
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()
    plt.title('P1 and P2 in p1_ego coordinates -  W/O merging')

    
    # Plotting p1 and p2 in p2_ego coordinates - W/O merging   
    plt.subplot(2, 2, 4) 
    plt.plot(*p1_ego_p2.T, '--', color='black', label='p1_ego_p2')
    plt.plot(*p2_ego_p2.T,':' ,color='tab:orange', label='p2_ego_p2', linewidth = 4)
    plt.scatter(X1_ego_p2.t[0],X1_ego_p2.t[1], color='tab:red',marker='x', label='X1_ego2',s = 100) 
    plt.scatter(X2_ego_p2.t[0],X2_ego_p2.t[1], color='tab:purple',marker='x', label='X2_ego_p2',s = 100)       
    plt.gca().set_aspect('equal')        
    plt.grid()
    # move legend outside the plot
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend()
    plt.title('P1 and P2 in p2_ego coordinates -  W/O merging')
    plt.show()

def my_plotter(ax, data1, data2, param_dict):
    """
    Helper function to plot the data and enable zoom functionality.
    """
    # Plot the trajectory data
    out = ax.plot(data1, data2, **param_dict)
    
    # Enable zoom functionality (if implemented)
    disconnect_zoom = zoom_factory(ax)  # Assuming you have a zoom handler function defined
    
    ax.set_aspect('equal', 'box')
    return out

def draw_car_box(ax, x, y, yaw):
    """
    Draw the car as a rectangular box with given dimensions.
    
    Parameters:
    - ax: The matplotlib axes to plot on.
    - x, y: The position of the car.
    - yaw: The orientation of the car in radians.
    """
    from config import W, L, wb, b_f, b_r, arm
    
    # Calculate the corners of the rectangular box
    # The car pose corresponds to the center of the front axle
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
    ax.add_patch(car_box)
    
    # Optionally, plot the center of the front axle
    ax.plot(front_axle_x, front_axle_y, 'bo')  # Blue dot for the front axle center

def plot_ego_path(x_ego, y_ego, param_dict={}, ax_=None):# linestyle='--', color='orange', linewidth=1, label='ego', 
                  #marker = 'o', markersize = 5, markerfacecolor = 'orange', markeredgecolor = 'black'):
    """
    Plots the full ego vehicle trajectory as a background.
    
    Parameters:
    x_ego (pandas.Series or list of float): x coordinates of the ego vehicle.
    y_ego (pandas.Series or list of float): y coordinates of the ego vehicle.
    ax_ (matplotlib.axes._axes.Axes, optional): Axes on which to plot.
    """
    with plt.ioff():  # Disable interactive mode during plotting
        if ax_ is None:
            fig, ax = plt.subplots()
        else:
            ax = ax_                
        
        # Plot the trajectory in the background
        my_plotter(ax, x_ego, y_ego, param_dict)#{'color': 'orange', 'linewidth': 1, 'linestyle': '--', 'label': 'ego'})
        ax.set_title('Ego Path')
        ax.set_aspect('equal')
        
        # Set axis limits based on the full trajectory
        ax.set_xlim(min(x_ego) - 1, max(x_ego) + 1)
        ax.set_ylim(min(y_ego) - 1, max(y_ego) + 1)

    if ax_ is None:
        plt.show()
        
def plot_se2_path(x_ego, y_ego, yaw_deg, ax_=None, plot_full_path=True, path_marker=None):
    """
    Plots a series of oriented poses based on x, y, and yaw values, and optionally shows the full path.
    
    Parameters:
    x_ego (pandas.Series or list of float): x coordinate(s) of the ego vehicle.
    y_ego (pandas.Series or list of float): y coordinate(s) of the ego vehicle.
    yaw_deg (pandas.Series or list of float): yaw angle(s) in degrees.
    ax_ (matplotlib.axes._axes.Axes, optional): Axes on which to plot. If None, a new figure is created.
    plot_full_path (bool, optional): Whether to plot the entire path.
    path_marker (matplotlib line, optional): Line2D object to update the path plot without re-plotting.
    """
    # Check if the data arrays are non-empty
    if x_ego is None or y_ego is None or yaw_deg is None:
        print("Error: Empty data provided to plot_se2_path.")
        return
    
    def draw_pose(ax, se2, length=0.5, **kwargs):
        """
        Draw a single SE(2) pose on the given axes.
        """
        origin = se2.t
        angle = se2.theta()
        trplot2(transl2(origin[0], origin[1]) @ trot2(angle), length=3, width=1, rviz=True, ax=ax)  # Ensure correct axes are used

    # Convert yaw angles from degrees to radians
    yaw_rad = np.deg2rad(yaw_deg)

    if ax_ is None:
        # If no axes are passed, create a new figure and axis
        fig, ax = plt.subplots()
    else:
        ax = ax_

    # Plot the path once (if desired)
    if plot_full_path:
        path = np.array([[x, y] for x, y in zip(x_ego, y_ego)])
        if path_marker is None:
            path_marker, = ax.scatter(path[:, 0], path[:, 1], color = 'black', label='Path', s= 5)
        else:
            path_marker.set_data(path[:, 0], path[:, 1])

    # Plot the current pose (oriented marker)
    # if x_ego is not None:  # Make sure there's at least one pose to draw
    # se2_matrix = SE2(x_ego.iloc[-1], y_ego.iloc[-1], yaw_rad.iloc[-1])  # Use .iloc[-1] to access the last element
    se2_matrix = SE2(x_ego, y_ego, yaw_rad)  # Use .iloc[-1] to access the last element
    draw_pose(ax, se2_matrix, length=0.5)


    draw_car_box(ax, x_ego, y_ego, yaw_rad)


    # Set plot limits and labels
    # ax.set_xlim(-5, 5)
    # ax.set_ylim(-5, 5)
    # ax.set_aspect('equal')  # Maintain equal scaling for x and y axes
    # ax.set_xlabel('X')
    # ax.set_ylabel('Y')
    # ax.set_title('Car Pose at Current Time')

    # plt.legend()

    if ax_ is None:
        plt.show()

    return path_marker
    
def plot_paths_ego(ax, p2_2, p1_2, p2_2_merged, title, x_limits, y_limits):
    """
    Helper function to plot paths, rectangle, and concentric circles.
    
    Parameters:
    - ax: The matplotlib axis to plot on.
    - p2_2: The scatter data for p2_2.
    - p1_2: The line data for p1_2.
    - p2_2_merged: The line data for merged p2_2.
    - title: The title for the plot.
    - x_limits: The x-axis limits.
    - y_limits: The y-axis limits.
    """
    ax.clear()
    ax.set_xlim(x_limits)
    ax.set_ylim(y_limits)

    # Plot the paths
    ax.scatter(*p2_2.T, color='red', s=5, label='p2_2')
    ax.plot(*p1_2.T, '--', color='blue', label='p1_2')
    ax.plot(*p2_2_merged.T, '--', color='green', label='p2_2_merged')
    ax.set_aspect('equal')
    ax.grid()
    ax.set_title(title)

    # Add rectangle
    rectangle_width = 1.8
    rectangle_length = 4.5
    rectangle_x = -(rectangle_length-1.12)  # Offset the origin by 1.12 meters from the right edge
    rectangle_y = -rectangle_width / 2  # Centered along the y-axis

    rect = patches.Rectangle((rectangle_x, rectangle_y), rectangle_length, rectangle_width, 
                             linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(rect)

    # Add concentric dashed circles around the origin
    max_radius = 30
    for radius in range(3, max_radius + 1, 3):
        circle = patches.Circle((0, 0), radius, linestyle='--', edgecolor='gray', facecolor='none')
        ax.add_patch(circle)

def plot_trip_map(X_gps_lng_lat, trip_name):
    trip_latlong = np.fliplr(X_gps_lng_lat[0:2, :].T)
    map_name = 'map_' + trip_name
    m, map_nampe = trip_view_on_map(trip_latlong, map_name)
    webbrowser.open_new_tab(map_nampe)    