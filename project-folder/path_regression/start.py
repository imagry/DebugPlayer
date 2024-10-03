# main_path_regression.py

# main_analysis_manager.py
import os
import sys
import argparse
import pyqtgraph as pg
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QAction  # Import QAction from PySide6.QtGui
from pyqtgraph.dockarea import DockArea, Dock
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

import pandas as pd
import numpy as np
import multiprocessing

# Add the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plugins.main_path_regression import MainPathRegression
from data_handlers import load_data, parse_arguments, create_path_regressors
from ui_components import create_main_window, connect_signals
from slider import TimestampSlider
from plot_functions import save_figure
from data_classes.PathRegressor import PathRegressor
from plugins.plugin_registry import PluginRegistry
from plugins.plugin_api_interfaces import UserPluginInterface
from plot_functions import calculate_virtual_path
from config import Config
from menu_setup import setup_menus
# plugins
from plugins.path_view_plugin import PathViewPlugin  # Assuming the plugin is in a 'plugins' directory
from plugins.carpose_plugin import CarPosePlugin

# Add the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

        
def main():    
    # Global settings
    _config = Config()
    

    # GUI - Set up the application and main window
    app = pg.mkQApp("Path Regression Analysis")
    win = QtWidgets.QMainWindow()
    
    # Create the main window's control UI components, but no window or layout
    # View menu actions
    menu_setup_res = setup_menus(win, app, _config)
    d_control, d_spatial_plot, d_temporal_plot, d_slider, controls_widget, _ui_config_elements, _ui_display_elements, main_scope  = menu_setup_res
    
        
    # Connect signals                  
    connect_signals(_ui_config_elements, _ui_display_elements, main_scope)                    
                     
    # Add plots to plot docks
    plot_spatial = pg.PlotWidget(title="Spatial Plot")
    plot_temporal = pg.PlotWidget(title="Temporal Plot")
    plot_spatial.plot(np.random.normal(size=100))  # Placeholder plot data
    plot_temporal.plot(np.random.normal(size=100), np.random.normal(size=100) )  # Placeholder plot data
    
    # connect the plots to the main_scope dock
    d_control.addWidget(controls_widget)
    d_spatial_plot.addWidget(plot_spatial)
    d_temporal_plot.addWidget(plot_temporal)
    
    # Initialize the main plugins application
    regression_app = MainPathRegression(d_slider)

    ############################################################################################
    # REGISTER PLUGINS
    # adding carpose plugin
    carpose_plugin = CarPosePlugin()
    regression_app.load_plugins([carpose_plugin])
    
    # Adding pathview plugin 
    driving_path_view_plugin = PathViewPlugin()
    regression_app.load_plugins([driving_path_view_plugin]) 
    
    
    ############################################################################################
    
    # Run the application with a given trip path
    trip_pat1, _ = parse_arguments()
    regression_app.run(trip_pat1, plot_spatial)
       
    
    # Update plots based on calculations
    # calculate_virtual_path(plot1, ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2'))

    # Show the main window
    win.show()
    app.exec()
    
    # Access the calculated result after the event loop
    calculated_result = main_scope.get('calculated_result')
    if calculated_result is not None:
        print("Calculated Result:", calculated_result)


# Start the Qt event loop
if __name__ == '__main__':
    main()
