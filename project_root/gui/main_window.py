from PySide6 import QtWidgets
from pyqtgraph.dockarea import DockArea, Dock
from gui.custom_plot_widget import CustomPlotWidget
from gui.timestamp_slider import TimestampSlider
from core.plot_manager import PlotManager  # Use PlotManager


def create_main_window(car_pose_plugin):
    win = QtWidgets.QMainWindow()  # Create the main window object
    area = DockArea()  # Create a DockArea to hold docks/widgets
    win.setCentralWidget(area)  # Set the dock area as the central widget
    win.resize(1000, 600)  # Resize the main window
    win.setWindowTitle('Motion Planning Playback Debug Tool')  # Set the window title

    # Initialize the PlotManager
    plot_manager = PlotManager()
    
    # Register the car_pose plugin with the PlotManager
    plot_manager.register_plugin("car_pose", car_pose_plugin)

    # Create the control dock
    d1 = Dock("Controls", size=(300, 200))  # Create a dock for controls
    area.addDock(d1, 'left')  # Add the dock to the dock area (on the left)

    # Create the plot dock for car pose
    d2 = Dock("Car Pose Plot", size=(500, 400))  # Create a dock for the plot
    area.addDock(d2, 'right')  # Add the dock to the dock area (on the right)

    # Create the plot dock for route
    d3 = Dock("Route Plot", size=(500, 400))  # Create another dock for route plot
    area.addDock(d3, 'bottom', d2)  # Add the dock to the bottom of d2

    # Create the TimestampSlider dock
    d4 = Dock("Timestamp Slider", size=(500, 100))  # Create a dock for the slider
    area.addDock(d4, 'bottom', d1)  # Add the dock to the bottom of the control dock

    # Initialize CustomPlotWidget and register signals
    car_pose_plot = CustomPlotWidget(signal_names=["car_pose(t)", "route"])
    route_plot = CustomPlotWidget(signal_names=["route"])

    # Register the plots with the PlotManager
    plot_manager.register_plot(car_pose_plot)  # Automatically fetch signal_names from the widget
    plot_manager.register_plot(route_plot)     # Automatically fetch signal_names from the widget

    # Add the plots to their respective docks
    d2.addWidget(car_pose_plot)
    d3.addWidget(route_plot)

   # Now that we have loaded plugins, use the actual timestamps from the car_pose_plugin
    timestamps = car_pose_plugin.timestamps # Get timestamps from the plugin in ms

    # Initialize the TimestampSlider and connect it to the PlotManager
    slider = TimestampSlider(plot_manager, timestamps)
    d4.addWidget(slider)  # Add the slider to the dock

    return win, plot_manager  # Return the window and the PlotManager

