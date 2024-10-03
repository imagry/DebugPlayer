# menu_setup.py
import os
import sys
from PySide6.QtGui import QAction  # Import QAction from PySide6.QtGui
from pyqtgraph.dockarea import Dock
from pyqtgraph.dockarea import DockArea, Dock

from path_regression.data_handlers import create_path_regressors
from path_regression.ui_components import create_main_window
from config import Config


def setup_menus(win, app, _config):
    
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
    toggle_controls_action.triggered.connect(lambda: toggle_controls(d_control, toggle_controls_action))
    show_slider_action.triggered.connect(lambda: toggle_slider(d_slider, show_slider_action))

    # Create docks
    d_control = Dock("Controls", size=(300, 200))  # Dock for buttons, input fields
    d_spatial_plot = Dock("Plot 1", size=(500, 400))  # Dock for the first plot
    d_temporal_plot = Dock("Plot 2", size=(500, 400))  # Dock for the second plot
    d_slider = Dock("Slider", size=(500, 200))  # Dock for the timestamp slider
    
    # Add docks to DockArea
    area.addDock(d_control, 'left')  # controls
    area.addDock(d_spatial_plot, 'right')  # plot 1
    area.addDock(d_temporal_plot, 'bottom', d_spatial_plot)  # plot 2
    area.addDock(d_slider, 'bottom', d_control)
    
    # Set up UI components and add the controls widget to the controls dock
    controls_widget, ui_elements, ui_display_elements = create_main_window()
               
    # Path Regressor  
    main_scope = create_path_regressors(ui_elements, _config.is_caching_mode_enabled(),
                                        _config.get_cache_dir(), _config.get_max_workers())
    
    # Define functions for the menu actions    
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
    
    return d_control, d_spatial_plot, d_temporal_plot, d_slider, controls_widget, ui_elements, ui_display_elements, main_scope