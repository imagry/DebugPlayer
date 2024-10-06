from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from gui.custom_plot_widget import CustomPlotWidget
from gui.timestamp_slider import TimestampSlider
from core.plot_manager import PlotManager
from gui.menu_bar import setup_menu_bar

def create_main_window(car_pose_plugin):
    win = QMainWindow()  # Create the main window object
    win.resize(1200, 800)  # Resize the main window
    win.setWindowTitle('Motion Planning Playback Debug Tool')  # Set the window title
  
    # Initialize the PlotManager
    plot_manager = PlotManager()

    # Register the car_pose plugin with the PlotManager
    plot_manager.register_plugin("car_pose", car_pose_plugin)

    # Save the initial layout
    def save_layout():
        win.saved_layout = win.saveState()

    # Restore the saved layout
    def restore_layout():
        if hasattr(win, 'saved_layout'):
            win.restoreState(win.saved_layout)
                        
   # Add a method to toggle the control panel
    def toggle_control_panel():
        if d1.isHidden():
            d1.show()
        else:
            d1.hide()
            
    # Attach restore_layout and save_layout to window object
    win.save_layout = save_layout
    win.restore_layout = restore_layout
    
    # Attach toggle_control_panel to the window object so the menu can access it
    win.toggle_control_panel = toggle_control_panel
    
    # Set up the menu bar
    setup_menu_bar(win)  # Call the setup function from menu_bar.py   

   # Create the Control Panel as d1 (dockable widget)
    d1 = QDockWidget("Control Panel", win)
    control_panel_widget = QWidget()
    control_panel_layout = QVBoxLayout(control_panel_widget)  # Add layout to control panel
    # Add widgets to control panel layout as needed...
    d1.setWidget(control_panel_widget)
    d1.setFixedWidth(200)  # Make the control panel narrow
    win.addDockWidget(Qt.LeftDockWidgetArea, d1)

    # Create Car Pose Plot as d2
    d2 = QDockWidget("Car Pose Plot", win)
    car_pose_plot = CustomPlotWidget(signal_names=["car_pose(t)", "route"])
    d2.setWidget(car_pose_plot)
    win.addDockWidget(Qt.RightDockWidgetArea, d2)

    # Create Route Plot as d3
    d3 = QDockWidget("Route Plot", win)
    route_plot = CustomPlotWidget(signal_names=["route"])
    d3.setWidget(route_plot)
    win.addDockWidget(Qt.RightDockWidgetArea, d3)

    # Make sure d3 is below d2 (vertically stacked)
    win.splitDockWidget(d2, d3, Qt.Vertical)

    # Register the plots with the PlotManager
    plot_manager.register_plot(car_pose_plot)  # Automatically fetch signal_names from the widget
    plot_manager.register_plot(route_plot)     # Automatically fetch signal_names from the widget

    # Create TimestampSlider as d4
    d4 = QDockWidget("Timestamp Slider", win)
    slider = TimestampSlider(plot_manager, car_pose_plugin.timestamps)  # Initialize slider with timestamps
    d4.setWidget(slider)
    d4.setFixedHeight(100)  # Set a height for the slider dock
    win.addDockWidget(Qt.BottomDockWidgetArea, d4)

    save_layout()  # Save the default layout state after initialization
    
    return win, plot_manager  # Return the window and the PlotManager

