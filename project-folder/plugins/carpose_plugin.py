# carpose_plugin.py
from plugins.plugin_api_interfaces import UserPluginInterface
from utils.data_loaders.car_pose_loader import prepare_car_pose_data
from utils.data_loaders.car_pose_loader import CarPose
import pyqtgraph as pg
import numpy as np
import pandas as pd
class CarPosePlugin(UserPluginInterface):
    def __init__(self):
        self.car_pose = None
        self.timestamps = None
        self.plot_widget = None  # Store plot widget reference

    def load_data(self, trip_path):
        """Load the car pose data."""
        df_carpose = prepare_car_pose_data(trip_path)
        self.car_pose = CarPose(df_carpose)   
        self.timestamps = self.car_pose.get_timestamps() 

        self.trajectory = self.car_pose.get_trajectory()             
        print(f"Loaded car pose data from {trip_path}")

    def sync_data_with_timestamp(self, timestamp):
        """Update the vehicle's position at the given timestamp and refresh plot."""
        if self.car_pose is not None:
            self.current_position = self.get_data_with_timestamp(timestamp)

        # If we have a plot widget, update the plot with the new position
        if self.plot_widget is not None:
            self.update_plot()


    def set_display(self, plot_widget, timestamp, plot_opt_dict=None):
        """Store plot widget and plot the full trajectory and current position."""
        self.plot_widget = plot_widget  # Store the plot widget reference
        
        # TODO: add plot of pose not just position
        if plot_opt_dict is not None:
            self.plot_opts_dict = plot_opt_dict
            # define a lmabda function for the plot as fucntion of x and y
            self.plot_handle = lambda x, y: self.plot_widget.plot(x, y, pen=plot_opt_dict.get('pen', None), symbol=plot_opt_dict.get('symbol', 'o'), symbolSize=plot_opt_dict.get('symbolSize', 5), symbolBrush=plot_opt_dict.get('symbolBrush', 'r'))            
        else:
            self.plot_opts_dict = None
            self.plot_handle = lambda x, y: self.plot_widget.plot(x, y, pen=pg.mkPen(color='b'), symbol='o', symbolSize=5, symbolBrush='r')
            
            
    def update_plot(self):
        """Update the plot with the vehicle's current position."""
        if self.current_position is not None :
            x = self.current_position[0]
            y = self.current_position[1]
            yaw = self.current_position[2]
            
            self.plot_widget.clear()  # Clear existing plot
            # extract the x and y coordinates from the trajectory
            x_traj = np.asarray(self.trajectory['cp_x'])
            y_traj = np.asarray(self.trajectory['cp_y'])
            
            self.plot_widget.plot(x_traj, y_traj, pen=pg.mkPen(color='b'))  # Plot the full trajectory
            
            # Ensure that x and y are arrays or lists            
            if x.shape == ():
                x = np.array([x])
            if y.shape == ():
                y = np.array([y])
                        
            if self.plot_widget is not None:
                # Plot the current position
                self.plot_handle(x,y)
        else:
            print("No data to plot.")
            

            
         
            
    
    def get_data_with_timestamp(self, timestamp):
        """Get the car pose data for the given timestamp."""
        return self.car_pose.get_car_pose_at_timestamp(timestamp, interpolation = True)

    def get_car_pose_data(self):
        """Return the car pose data."""
        return self.car_pose
    
    def get_timestamps(self):
        """Return the timestamps."""
        return self.timestamps
