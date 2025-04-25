#!/usr/bin/env python3

"""
Debug Player Signal Filtering Demo

This script demonstrates the enhanced signal filtering capabilities in the Debug Player,
showcasing how to filter signals by type, category, tag, and search text.
"""

import os
import sys
import random
import math
from typing import Dict, Any, List
import logging

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer

# Ensure the Debug Player modules are in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Debug Player components
from core.signal_registry import SignalRegistry
from core.view_manager import ViewManager
from gui.signal_filter_panel import SignalFilterPanel
from gui.views import register_views

# Import standard view types
try:
    from views.temporal_view import TemporalView
    from views.spatial_view import SpatialView
except ImportError:
    print("Warning: Could not import standard view types. Trying alternate paths...")
    try:
        # Try alternate import paths
        from project_root.views.temporal_view import TemporalView
        from project_root.views.spatial_view import SpatialView
    except ImportError:
        print("Error: Could not import TemporalView and SpatialView classes. Will create mock versions.")
        # Create mock classes if needed
        from core.view_manager import ViewBase
        class TemporalView(ViewBase):
            def __init__(self, view_id, parent=None):
                super().__init__(view_id, parent)
                self.supported_signal_types = {'temporal'}
                self.widget = QWidget()
                self.widget.setLayout(QVBoxLayout())
                self.widget.layout().addWidget(QLabel("Mock Temporal View - Import Failed"))
            
            def update_data(self, signal_name, data):
                return True
        
        class SpatialView(ViewBase):
            def __init__(self, view_id, parent=None):
                super().__init__(view_id, parent)
                self.supported_signal_types = {'spatial'}
                self.widget = QWidget()
                self.widget.setLayout(QVBoxLayout())
                self.widget.layout().addWidget(QLabel("Mock Spatial View - Import Failed"))
            
            def update_data(self, signal_name, data):
                return True

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DemoSignalProvider:
    """
    Provides sample signals with rich metadata for testing the filter panel.
    """
    def __init__(self, signal_registry: SignalRegistry):
        self.signal_registry = signal_registry
        self.timestamp = 0.0
        self.signal_data = {}
        
        # Register example signals with rich metadata
        self._register_signals()
        
    def _register_signals(self):
        # Vehicle category signals
        self._register_vehicle_signals()
        
        # Sensor category signals
        self._register_sensor_signals()
        
        # System category signals
        self._register_system_signals()
        
        # Environment category signals
        self._register_environment_signals()
        
        logger.info(f"Registered {len(self.signal_data)} demo signals")
    
    def _register_vehicle_signals(self):
        # Vehicle motion signals (temporal)
        motion_signals = [
            {"name": "vehicle_speed", "func": self._get_vehicle_speed, "description": "Vehicle forward speed", 
             "units": "m/s", "tags": ["speed", "motion", "control"], "precision": 2},
            {"name": "vehicle_acceleration", "func": self._get_vehicle_acceleration, "description": "Vehicle acceleration", 
             "units": "m/s²", "tags": ["acceleration", "motion"], "precision": 2},
            {"name": "steering_angle", "func": self._get_steering_angle, "description": "Steering wheel angle", 
             "units": "degrees", "tags": ["steering", "control"], "precision": 1},
            {"name": "yaw_rate", "func": self._get_yaw_rate, "description": "Vehicle yaw (rotation) rate", 
             "units": "deg/s", "tags": ["rotation", "motion"], "precision": 1},
        ]
        
        for signal in motion_signals:
            self.signal_registry.register_signal(
                signal_name=signal["name"],
                signal_definition={
                    "func": signal["func"],
                    "type": "temporal",
                    "description": signal["description"],
                    "units": signal["units"],
                    "category": "vehicle_state",
                    "tags": signal["tags"],
                    "precision": signal["precision"],
                    "color": "#3498db"  # Blue
                },
                plugin_name="demo_plugin"
            )
            self.signal_data[signal["name"]] = 0.0
        
        # Vehicle spatial signals
        self.signal_registry.register_signal(
            signal_name="vehicle_pose",
            signal_definition={
                "func": self._get_vehicle_pose,
                "type": "spatial",
                "description": "Vehicle position and orientation",
                "units": "meters",
                "category": "vehicle_state",
                "tags": ["position", "orientation", "pose"],
                "color": "#2ecc71"  # Green
            },
            plugin_name="demo_plugin"
        )
        self.signal_data["vehicle_pose"] = {"x": [0.0], "y": [0.0], "theta": [0.0]}
    
    def _register_sensor_signals(self):
        # Camera signals
        self.signal_registry.register_signal(
            signal_name="camera_fps",
            signal_definition={
                "func": self._get_camera_fps,
                "type": "temporal",
                "description": "Camera frames per second",
                "units": "Hz",
                "category": "sensors",
                "tags": ["camera", "performance", "fps"],
                "precision": 1,
                "color": "#9b59b6"  # Purple
            },
            plugin_name="demo_plugin"
        )
        self.signal_data["camera_fps"] = 30.0
        
        # Lidar signals
        self.signal_registry.register_signal(
            signal_name="lidar_point_cloud",
            signal_definition={
                "func": self._get_lidar_points,
                "type": "spatial",
                "description": "Lidar point cloud data",
                "units": "meters",
                "category": "sensors",
                "tags": ["lidar", "point_cloud", "detection"],
                "color": "#f1c40f"  # Yellow
            },
            plugin_name="demo_plugin"
        )
        self.signal_data["lidar_point_cloud"] = {"x": [], "y": []}
        
        # Radar signals
        self.signal_registry.register_signal(
            signal_name="radar_targets",
            signal_definition={
                "func": self._get_radar_targets,
                "type": "spatial",
                "description": "Radar detected targets",
                "units": "meters",
                "category": "sensors",
                "tags": ["radar", "targets", "detection"],
                "color": "#e74c3c"  # Red
            },
            plugin_name="demo_plugin"
        )
        self.signal_data["radar_targets"] = {"x": [], "y": []}
    
    def _register_system_signals(self):
        # System performance signals
        performance_signals = [
            {"name": "cpu_usage", "func": self._get_cpu_usage, "description": "CPU utilization", 
             "units": "%", "tags": ["cpu", "performance", "resource"], "precision": 1},
            {"name": "memory_usage", "func": self._get_memory_usage, "description": "Memory usage", 
             "units": "MB", "tags": ["memory", "performance", "resource"], "precision": 1},
            {"name": "disk_usage", "func": self._get_disk_usage, "description": "Disk space usage", 
             "units": "GB", "tags": ["disk", "storage", "resource"], "precision": 2},
        ]
        
        for signal in performance_signals:
            self.signal_registry.register_signal(
                signal_name=signal["name"],
                signal_definition={
                    "func": signal["func"],
                    "type": "temporal",
                    "description": signal["description"],
                    "units": signal["units"],
                    "category": "system",
                    "tags": signal["tags"],
                    "precision": signal["precision"],
                    "color": "#95a5a6"  # Gray
                },
                plugin_name="demo_plugin"
            )
            self.signal_data[signal["name"]] = 0.0
    
    def _register_environment_signals(self):
        # Environment signals
        environment_signals = [
            {"name": "outdoor_temperature", "func": self._get_outdoor_temp, "description": "Outdoor temperature", 
             "units": "°C", "tags": ["temperature", "weather"], "precision": 1},
            {"name": "wind_speed", "func": self._get_wind_speed, "description": "Wind speed", 
             "units": "m/s", "tags": ["wind", "weather"], "precision": 1},
        ]
        
        for signal in environment_signals:
            self.signal_registry.register_signal(
                signal_name=signal["name"],
                signal_definition={
                    "func": signal["func"],
                    "type": "temporal",
                    "description": signal["description"],
                    "units": signal["units"],
                    "category": "environment",
                    "tags": signal["tags"],
                    "precision": signal["precision"],
                    "color": "#16a085"  # Teal
                },
                plugin_name="demo_plugin"
            )
            self.signal_data[signal["name"]] = 0.0
    
    def update_data(self, timestamp: float):
        """
        Update all signal data for the given timestamp.
        """
        self.timestamp = timestamp
        
        # Update vehicle motion signals
        self.signal_data["vehicle_speed"] = 10.0 + 5.0 * math.sin(timestamp / 10.0)
        self.signal_data["vehicle_acceleration"] = 0.5 * math.cos(timestamp / 10.0)
        self.signal_data["steering_angle"] = 30.0 * math.sin(timestamp / 15.0)
        self.signal_data["yaw_rate"] = 5.0 * math.cos(timestamp / 15.0)
        
        # Update vehicle pose
        path_x = []
        path_y = []
        path_theta = []
        
        # Generate path up to current time (circular path)
        for t in range(0, int(timestamp * 10), 5):
            t_sec = t / 10.0
            angle = t_sec / 5.0
            path_x.append(50.0 * math.cos(angle))
            path_y.append(50.0 * math.sin(angle))
            path_theta.append(angle + math.pi/2)  # Tangent to circle
        
        self.signal_data["vehicle_pose"] = {"x": path_x, "y": path_y, "theta": path_theta}
        
        # Update sensor signals
        self.signal_data["camera_fps"] = 30.0 + 2.0 * math.sin(timestamp) - random.uniform(0, 3)
        
        # Update lidar points (random points around vehicle position)
        current_x = 50.0 * math.cos(timestamp / 5.0)
        current_y = 50.0 * math.sin(timestamp / 5.0)
        
        lidar_x = []
        lidar_y = []
        
        for _ in range(50):  # 50 lidar points
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 20)
            lidar_x.append(current_x + distance * math.cos(angle))
            lidar_y.append(current_y + distance * math.sin(angle))
        
        self.signal_data["lidar_point_cloud"] = {"x": lidar_x, "y": lidar_y}
        
        # Update radar targets (just a few points in front of vehicle)
        radar_x = []
        radar_y = []
        
        vehicle_angle = timestamp / 5.0
        forward_direction = vehicle_angle + math.pi/2
        
        for i in range(3):  # 3 radar targets
            angle_offset = random.uniform(-0.3, 0.3)
            distance = random.uniform(20, 40)
            radar_x.append(current_x + distance * math.cos(forward_direction + angle_offset))
            radar_y.append(current_y + distance * math.sin(forward_direction + angle_offset))
        
        self.signal_data["radar_targets"] = {"x": radar_x, "y": radar_y}
        
        # Update system signals
        self.signal_data["cpu_usage"] = 30.0 + 20.0 * math.sin(timestamp / 20.0) + random.uniform(-5, 5)
        self.signal_data["memory_usage"] = 500.0 + 100.0 * math.sin(timestamp / 30.0) + random.uniform(-20, 20)
        self.signal_data["disk_usage"] = 20.0 + timestamp / 100.0  # Slowly increasing
        
        # Update environment signals
        self.signal_data["outdoor_temperature"] = 25.0 + 5.0 * math.sin(timestamp / 50.0) + random.uniform(-1, 1)
        self.signal_data["wind_speed"] = 5.0 + 3.0 * math.sin(timestamp / 25.0) + random.uniform(-1, 1)
    
    # Signal getter methods
    def _get_vehicle_speed(self, timestamp):
        return {"value": self.signal_data["vehicle_speed"]}
    
    def _get_vehicle_acceleration(self, timestamp):
        return {"value": self.signal_data["vehicle_acceleration"]}
    
    def _get_steering_angle(self, timestamp):
        return {"value": self.signal_data["steering_angle"]}
    
    def _get_yaw_rate(self, timestamp):
        return {"value": self.signal_data["yaw_rate"]}
    
    def _get_vehicle_pose(self, timestamp):
        return self.signal_data["vehicle_pose"]
    
    def _get_camera_fps(self, timestamp):
        return {"value": self.signal_data["camera_fps"]}
    
    def _get_lidar_points(self, timestamp):
        return self.signal_data["lidar_point_cloud"]
    
    def _get_radar_targets(self, timestamp):
        return self.signal_data["radar_targets"]
    
    def _get_cpu_usage(self, timestamp):
        return {"value": self.signal_data["cpu_usage"]}
    
    def _get_memory_usage(self, timestamp):
        return {"value": self.signal_data["memory_usage"]}
    
    def _get_disk_usage(self, timestamp):
        return {"value": self.signal_data["disk_usage"]}
    
    def _get_outdoor_temp(self, timestamp):
        return {"value": self.signal_data["outdoor_temperature"]}
    
    def _get_wind_speed(self, timestamp):
        return {"value": self.signal_data["wind_speed"]}


class SignalFilteringDemo(QMainWindow):
    """
    Demo application showcasing the Debug Player's signal filtering capabilities.
    """
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Debug Player - Signal Filtering Demo")
        self.resize(1280, 800)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create view manager and register view types
        self.view_manager = ViewManager()
        register_views(self.view_manager)
        
        # Register the standard view types as well
        self.view_manager.register_view_class('temporal', TemporalView)
        self.view_manager.register_view_class('spatial', SpatialView)
        
        # Create signal registry
        self.signal_registry = SignalRegistry()
        
        # Create demo signal provider
        self.signal_provider = DemoSignalProvider(self.signal_registry)
        
        # Create a horizontal splitter for filter panel and views
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.main_splitter)
        
        # Set up the signal filter panel on the left
        self.filter_panel = SignalFilterPanel(self.signal_registry)
        self.filter_panel.signal_selection_changed.connect(self._on_signal_selection_changed)
        self.main_splitter.addWidget(self.filter_panel)
        
        # Create a widget for the views on the right
        self.views_widget = QWidget()
        self.views_layout = QVBoxLayout(self.views_widget)
        self.main_splitter.addWidget(self.views_widget)
        
        # Set up views
        self.setup_views()
        
        # Set reasonable sizes for the splitter
        self.main_splitter.setSizes([300, 980])
        
        # Create timer for updating data
        self.timestamp = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Update every 100ms
        
        # Initialize filter panel
        self.filter_panel.refresh_signals()
        
        logger.info("Signal Filtering Demo initialized")
    
    def setup_views(self):
        """
        Set up the view widgets to display the filtered signals.
        """
        # Create a splitter for temporal and spatial views
        view_splitter = QSplitter(Qt.Vertical)
        self.views_layout.addWidget(view_splitter)
        
        # Create temporal view
        temporal_view = self.view_manager.create_view("main_temporal_view", "temporal", {
            "title": "Temporal Signals",
            "x_label": "Time (s)",
            "y_label": "Value",
            "show_grid": True,
            "show_legend": True
        })
        view_splitter.addWidget(temporal_view.get_widget())
        
        # Create spatial view
        spatial_view = self.view_manager.create_view("main_spatial_view", "spatial", {
            "title": "Spatial Signals",
            "x_label": "X Position (m)",
            "y_label": "Y Position (m)",
            "aspect_locked": True,
            "show_grid": True
        })
        view_splitter.addWidget(spatial_view.get_widget())
        
        # Create a horizontal layout for the detail views
        detail_widget = QWidget()
        detail_layout = QHBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        view_splitter.addWidget(detail_widget)
        
        # Create text view
        text_view = self.view_manager.create_view("detail_text_view", "text", {
            "title": "Signal Details",
            "auto_scroll": True
        })
        detail_layout.addWidget(text_view.get_widget())
        
        # Set reasonable sizes for view splitter
        view_splitter.setSizes([300, 300, 200])
    
    def _on_signal_selection_changed(self, selected_signals):
        """
        Handle signal selection changes from the filter panel.
        """
        # Update views based on selected signals
        self.view_manager.update_view_signals(selected_signals)
        
        # Update the signal details text view
        details = []
        for signal_name in selected_signals:
            metadata = self.signal_registry.get_signal_metadata(signal_name) or {}
            details.append(f"Signal: {signal_name}")
            details.append(f"  Type: {metadata.get('type', 'unknown')}")
            details.append(f"  Category: {metadata.get('category', 'uncategorized')}")
            details.append(f"  Description: {metadata.get('description', 'No description')}")
            if 'units' in metadata:
                details.append(f"  Units: {metadata['units']}")
            if 'tags' in metadata:
                details.append(f"  Tags: {', '.join(metadata['tags'])}")
            details.append("")
        
        detail_text = "\n".join(details) if details else "No signals selected"
        self.view_manager.update_signal_data("signal_details", detail_text)
    
    def update_data(self):
        """
        Update all signals with new data.
        """
        # Increment timestamp
        self.timestamp += 0.1
        
        # Update signal data
        self.signal_provider.update_data(self.timestamp)
        
        # Broadcast data update to views
        for signal_name in self.signal_provider.signal_data.keys():
            data = self.signal_provider.signal_data[signal_name]
            
            # Different format for different signal types
            if isinstance(data, dict) and all(k in data for k in ["x", "y"]):
                # Spatial signal
                self.view_manager.update_signal_data(signal_name, data)
            else:
                # Temporal or other signal types
                if isinstance(data, (int, float)):
                    self.view_manager.update_signal_data(signal_name, {"value": data})
                else:
                    self.view_manager.update_signal_data(signal_name, data)
        
        # Update status bar with current timestamp
        self.statusBar().showMessage(f"Timestamp: {self.timestamp:.1f} seconds")


def main():
    """
    Main function to run the demo.
    """
    app = QApplication(sys.argv)
    demo = SignalFilteringDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
