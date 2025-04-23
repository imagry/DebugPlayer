#!/usr/bin/env python3

"""
Debug Player View System Demo

This script demonstrates the enhanced view system in the Debug Player,
showcasing the different view types (Temporal, Spatial, Table, Text, and Metrics)
and how they can be used to visualize different types of data.
"""

import os
import sys
import math
import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
import logging

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QTabWidget
from PySide6.QtCore import Qt, QTimer

# Ensure the Debug Player modules are in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Debug Player components
from core.view_manager import ViewManager
from gui.views import register_views
from gui.views.table_view import TableView
from gui.views.text_view import TextView
from gui.views.metrics_view import MetricsView
from views.temporal_view import TemporalView
from views.spatial_view import SpatialView

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DemoDataGenerator:
    """
    Generates sample data for the view system demonstration.
    """
    def __init__(self):
        self.timestamp = 0.0
        self.update_interval = 100  # milliseconds
        
        # Initialize data structures
        self.sine_values = []
        self.time_values = []
        self.vehicle_path = {"x": [], "y": [], "theta": []}
        self.log_messages = []
        self.metrics = {}
        
        # Generate initial data
        self._generate_initial_data()
        
    def _generate_initial_data(self):
        # Generate time and sine data points
        for t in range(0, 1000, 10):
            self.time_values.append(t / 1000.0)  # Convert to seconds
            self.sine_values.append(math.sin(t / 100.0))
            
        # Generate vehicle path (figure-8 pattern)
        for t in range(0, 1000, 10):
            angle = t / 100.0
            x = 50.0 * math.sin(angle)
            y = 25.0 * math.sin(2 * angle)
            theta = math.atan2(2 * math.cos(2 * angle), math.cos(angle))
            
            self.vehicle_path["x"].append(x)
            self.vehicle_path["y"].append(y)
            self.vehicle_path["theta"].append(theta)
        
        # Generate initial log messages
        self.log_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] INFO: View System Demo started")
        self.log_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] DEBUG: Initializing data structures")
        
        # Generate initial metrics
        self.metrics = {
            "cpu_usage": 25.0,
            "memory_usage": 128.5,
            "fps": 30.0,
            "temperature": 45.2,
            "disk_space": 1024.0,
            "network_traffic": 1.5
        }
        
    def update(self):
        """
        Update data for the next frame.
        """
        # Increment timestamp
        self.timestamp += 0.1
        
        # Update metrics with some random fluctuation
        random.seed(int(self.timestamp * 10))
        
        self.metrics["cpu_usage"] = 25.0 + 15.0 * math.sin(self.timestamp / 5.0) + random.uniform(-3.0, 3.0)
        self.metrics["memory_usage"] = 128.5 + self.timestamp * 0.5 + random.uniform(-5.0, 5.0)
        if self.metrics["memory_usage"] > 512.0:
            # Simulate memory cleanup
            self.metrics["memory_usage"] = 128.5
            self.log_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] INFO: Memory cleanup performed")
            
        self.metrics["fps"] = 30.0 + random.uniform(-3.0, 1.0)
        self.metrics["temperature"] = 45.2 + (self.metrics["cpu_usage"] / 100.0) * 10.0
        self.metrics["disk_space"] = 1024.0 - self.timestamp * 0.1
        self.metrics["network_traffic"] = 1.5 + 0.5 * math.sin(self.timestamp / 2.0)
        
        # Add occasional log messages
        if random.random() < 0.1:  # 10% chance each update
            log_types = ["INFO", "DEBUG", "WARNING", "ERROR"]
            weights = [0.5, 0.3, 0.15, 0.05]  # Higher probability for INFO/DEBUG
            log_type = random.choices(log_types, weights=weights)[0]
            
            messages = {
                "INFO": [
                    "System check completed",
                    "Data processing finished",
                    "View update completed",
                    "Configuration loaded successfully"
                ],
                "DEBUG": [
                    "Processing frame data",
                    "Updating view components",
                    "Calculating metrics",
                    "Rendering complete"
                ],
                "WARNING": [
                    "High CPU usage detected",
                    "Memory consumption increasing",
                    "Network latency higher than normal",
                    "Buffer underrun in data processing"
                ],
                "ERROR": [
                    "Failed to process data packet",
                    "Connection timeout occurred",
                    "Unable to render frame",
                    "Resource allocation failed"
                ]
            }
            
            message = random.choice(messages[log_type])
            self.log_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log_type}: {message}")
            
            # Keep log limited to recent messages
            if len(self.log_messages) > 100:
                self.log_messages = self.log_messages[-100:]
        
        return {
            "timestamp": self.timestamp,
            "sine_value": math.sin(self.timestamp),
            "vehicle_path": self._get_vehicle_path_subset(),
            "logs": self.log_messages,
            "metrics": self.metrics,
            "table_data": self._generate_table_data()
        }
    
    def _get_vehicle_path_subset(self):
        """
        Get a subset of the vehicle path based on current timestamp.
        """
        # Map timestamp to an index in our pre-generated path
        max_idx = min(int(self.timestamp * 10) % 100, 99)
        
        return {
            "x": self.vehicle_path["x"][:max_idx + 1],
            "y": self.vehicle_path["y"][:max_idx + 1],
            "theta": self.vehicle_path["theta"][:max_idx + 1]
        }
    
    def _generate_table_data(self):
        """
        Generate sample tabular data.
        """
        timestamp = self.timestamp
        data = []
        
        # Generate a table with 10 rows of data
        for i in range(10):
            row_timestamp = timestamp - (9-i) * 0.1  # Most recent at the bottom
            if row_timestamp < 0:
                continue
                
            sine = math.sin(row_timestamp)
            cosine = math.cos(row_timestamp)
            tangent = math.tan(row_timestamp) if abs(cosine) > 0.01 else float('inf')
            
            data.append({
                "timestamp": round(row_timestamp, 1),
                "sine": round(sine, 3),
                "cosine": round(cosine, 3),
                "tangent": round(tangent, 3) if abs(tangent) != float('inf') else "N/A",
                "random": round(random.uniform(-1, 1), 3)
            })
        
        return data


class ViewSystemDemo(QMainWindow):
    """
    Demo application showcasing the Debug Player's view system.
    """
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Debug Player - View System Demo")
        self.resize(1280, 800)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create data generator
        self.data_generator = DemoDataGenerator()
        
        # Create view manager and register view types
        self.view_manager = ViewManager()
        register_views(self.view_manager)
        
        # Create a tab widget to organize the different view demos
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Set up the temporal view demo tab
        self.setup_temporal_view_tab()
        
        # Set up the spatial view demo tab
        self.setup_spatial_view_tab()
        
        # Set up the table view demo tab
        self.setup_table_view_tab()
        
        # Set up the text view demo tab
        self.setup_text_view_tab()
        
        # Set up the metrics view demo tab
        self.setup_metrics_view_tab()
        
        # Set up a combined views demo tab
        self.setup_combined_views_tab()
        
        # Create a timer for updating data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Update every 100ms
        
        logger.info("View System Demo initialized")
    
    def setup_temporal_view_tab(self):
        """
        Set up a tab demonstrating the temporal view.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a temporal view
        view_id = "demo_temporal_view"
        temporal_view = self.view_manager.create_view(view_id, "temporal", {
            "title": "Sine Wave Demo",
            "x_label": "Time (s)",
            "y_label": "Amplitude",
            "show_grid": True,
            "show_legend": True
        })
        
        # Add the view to the tab
        layout.addWidget(temporal_view.get_widget())
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Temporal View")
        
    def setup_spatial_view_tab(self):
        """
        Set up a tab demonstrating the spatial view.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a spatial view
        view_id = "demo_spatial_view"
        spatial_view = self.view_manager.create_view(view_id, "spatial", {
            "title": "Vehicle Path Demo",
            "x_label": "X Position",
            "y_label": "Y Position",
            "aspect_locked": True,
            "show_grid": True
        })
        
        # Add the view to the tab
        layout.addWidget(spatial_view.get_widget())
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Spatial View")
    
    def setup_table_view_tab(self):
        """
        Set up a tab demonstrating the table view.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a table view
        view_id = "demo_table_view"
        table_view = self.view_manager.create_view(view_id, "table", {
            "title": "Data Table Demo"
        })
        
        # Add the view to the tab
        layout.addWidget(table_view.get_widget())
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Table View")
    
    def setup_text_view_tab(self):
        """
        Set up a tab demonstrating the text view.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a text view
        view_id = "demo_text_view"
        text_view = self.view_manager.create_view(view_id, "text", {
            "title": "Log Viewer Demo",
            "auto_scroll": True,
            "show_timestamps": True
        })
        
        # Add the view to the tab
        layout.addWidget(text_view.get_widget())
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Text View")
    
    def setup_metrics_view_tab(self):
        """
        Set up a tab demonstrating the metrics view.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a metrics view
        view_id = "demo_metrics_view"
        metrics_view = self.view_manager.create_view(view_id, "metrics", {
            "title": "System Metrics Demo",
            "layout_columns": 3
        })
        
        # Add the view to the tab
        layout.addWidget(metrics_view.get_widget())
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Metrics View")
    
    def setup_combined_views_tab(self):
        """
        Set up a tab with multiple view types combined.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a splitter for the top row
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Create a temporal view
        combined_temporal_view = self.view_manager.create_view("combined_temporal_view", "temporal", {
            "title": "Sine Wave",
            "x_label": "Time (s)",
            "y_label": "Amplitude"
        })
        top_splitter.addWidget(combined_temporal_view.get_widget())
        
        # Create a spatial view
        combined_spatial_view = self.view_manager.create_view("combined_spatial_view", "spatial", {
            "title": "Vehicle Path",
            "aspect_locked": True
        })
        top_splitter.addWidget(combined_spatial_view.get_widget())
        
        # Create a splitter for the bottom row
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Create a text view
        combined_text_view = self.view_manager.create_view("combined_text_view", "text", {
            "title": "Log Messages",
            "auto_scroll": True
        })
        bottom_splitter.addWidget(combined_text_view.get_widget())
        
        # Create a metrics view
        combined_metrics_view = self.view_manager.create_view("combined_metrics_view", "metrics", {
            "title": "Key Metrics",
            "layout_columns": 2
        })
        bottom_splitter.addWidget(combined_metrics_view.get_widget())
        
        # Create a vertical splitter to combine the top and bottom rows
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(top_splitter)
        vertical_splitter.addWidget(bottom_splitter)
        
        # Add the splitter to the layout
        layout.addWidget(vertical_splitter)
        
        # Set reasonable sizes
        top_splitter.setSizes([500, 500])
        bottom_splitter.setSizes([500, 500])
        vertical_splitter.setSizes([400, 400])
        
        # Add the tab to the tab widget
        self.tab_widget.addTab(tab, "Combined Views")
    
    def update_data(self):
        """
        Update all views with new data.
        """
        data = self.data_generator.update()
        
        # Update temporal views
        self.view_manager.update_signal_data("sine_wave", {
            "value": data["sine_value"]
        })
        
        # Update spatial views
        self.view_manager.update_signal_data("vehicle_path", data["vehicle_path"])
        
        # Update table views
        self.view_manager.update_signal_data("table_data", data["table_data"])
        
        # Update text views
        self.view_manager.update_signal_data("log_messages", data["logs"])
        
        # Update metrics views
        self.view_manager.update_signal_data("system_metrics", data["metrics"])
        
        # Update status bar with current timestamp
        self.statusBar().showMessage(f"Current Timestamp: {data['timestamp']:.1f} seconds")


def main():
    """
    Main function to run the demo.
    """
    app = QApplication(sys.argv)
    demo = ViewSystemDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
