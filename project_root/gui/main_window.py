import os
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

from PySide6.QtWidgets import (QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QMenu, QMenuBar, 
                           QMessageBox, QSizePolicy, QLabel, QPushButton, QTabWidget, QToolBar, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon
from typing import Dict, List, Optional, Tuple, Any

from core.plot_manager import PlotManager
from core.view_manager import ViewManager
from gui.timestamp_slider import TimestampSlider
from core.signal_registry import SignalRegistry
from core.bookmark_manager import BookmarkManager
from gui.bookmark_panel import BookmarkPanel
from gui.minimap_widget import MinimapWidget
from gui.signal_filter_panel import SignalFilterPanel

# Constants for view types
VIEW_TYPE_TEMPORAL = 'temporal'
VIEW_TYPE_SPATIAL = 'spatial'
VIEW_TYPE_TABLE = 'table'

# Default configurations for views
DEFAULT_TEMPORAL_CONFIG = {
    'time_window': 10.0,  # Default time window in seconds
    'show_grid': True,
    'show_legend': True,
    'auto_range': True
}

DEFAULT_SPATIAL_CONFIG = {
    'show_grid': True,
    'show_axes': True,
    'show_legend': True,
    'auto_range': True,
    'aspect_locked': True  # Keep aspect ratio 1:1 for spatial views
}

# Import view classes
from views.temporal_view import TemporalView
from views.spatial_view import SpatialView

# Import signal lists from config for backward compatibility
from core.config import spatial_signals, temporal_signals

# Constants for view types
VIEW_TYPE_TEMPORAL = 'temporal'
VIEW_TYPE_SPATIAL = 'spatial'
VIEW_TYPE_TABLE = 'table'

# Default view configurations
DEFAULT_SPATIAL_CONFIG = {
    "title": "Vehicle Position",
    "x_label": "X",
    "y_label": "Y",
    "aspect_locked": True,
    "show_grid": True
}

DEFAULT_TEMPORAL_CONFIG = {
    "title": "Vehicle Signals",
    "x_label": "Time",
    "y_label": "Value",
    "y_range": [-1, 1]  # Default range, will adjust automatically
}


def create_main_window(plot_manager: PlotManager) -> tuple[QMainWindow, PlotManager, ViewManager]:
    """
    Create the main application window using the ViewManager for flexible layout management.
    
    Args:
        plot_manager: The PlotManager instance managing signal data flow
        
    Returns:
        Tuple containing the main window, plot manager, and view manager
    """
    # Create main window
    win = QMainWindow()
    win.resize(1200, 800)
    win.setWindowTitle('Motion Planning Playback Debug Tool')
    
    # Initialize the view manager
    view_manager = ViewManager()
    
    # Create bookmark manager with save path
    save_dir = os.path.join(os.path.expanduser("~"), ".debug_player")
    os.makedirs(save_dir, exist_ok=True)
    bookmark_path = os.path.join(save_dir, "bookmarks.json")
    bookmark_manager = BookmarkManager(save_path=bookmark_path)
    
    # Register view types
    view_manager.register_view_class(VIEW_TYPE_TEMPORAL, TemporalView)
    view_manager.register_view_class(VIEW_TYPE_SPATIAL, SpatialView)
    
    # Create the default view templates
    view_manager.register_template('spatial_default', {
        'type': VIEW_TYPE_SPATIAL,
        'config': DEFAULT_SPATIAL_CONFIG,
        'signals': []  # Will be populated later
    })
    
    view_manager.register_template('temporal_default', {
        'type': VIEW_TYPE_TEMPORAL,
        'config': DEFAULT_TEMPORAL_CONFIG,
        'signals': []  # Will be populated later
    })
    
    # Initialize current timestamp
    current_timestamp = 0.0
    
    # Create and setup views and docks
    view_docks = setup_view_docks(win, plot_manager, view_manager)
    
    # Create bookmark panel
    bookmark_dock, bookmark_panel = setup_bookmark_panel(win, bookmark_manager, current_timestamp)
    
    # Create minimap for timeline navigation
    minimap_dock, minimap = setup_minimap(win, plot_manager, bookmark_manager, current_timestamp)
    
    # Create signal filter panel
    filter_dock, filter_panel = setup_signal_filter_panel(win, plot_manager.signal_registry, view_manager)
    
    # Set up the menu bar with new features
    setup_menu_bar(win, plot_manager, view_manager, current_timestamp)
    
    # Create Timestamp Slider
    slider = setup_timestamp_slider(win, plot_manager, view_manager, current_timestamp)
    
    # Connect navigation components together
    bookmark_panel.bookmark_selected.connect(slider.set_timestamp)
    minimap.navigation_requested.connect(slider.set_timestamp)
    
    # Update bookmark panel and minimap when timestamp changes
    slider.timestamp_changed.connect(bookmark_panel.set_current_timestamp)
    slider.timestamp_changed.connect(minimap.set_current_timestamp)
    
    # Initialize the signal filter panel with available signals
    filter_panel.refresh_signals()
    
    # Extract docks for layout management
    spatial_dock = view_docks.get('spatial_dock')
    temporal_dock = view_docks.get('temporal_dock')
    
    # Tabify the docks
    if spatial_dock and temporal_dock:
        win.tabifyDockWidget(spatial_dock, temporal_dock)
        spatial_dock.raise_()
        spatial_dock.show()
        temporal_dock.show()
    
    # Layout bookmark dock and view docks side-by-side
    win.splitDockWidget(bookmark_dock, spatial_dock, Qt.Horizontal)
    
    # Maximize the window
    win.showMaximized()
    
    return win, plot_manager, view_manager


def setup_signal_filter_panel(win: QMainWindow, signal_registry: SignalRegistry, view_manager: ViewManager) -> Tuple[QDockWidget, SignalFilterPanel]:
    """
    Set up the signal filter panel for searching and filtering signals.
    
    Args:
        win: Main window to add the panel to
        signal_registry: SignalRegistry instance
        view_manager: ViewManager instance
        
    Returns:
        Tuple of (dock widget, signal filter panel instance)
    """
    # Create signal filter panel
    filter_panel = SignalFilterPanel(signal_registry, win)
    
    # Connect signal selection changes to view updates
    filter_panel.signal_selection_changed.connect(
        lambda signals: view_manager.update_view_signals(signals)
    )
    
    # Create dock widget for the filter panel
    filter_dock = QDockWidget("Signal Filters", win)
    filter_dock.setObjectName("SignalFilterDock")
    filter_dock.setWidget(filter_panel)
    filter_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    win.addDockWidget(Qt.RightDockWidgetArea, filter_dock)
    
    return filter_dock, filter_panel

def setup_bookmark_panel(win: QMainWindow, bookmark_manager: BookmarkManager, current_timestamp: float) -> Tuple[QDockWidget, BookmarkPanel]:
    """
    Set up the bookmark panel for saving and navigating to important timestamps.
    
    Args:
        win: Main window to add the panel to
        bookmark_manager: BookmarkManager instance
        current_timestamp: Initial timestamp value
        
    Returns:
        Tuple of (dock widget, bookmark panel instance)
    """
    # Create bookmark panel
    bookmark_panel = BookmarkPanel(win, bookmark_manager)
    bookmark_panel.set_current_timestamp(current_timestamp)
    
    # Create dock widget for bookmark panel
    bookmark_dock = QDockWidget("Bookmarks", win)
    bookmark_dock.setObjectName("BookmarkDock")
    bookmark_dock.setWidget(bookmark_panel)
    bookmark_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    win.addDockWidget(Qt.LeftDockWidgetArea, bookmark_dock)
    
    return bookmark_dock, bookmark_panel
    

def setup_minimap(win: QMainWindow, plot_manager: PlotManager, bookmark_manager: BookmarkManager, current_timestamp: float) -> Tuple[QDockWidget, MinimapWidget]:
    """
    Set up the minimap for navigating through the timeline.
    
    Args:
        win: Main window to add the minimap to
        plot_manager: PlotManager instance
        bookmark_manager: BookmarkManager instance
        current_timestamp: Initial timestamp value
        
    Returns:
        Tuple of (dock widget, minimap instance)
    """
    # Create minimap widget
    minimap = MinimapWidget(win, bookmark_manager)
    minimap.set_current_timestamp(current_timestamp)
    
    # Add some example data for the minimap
    # In a real application, this would come from the actual signal data
    timestamps = np.arange(0, 100.1, 0.1)
    values1 = np.sin(timestamps / 5.0) * 10 + 50  # Sine wave
    values2 = np.cos(timestamps / 3.0) * 20 + 30  # Cosine wave
    
    try:
        minimap.add_data_series("sine", timestamps, values1)
        minimap.add_data_series("cosine", timestamps, values2)
    except Exception as e:
        print(f"Error adding data to minimap: {str(e)}")
    
    # Set initial view range (10 seconds)
    minimap.set_view_range(0, 10)
    
    # Create dock widget for minimap
    minimap_dock = QDockWidget("Timeline Overview", win)
    minimap_dock.setObjectName("MinimapDock")
    minimap_dock.setWidget(minimap)
    minimap_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    win.addDockWidget(Qt.BottomDockWidgetArea, minimap_dock)
    
    return minimap_dock, minimap


def setup_view_docks(win: QMainWindow, plot_manager: PlotManager, view_manager: ViewManager) -> dict[str, QDockWidget]:
    """
    Set up view docks using the ViewManager.
    
    This function creates the main views (spatial and temporal) and wraps them in dock widgets
    for flexible UI layout. It also connects signals to the appropriate views based on their type.
    
    Args:
        win: Main window to add docks to
        plot_manager: PlotManager instance
        view_manager: ViewManager instance
        
    Returns:
        Dictionary mapping view names to their dock widgets
    """
    # Create view instances from templates
    spatial_view = view_manager.create_view_from_template('spatial_view', 'spatial_default')
    temporal_view = view_manager.create_view_from_template('temporal_view', 'temporal_default')
    
    # Get the QWidgets for the views
    spatial_widget = spatial_view.get_widget()
    temporal_widget = temporal_view.get_widget()
    
    # Create dock widgets
    spatial_dock = QDockWidget("Vehicle Position", win)
    spatial_dock.setObjectName("SpatialViewDock")
    spatial_dock.setWidget(spatial_widget)
    spatial_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    win.addDockWidget(Qt.RightDockWidgetArea, spatial_dock)
    
    temporal_dock = QDockWidget("Vehicle Signals", win)
    temporal_dock.setObjectName("TemporalViewDock")
    temporal_dock.setWidget(temporal_widget)
    temporal_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    win.addDockWidget(Qt.RightDockWidgetArea, temporal_dock)
    
    # Connect signals to views and register them with the plot manager
    # First, get all registered signals from the signal registry
    temporal_signals = plot_manager.signal_registry.get_signals_by_type("temporal")
    spatial_signals = plot_manager.signal_registry.get_signals_by_type("spatial")
    
    # Register all signals from the registry
    all_signals = temporal_signals + spatial_signals
    
    # Make sure plot widgets know about these signals
    for signal in all_signals:
        provider = plot_manager.signal_registry.signal_providers.get(signal)
        if provider:
            signal_type = plot_manager.signal_registry.get_signal_type(signal)
            if signal_type == "temporal":
                plot_manager.temporal_plot_widget.register_signal(signal)
            elif signal_type == "spatial":
                plot_manager.spatial_plot_widget.register_signal(signal)
    
    # Connect temporal signals to temporal view
    for signal in temporal_signals:
        view_manager.connect_signal_to_view(signal, 'temporal_view')
    
    # Connect spatial signals to spatial view
    for signal in spatial_signals:
        view_manager.connect_signal_to_view(signal, 'spatial_view')
    
    # For backward compatibility, process legacy signals
    # This can be removed once the transition to SignalRegistry is complete
    for signal, info in plot_manager.signal_plugins.items():
        signal_type = info.get("type", "temporal")
        
        # Register with plot widgets if not already registered
        if signal_type == "temporal":
            plot_manager.temporal_plot_widget.register_signal(signal)
            if signal not in temporal_signals:
                view_manager.connect_signal_to_view(signal, 'temporal_view')
        elif signal_type == "spatial":
            plot_manager.spatial_plot_widget.register_signal(signal)
            if signal not in spatial_signals:
                view_manager.connect_signal_to_view(signal, 'spatial_view')
    
    return {
        'spatial_dock': spatial_dock,
        'temporal_dock': temporal_dock,
        'spatial_view_id': 'spatial_view',
        'temporal_view_id': 'temporal_view'
    }


def setup_menu_bar(win, plot_manager, view_manager, current_timestamp):
    """
    Set up the menu bar with various options for the application.
    
    Args:
        win: Main window to add menu bar to
        plot_manager: PlotManager instance
        view_manager: ViewManager instance
        current_timestamp: Initial timestamp value
    """
    menubar = QMenuBar(win)
    win.setMenuBar(menubar)
    
    # Signal Menu for managing signal visibility
    signal_menu = menubar.addMenu("Signals")
    
    # Create submenus for temporal and spatial signals
    temporal_menu = QMenu("Temporal Signals", win)
    spatial_menu = QMenu("Spatial Signals", win)
    signal_menu.addMenu(temporal_menu)
    signal_menu.addMenu(spatial_menu)
    
    # Get signals by type from the registry
    temporal_signals = plot_manager.signal_registry.get_signals_by_type("temporal")
    spatial_signals = plot_manager.signal_registry.get_signals_by_type("spatial")
    
    # Add temporal signal actions
    for signal in temporal_signals:
        signal_action = QAction(signal, win)
        signal_action.setCheckable(True)
        signal_action.setChecked(True)  # Default to visible
        signal_action.triggered.connect(
            lambda checked, s=signal: toggle_signal_in_view(view_manager, 'temporal_view', s, checked)
        )
        temporal_menu.addAction(signal_action)
    
    # Add spatial signal actions
    for signal in spatial_signals:
        signal_action = QAction(signal, win)
        signal_action.setCheckable(True)
        signal_action.setChecked(True)  # Default to visible
        signal_action.triggered.connect(
            lambda checked, s=signal: toggle_signal_in_view(view_manager, 'spatial_view', s, checked)
        )
        spatial_menu.addAction(signal_action)
    
    # View Menu for managing the UI layout
    view_menu = menubar.addMenu("View")
    
    # Add layout actions
    save_layout_action = QAction("Save Layout", win)
    save_layout_action.triggered.connect(lambda: save_current_layout(win, view_manager))
    view_menu.addAction(save_layout_action)
    
    load_layout_action = QAction("Load Layout", win)
    load_layout_action.triggered.connect(lambda: load_saved_layout(win, view_manager))
    view_menu.addAction(load_layout_action)
    
    # Add view creation actions
    view_menu.addSeparator()
    add_view_menu = QMenu("Add View", win)
    view_menu.addMenu(add_view_menu)
    
    add_temporal_action = QAction("Add Temporal View", win)
    add_temporal_action.triggered.connect(lambda: add_new_view(win, view_manager, VIEW_TYPE_TEMPORAL))
    add_view_menu.addAction(add_temporal_action)
    
    add_spatial_action = QAction("Add Spatial View", win)
    add_spatial_action.triggered.connect(lambda: add_new_view(win, view_manager, VIEW_TYPE_SPATIAL))
    add_view_menu.addAction(add_spatial_action)


def setup_timestamp_slider(win, plot_manager, view_manager, current_timestamp):
    """
    Set up the timestamp slider for navigating through time-series data.
    
    Args:
        win: Main window to add slider to
        plot_manager: PlotManager instance
        view_manager: ViewManager instance
        current_timestamp: Initial timestamp value
    """
    # Get timestamps from a plugin if available
    timestamps = []
    
    # Try to get timestamps from the signal registry first
    for plugin_name, plugin in plot_manager.plugins.items():
        if hasattr(plugin, 'get_timestamps') and callable(plugin.get_timestamps):
            try:
                timestamps = plugin.get_timestamps()
                if timestamps and len(timestamps) > 0:
                    break
            except Exception as e:
                print(f"Error getting timestamps from {plugin_name}: {str(e)}")
    # Fallback: try to get timestamps from legacy method
    if (timestamps is None or len(timestamps) == 0) and "CarPosePlugin" in plot_manager.plugins:
        try:
            car_pose_plugin = plot_manager.plugins["CarPosePlugin"]
            if "timestamps" in car_pose_plugin.signals:
                timestamps_func = car_pose_plugin.signals["timestamps"].get("func")
                if timestamps_func and callable(timestamps_func):
                    timestamps = timestamps_func()
        except Exception as e:
            print(f"Error getting timestamps from legacy method: {str(e)}")
    
    if timestamps is not None and len(timestamps) > 0:
        initial_timestamp = float(timestamps[0])  # Convert to float to avoid numpy dtype issues
        plot_manager.request_data(initial_timestamp)
        print(f"Initialized with timestamp: {initial_timestamp}")
    else:
        print("No timestamps available. Using default timestamp 0.0")
        plot_manager.request_data(0.0)
    
    def update_timestamp(new_timestamp):
        """Update all views with data for the new timestamp."""
        nonlocal current_timestamp
        current_timestamp = new_timestamp
        
        # Request data using PlotManager
        plot_manager.request_data(current_timestamp)
        
        # Update timestamp in temporal views
        temporal_views = view_manager.get_views_for_signal("dummy_temporal_signal")
        for view in temporal_views:
            if hasattr(view, 'set_current_timestamp') and callable(view.set_current_timestamp):
                view.set_current_timestamp(current_timestamp)

    # Create Timestamp Slider Dock
    slider_dock = QDockWidget("", win)  # No title bar
    slider_dock.setObjectName("TimestampSliderDock")
    slider_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

    slider = TimestampSlider(plot_manager, timestamps)
    slider.timestamp_changed.connect(update_timestamp)
    slider_dock.setWidget(slider)

    # Remove the title bar for a more compact layout
    slider_dock.setTitleBarWidget(QWidget())

    # Set size constraints
    slider_dock.setMinimumHeight(50)
    slider_dock.setMaximumHeight(60)

    # Add the dock to the bottom area
    win.addDockWidget(Qt.BottomDockWidgetArea, slider_dock)
    slider_dock.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    
    return slider


def toggle_signal_in_view(view_manager, view_id, signal_name, visible):
    """
    Toggle the visibility of a signal in a specific view.
    
    Args:
        view_manager: ViewManager instance
        view_id: ID of the view to toggle signal in
        signal_name: Name of the signal to toggle
        visible: Whether the signal should be visible
    """
    view = view_manager.get_view(view_id)
    if not view:
        print(f"Warning: View {view_id} not found")
        return
        
    if visible:
        # Connect the signal to the view if not already connected
        view_manager.connect_signal_to_view(signal_name, view_id)
    else:
        # Disconnect the signal from the view
        view_manager.disconnect_signal_from_view(signal_name, view_id)
        
    # If the view has a set_signal_visible method, call it
    if hasattr(view, 'set_signal_visible') and callable(view.set_signal_visible):
        view.set_signal_visible(signal_name, visible)


def add_new_view(win, view_manager, view_type):
    """
    Add a new view to the main window.
    
    Args:
        win: Main window to add view to
        view_manager: ViewManager instance
        view_type: Type of view to add (e.g., 'temporal', 'spatial')
    """
    # Generate a unique ID for the new view
    view_count = len([v_id for v_id in view_manager.views.keys() if view_type in v_id])
    view_id = f"{view_type}_view_{view_count + 1}"
    
    # Create the view based on type
    if view_type == VIEW_TYPE_TEMPORAL:
        view = view_manager.create_view_from_template(view_id, 'temporal_default')
    elif view_type == VIEW_TYPE_SPATIAL:
        view = view_manager.create_view_from_template(view_id, 'spatial_default')
    else:
        print(f"Warning: Unsupported view type {view_type}")
        return
        
    if not view:
        print(f"Error: Failed to create view of type {view_type}")
        return
        
    # Create a dock widget for the view
    dock = QDockWidget(f"{view_type.title()} View {view_count + 1}", win)
    dock.setObjectName(f"{view_type}ViewDock{view_count + 1}")
    dock.setWidget(view.get_widget())
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
    
    # Add the dock to the right area
    win.addDockWidget(Qt.RightDockWidgetArea, dock)
    
    # Connect appropriate signals based on view type
    if view_type == VIEW_TYPE_TEMPORAL:
        for signal in view_manager.get_view('temporal_view').view_id:
            view_manager.connect_signal_to_view(signal, view_id)
    elif view_type == VIEW_TYPE_SPATIAL:
        for signal in view_manager.get_view('spatial_view').view_id:
            view_manager.connect_signal_to_view(signal, view_id)
    
    return view


def save_current_layout(win, view_manager):
    """
    Save the current view layout configuration.
    
    Args:
        win: Main window
        view_manager: ViewManager instance
    """
    # Get the current layout from the view manager
    layout = view_manager.save_layout()
    
    # TODO: In a real application, we would save this to a file or settings
    # For now, just print it
    print("Layout saved (not actually persisted):")
    print(f"Views: {list(layout['views'].keys())}")
    print(f"Connections: {list(layout['connections'].keys())}")
    
    # Show confirmation to user
    QMessageBox.information(win, "Layout Saved", "The current layout has been saved.")
    

def load_saved_layout(win, view_manager):
    """
    Load a saved view layout configuration.
    
    Args:
        win: Main window
        view_manager: ViewManager instance
    """
    # TODO: In a real application, we would load this from a file or settings
    # For now, just show a message
    QMessageBox.information(win, "Load Layout", "This feature is not yet implemented. It would load a saved layout configuration.")

