from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QComboBox, QCheckBox, QHBoxLayout, QMenu, QMenuBar, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, Signal
from gui.custom_plot_widget import CustomPlotWidget
from gui.timestamp_slider import TimestampSlider
from core.plot_manager import PlotManager
from PySide6.QtGui import QAction

# Define global list for spatial signals
spatial_signal_names = ["car_pose(t)", "route", "path_in_world_coordinates(t)"]
temporal_signal_names = ["speed","steering","driving_mode","traget_speed","target_steering"]

def create_main_window(plot_manager):
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


def setup_plot_docks(win, plot_manager):
    car_pose_plot = CustomPlotWidget(signal_names=spatial_signal_names, default_visible_signals=spatial_signal_names)
    car_signals_plot = CustomPlotWidget(signal_names= temporal_signal_names, default_visible_signals = temporal_signal_names)

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

    plot_manager.register_plot(car_pose_plot)
    plot_manager.register_plot(car_signals_plot)

    return {'plots': [car_pose_plot, car_signals_plot], 'docks': [car_pose_dock, car_signals_dock]}


def setup_menu_bar(win, plot_manager, plots, current_timestamp):
    menubar = QMenuBar(win)
    win.setMenuBar(menubar)

    # View Menu for Loading/Removing Signals
    view_menu = menubar.addMenu("View")

    load_signal_menu = QMenu("Load Signals", win)
    view_menu.addMenu(load_signal_menu)

    # Add checkboxes for each available signal
    for signal_name in plot_manager.signal_plugins.keys():
        signal_action = QAction(signal_name, win)
        signal_action.setCheckable(True)
        signal_action.setChecked(any(signal_name in plot.signal_names for plot in plots))
        signal_action.triggered.connect(lambda checked, s=signal_name: toggle_signal_visibility(plot_manager, plots, s, checked, current_timestamp))
        load_signal_menu.addAction(signal_action)


def setup_timestamp_slider(win, plot_manager, current_timestamp):
    if "timestamps" in plot_manager.signal_plugins:
        timestamps = plot_manager.plugins["CarPosePlugin"].signals["timestamps"]
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


def toggle_signal_visibility(plot_manager, plots, signal_name, visible, current_timestamp):
    for plot in plots:
        if visible:
            if signal_name not in plot.signal_names:
                plot.signal_names.append(signal_name)
                plot_manager.assign_signal_to_plot(plot, signal_name)
                plot_manager.request_data(current_timestamp)
        else:
            if signal_name in plot.signal_names:
                plot.signal_names.remove(signal_name)
                plot_manager.remove_signal_from_plot(plot, signal_name)
                plot.plot_data()
