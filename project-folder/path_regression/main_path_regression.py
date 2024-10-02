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

from data_handlers import load_data, parse_arguments, create_path_regressors
from ui_components import create_main_window, connect_signals, TimestampSlider
from plot_functions import save_figure
from DataClasses.PathRegressor import PathRegressor
from plugin_registry import PluginRegistry
from api_interfaces import UserPluginInterface
from plot_functions import calculate_virtual_path

# Add the root directory of the project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class MainPathRegression:
    def __init__(self):
        # Initialize the plugin registry and backbone data
        self.plugin_registry = PluginRegistry()
        self.backbone_data = {}

        # Initialize the slider with a dummy range, min_time and max_time can be adjusted
        self.timestamp_slider = TimestampSlider(min_time=0, max_time=1000)  
        # Connect the slider's sync mechanism to the sync function in the backbone
        self.timestamp_slider.sync_data = self.sync_plugins_with_timestamp

    def load_plugins(self, plugins):
        """Register user plugins."""
        for plugin in plugins:
            self.plugin_registry.register_plugin(plugin)
            
    def sync_plugins_with_timestamp(self, timestamp):
        """Sync all registered plugins with the selected timestamp."""
        print(f"Syncing all plugins with timestamp {timestamp}")
        # Sync all registered plugins based on the timestamp
        for plugin in self.plugin_registry.plugins:
            plugin.sync_data_with_timestamp(timestamp, self.backbone_data)


    def run(self, file_paths: dict, display_options: dict):
        # Load and sync data
        print("Loading and syncing data...")
        self.plugin_registry.load_all_plugins(file_paths)
        self.plugin_registry.sync_all_plugins(self.backbone_data)

        # Display the GUI components for all plugins
        self.plugin_registry.display_all_plugins(display_options)

        # Display the timestamp slider
        self.timestamp_slider.show()

        
        
def main():    
    # Global settings
    cpu_num = multiprocessing.cpu_count() 
    MAX_WORKERS = np.floor(cpu_num * 0.8)
    CACHE_DIR = os.path.join(os.path.dirname(parent_dir), "personal-folder", "cache")
    caching_mode_enabled = True

    # GUI - Set up the application and main window
    app = pg.mkQApp("Path Regression Analysis")
    win = QtWidgets.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)
    win.resize(1000, 600)
    win.setWindowTitle('Path Regression DockArea Interface')
    
    # Create a menu bar at the top
    menu_bar = win.menuBar()
    
    # Add menus to the menu bar
    file_menu = menu_bar.addMenu("File")
    view_menu = menu_bar.addMenu("View")
    widgets_menu = menu_bar.addMenu("Widgets")
    help_menu = menu_bar.addMenu("Help")
    
    # File menu actions
    open_action = QAction("Open", win)
    save_action = QAction("Save", win)
    exit_action = QAction("Exit", win)
    file_menu.addAction(open_action)
    file_menu.addAction(save_action)
    file_menu.addSeparator()
    file_menu.addAction(exit_action)
    
    # View menu actions
    toggle_controls_action = QAction("Toggle Controls", win, checkable=True)
    view_menu.addAction(toggle_controls_action)
    
    # Widgets menu
    show_slider_action = QAction("Show Slider", win, checkable=True)
    widgets_menu.addAction(show_slider_action)

    # Help menu actions
    about_action = QAction("About", win)
    help_menu.addAction(about_action)
    
    # Define what happens when actions are triggered
    exit_action.triggered.connect(app.quit)  # Exit the app when Exit is triggered
    toggle_controls_action.triggered.connect(lambda: toggle_controls(d1, toggle_controls_action))
    show_slider_action.triggered.connect(lambda: toggle_slider(d4, show_slider_action))


    # Create docks
    d1 = Dock("Controls", size=(300, 200))  # Dock for buttons, input fields
    d2 = Dock("Plot 1", size=(500, 400))  # Dock for the first plot
    d3 = Dock("Plot 2", size=(500, 400))  # Dock for the second plot
    d4 = Dock("Slider", size=(500, 200))  # Dock for the timestamp slider
    
    # Add docks to DockArea
    area.addDock(d1, 'left')
    area.addDock(d2, 'right')
    area.addDock(d3, 'bottom', d2)
    area.addDock(d4, 'bottom', d1)
    
    
    # Set up UI components and add the controls widget to the controls dock
    controls_widget, ui_elements, ui_display_elements = create_main_window()
    d1.addWidget(controls_widget)
    
    # Setup the timestamp slider dock
    regression_app = MainPathRegression()
    d4.addWidget(regression_app.timestamp_slider)
    
    # Data Handling
    trip_path1, trip_path2 = parse_arguments()
    PathObj1, df_car_pose1 = load_data(trip_path1, caching_mode_enabled, CACHE_DIR)
    if trip_path2 is not None:
        PathObj2, df_car_pose2 = load_data(trip_path2, caching_mode_enabled, CACHE_DIR)
    else:    
        PathObj2 = None
        df_car_pose2 = None
        print("Only one trip is loaded.")

    # Path Regressor  
    main_scope = create_path_regressors(ui_elements, PathObj1, trip_path1, df_car_pose1, PathObj2, trip_path2, df_car_pose2, CACHE_DIR, MAX_WORKERS)
    
      # Add toggle button to show/hide controls dock
    toggle_button = QtWidgets.QPushButton("Hide Controls")
    
    def toggle_controls(dock, action):
        if dock.isVisible():
            dock.hide()  # Hide the dock if visible
            action.setChecked(False)
        else:
            dock.show()  # Show the dock if hidden
            action.setChecked(True)
    
    def toggle_slider(dock, action):
        if dock.isVisible():
            dock.hide()
            action.setChecked(False)
        else:
            dock.show()
            action.setChecked(True)

    toggle_button.clicked.connect(lambda: toggle_controls(d1, toggle_controls_action))

    # Add the toggle button to the dock for the controls
    controls_layout = controls_widget.layout()
    controls_layout.addWidget(toggle_button)
                
    # Add the toggle button to the dock for the controls
    controls_layout = controls_widget.layout()
    controls_layout.addWidget(toggle_button)
    
    # add to ui elements the item CACHE_DIR with value CACHE_DIR
    ui_elements['CACHE_DIR'] = CACHE_DIR
    ui_elements['MAX_WORKERS'] = MAX_WORKERS
        
    # Connect signals
    display_trips1_checkbox_button = ui_display_elements['display_trips1_checkbox']
    display_trips2_checkbox_button = ui_display_elements['display_trips2_checkbox']
    display_carpose_checkbox_button = ui_display_elements['display_carpose_checkbox']
    
    connect_signals(run_button=ui_elements['run_button'], 
                    load_button1=ui_elements['load_button1'],
                    load_button2=ui_elements['load_button2'],
                    update_plot_button=ui_elements['update_plot_button'], 
                    save_button=ui_elements['save_button'], 
                    ui_elements=ui_elements, 
                    main_scope=main_scope, 
                    ui_display_elements=ui_display_elements, 
                    display_trips1_checkbox_button=display_trips1_checkbox_button, 
                    display_trips2_checkbox_button=display_trips2_checkbox_button, 
                    display_carpose_checkbox_button=display_carpose_checkbox_button)

    # Add plots to plot docks
    plot1 = pg.PlotWidget(title="Path Plot 1")
    plot2 = pg.PlotWidget(title="Path Plot 2")
    plot1.plot(np.random.normal(size=100))  # Placeholder plot data
    plot2.plot(np.random.normal(size=100))  # Placeholder plot data

    
    d2.addWidget(plot1)
    d3.addWidget(plot2)
    
    # Update plots based on calculations
    calculate_virtual_path(plot1, ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2'))

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
