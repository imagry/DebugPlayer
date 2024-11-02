from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QComboBox, QCheckBox, QHBoxLayout, QMenu, QMenuBar, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, Signal
from gui.custom_plot_widget import SpatialPlotWidget, TemporalPlotWidget
from gui.timestamp_slider import TimestampSlider
from core.plot_manager import PlotManager
from core.config import spatial_signals, temporal_signals  # Import signal lists from config
from PySide6.QtGui import QAction

# Define global list for spatial signals
spatial_signals = ["car_pose(t)", "route", "path_in_world_coordinates(t)"]
# temporal_signal_names = ["current_speed","current_steering","driving_mode","target_speed","target_steering_angle"]
temporal_signals = [
    "current_steering",
    "current_speed",
    "driving_mode",
    "target_speed",
    "target_steering_angle"
    # "all_steering_data",
    # "all_current_speed_data",
    # "all_driving_mode_data",
    # "all_target_speed_data",
    # "all_target_steering_angle_data"
]


def create_main_window(plot_manager: PlotManager) -> tuple[QMainWindow, PlotManager]:
    win = QMainWindow()
    win.resize(1200, 800)
    win.setWindowTitle('Motion Planning Playback Debug Tool')

    current_timestamp = 0  # Initialize the current timestamp

    # Create and wrap the plots in QDockWidgets
    plots_and_docks = setup_plot_docks(win, plot_manager)

    # Extract individual plots and docks
    car_pose_plot, car_signals_plot = plots_and_docks['plots']
    car_pose_dock, car_signals_dock = plots_and_docks['docks']

    # Set up the menu bar with enhanced user interaction options
    setup_menu_bar(win, plot_manager, [car_pose_plot, car_signals_plot], current_timestamp)

    # Create Timestamp Slider with compact placement
    setup_timestamp_slider(win, plot_manager, current_timestamp)

    # Tabify the car pose and car signals dock widgets to appear as tabs
    win.tabifyDockWidget(car_pose_dock, car_signals_dock)

    # Ensure both docks are visible and initially focus on one of them
    car_pose_dock.raise_()
    car_pose_dock.show()
    car_signals_dock.show()

    # Maximize the plot area after setup to ensure plots get the most space
    win.showMaximized()

    return win, plot_manager


def setup_plot_docks(win: QMainWindow, plot_manager: PlotManager) -> dict[str, list]:
   
    # Directly reference the centralized widgets in PlotManager
    car_pose_plot = plot_manager.spatial_plot_widget
    car_signals_plot = plot_manager.temporal_plot_widget
    
    # Set up dock widgets
    car_pose_dock = QDockWidget("Car Pose Plot", win)
    car_pose_dock.setObjectName("CarPosePlotDock")
    car_pose_dock.setWidget(car_pose_plot)
    car_pose_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)  # Allow docking and closing
    win.addDockWidget(Qt.RightDockWidgetArea, car_pose_dock)

    car_signals_dock = QDockWidget("Car Signals", win)
    car_signals_dock.setObjectName("CarSignalsPlotDock")
    car_signals_dock.setWidget(car_signals_plot)
    car_signals_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    win.addDockWidget(Qt.RightDockWidgetArea, car_signals_dock)

    # Register the widgets with the plot manager, but without recreating them for each signal
    for signal in spatial_signals:
        plot_manager.register_plot(signal)
        # plot_manager.assign_signal_to_plot(car_pose_plot, signal)

        
    for signal in temporal_signals:
        plot_manager.register_plot(signal)
        # plot_manager.assign_signal_to_plot(car_signals_plot, signal)

    
    return {'plots': [car_pose_plot, car_signals_plot], 'docks': [car_pose_dock, car_signals_dock]}


def setup_menu_bar(win, plot_manager, plots, current_timestamp):
    menubar = QMenuBar(win)
    win.setMenuBar(menubar)

    # View Menu for Loading/Removing Signals
    view_menu = menubar.addMenu("View")

    load_signal_menu = QMenu("Load Signals", win)
    view_menu.addMenu(load_signal_menu)

    # Add checkboxes for each available signal
    for signal in plot_manager.signal_plugins.keys():
        signal_action = QAction(signal, win)
        signal_action.setCheckable(True)
        signal_action.setChecked(any(signal in plot.signals for plot in plots))
        signal_action.triggered.connect(lambda checked, s=signal: toggle_signal_visibility(plot_manager, plots, s, checked, current_timestamp))
        load_signal_menu.addAction(signal_action)


def setup_timestamp_slider(win, plot_manager, current_timestamp):
    if "timestamps" in plot_manager.signal_plugins:
        timestamps = plot_manager.plugins["CarPosePlugin"].signals["timestamps"]["func"]()  # Fetch timestamps from the CarPosePlugin - use () to call the lambda
    else:
        timestamps = []  # Fallback in case no plugin provides timestamps

    def update_timestamp(new_timestamp):
        nonlocal current_timestamp
        current_timestamp = new_timestamp  # Update the current timestamp
        plot_manager.request_data(current_timestamp)

    # Create Timestamp Slider Dock
    slider_dock = QDockWidget("", win)  # No title bar
    slider_dock.setObjectName("TimestampSliderDock")
    slider_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)  # Allow movement and floating

    slider = TimestampSlider(plot_manager, timestamps)
    slider.timestamp_changed.connect(update_timestamp)
    slider_dock.setWidget(slider)

    # Remove the title bar for a more compact layout
    slider_dock.setTitleBarWidget(QWidget())

    # Set a small minimum size for the dock
    slider_dock.setMinimumHeight(50)  # Reduced height to take up minimal space
    slider_dock.setMaximumHeight(60)  # Set a maximum to prevent it from expanding too much

    # Add the dock to the bottom area
    win.addDockWidget(Qt.BottomDockWidgetArea, slider_dock)

    # Correct the size policy to use QSizePolicy
    slider_dock.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)


def toggle_signal_visibility(plot_manager, plots, signal, visible, current_timestamp):
    for plot in plots:
        if visible:
            if signal not in plot.signals:
                plot.signals.append(signal)
                plot_manager.assign_signal_to_plot(plot, signal)
                plot_manager.request_data(current_timestamp)
        else:
            if signal in plot.signals:
                plot.signals.remove(signal)
                plot_manager.remove_signal_from_plot(plot, signal)
                plot.plot_data()
