# main_analysis_manager.py
import argparse
# %% Import libraries
import os
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
from init_utils import initialize_environment
# Initialize the environment
initialize_environment()
import data_preparation as dp 
import utils.plot_helpers as plt_helper

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
    # # Load the data    
    PathObj = dp.prepare_path_data(trip_path, interpolation=False) 
    df_car_pose = dp.prepare_car_pose_data(trip_path, interpolation=False)     
    
    return PathObj, df_car_pose
    
    # plot_dict = {'linestyle':':', 'color':'orange', 'linewidth':1, 'label':'ego', 'marker':'o', 'markersize':2, 'markerfacecolor':'orange', 'markeredgecolor':'orange'}
    # plt_helper.plot_ego_path(cp_x, cp_y, plot_dict, ax_=ax)


app = pg.mkQApp("Path Regression Analysis")

win = pg.GraphicsLayoutWidget(show=True, title="2D Trajectory Plot")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: 2D Trajectory Plot')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title="Parametric, grid enabled")


# Parse the command-line arguments
trip_path = parse_arguments()
PathObj, df_car_pose = load_data(trip_path)
# Create a figure and axis and plot in it the trajectory of the car
cp_x = df_car_pose['cp_x']
cp_y = df_car_pose['cp_y']

p1.ScatterPlotItem
p4.showGrid(x=True, y=True)
    # data = dp.load_data()
    # # Preprocess the data
    # data = dp.preprocess_data(data)
    # # Split the data
    # data = dp.split_data(data)
    # # Train the model
    # model = dp.train_model(data)
    # # Save the model
    # dp.save_model(model)
    # # Evaluate the model
    # dp.evaluate_model(model, data)
    # # Make predictions
    # dp.make_predictions(model, data)

if __name__ == '__main__':       
    pg.exec()
    
    