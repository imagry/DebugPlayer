#!/usr/bin/env python3

"""
Example Plugin for the Debug Player.

This plugin demonstrates all the features of the enhanced plugin system,
including versioning, rich metadata, and various signal types.

It serves as both a template and reference implementation for creating
custom plugins for the Debug Player.
"""

import math
import random
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from interfaces.PluginBase import PluginBase

class ExamplePlugin(PluginBase):
    """
    Example plugin that demonstrates all plugin system features.
    
    This plugin provides several different types of signals:
    - Temporal signals (sine waves, random data)
    - Spatial signals (vehicle path, point cloud)
    - Categorical signals (status, classifications)
    - Text signals (logs, messages)
    - Statistical signals (metrics, counters)
    
    It showcases rich metadata, signal categories, and proper versioning.
    """
    
    # Required plugin metadata
    METADATA = {
        "name": "Comprehensive Example Plugin",
        "version": "1.0.0",  # Semantic versioning
        "description": "Demonstrates all plugin system features with various signal types",
        "author": "Debug Player Team",
        "type": "data_source",
        "url": "https://github.com/imagry/DebugPlayer",
        "license": "MIT",
        "dependencies": {
            # List any plugin dependencies here
            # "car_state_plugin": ">=0.5.0"
        }
    }
    
    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize the example plugin.
        
        Args:
            file_path: Optional path to a data file. If None, mock data will be generated.
        """
        super().__init__(file_path)
        
        # Track the current timestamp for stateful signals
        self.current_timestamp = 0.0
        
        # Initialize data structures
        self.time_values = []
        self.sine_values = []
        self.vehicle_path = {"x": [], "y": [], "theta": []}
        self.random_points = {"x": [], "y": []}
        self.status_values = []
        self.status_timestamps = []
        self.log_messages = []
        self.metrics = {}
        
        # Generate example data
        self._generate_data()
        
        # Define signals with rich metadata
        self.signals = {
            # Temporal signals
            "sine_wave": {
                "func": self.get_sine_wave,
                "type": "temporal",
                "description": "A simple sine wave",
                "units": "amplitude",
                "category": "examples",
                "tags": ["sine", "wave", "example"],
                "valid_range": {"min": -1.0, "max": 1.0},
                "precision": 3,
                "color": "#3498db"  # Blue
            },
            "random_walk": {
                "func": self.get_random_walk,
                "type": "temporal",
                "description": "A random walk signal",
                "units": "steps",
                "category": "examples",
                "tags": ["random", "walk", "example"],
                "precision": 2,
                "color": "#e74c3c"  # Red
            },
            
            # Spatial signals
            "vehicle_path": {
                "func": self.get_vehicle_path,
                "type": "spatial",
                "description": "Example vehicle path (circular)",
                "units": "meters",
                "category": "vehicle",
                "tags": ["path", "trajectory", "spatial"],
                "color": "#2ecc71"  # Green
            },
            "point_cloud": {
                "func": self.get_point_cloud,
                "type": "spatial",
                "description": "Example point cloud (random points)",
                "units": "meters",
                "category": "sensors",
                "tags": ["points", "cloud", "spatial"],
                "color": "#9b59b6"  # Purple
            },
            
            # Categorical signals
            "status": {
                "func": self.get_status,
                "type": "categorical",
                "description": "Example status signal",
                "category": "system",
                "tags": ["status", "categorical"],
                "valid_values": ["IDLE", "ACTIVE", "ERROR", "WARNING"]
            },
            
            # Text signals
            "log_messages": {
                "func": self.get_log_messages,
                "type": "text",
                "description": "Example log messages",
                "category": "logs",
                "tags": ["logs", "messages", "text"]
            },
            
            # Statistical signals
            "metrics": {
                "func": self.get_metrics,
                "type": "statistical",
                "description": "Example performance metrics",
                "category": "performance",
                "tags": ["metrics", "statistics", "performance"],
                "units": {
                    "cpu_usage": "%",
                    "memory_usage": "MB",
                    "fps": "Hz"
                },
                "precision": 1,
                "critical_values": {
                    "cpu_usage": {"max": 80.0},
                    "memory_usage": {"max": 1000.0}
                }
            }
        }
    
    def has_signal(self, signal: str) -> bool:
        """
        Check if this plugin provides the requested signal.
        
        Args:
            signal: The name of the signal to check for
            
        Returns:
            True if this plugin provides the signal, False otherwise
        """
        return signal in self.signals
    
    def get_data_for_timestamp(self, signal: str, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a specific signal and timestamp.
        
        Args:
            signal: The name of the signal to fetch data for
            timestamp: The timestamp to fetch data for, in seconds
            
        Returns:
            A dictionary containing the data for the signal at the specified timestamp,
            or None if the signal is not found or data is not available
        """
        # Update the current timestamp for stateful signals
        self.current_timestamp = timestamp
        
        # Call the appropriate handler function based on the requested signal
        if signal in self.signals:
            handler = self.signals[signal]['func']
            return handler(timestamp)
        
        return None
    
    # Temporal signal handlers
    
    def get_sine_wave(self, timestamp: float) -> Dict[str, Any]:
        """Get the sine wave value at the specified timestamp."""
        # Find the closest time index
        if not self.time_values:
            return {"value": 0.0}
            
        idx = min(range(len(self.time_values)), key=lambda i: abs(self.time_values[i] - timestamp))
        return {"value": self.sine_values[idx]}
    
    def get_random_walk(self, timestamp: float) -> Dict[str, Any]:
        """Get a random walk value at the specified timestamp."""
        # Generate a random walk based on the timestamp
        # This is deterministic based on timestamp, but appears random
        random.seed(int(timestamp * 10))
        steps = int(timestamp / 10)
        value = sum(random.choice([-0.1, 0.1]) for _ in range(steps))
        return {"value": value}
    
    # Spatial signal handlers
    
    def get_vehicle_path(self, timestamp: float) -> Dict[str, Any]:
        """Get the vehicle path up to the specified timestamp."""
        # Find all points up to this timestamp
        if not self.time_values:
            return {"x": [0.0], "y": [0.0], "theta": [0.0]}
            
        max_idx = 0
        while max_idx < len(self.time_values) and self.time_values[max_idx] <= timestamp:
            max_idx += 1
            
        return {
            "x": self.vehicle_path["x"][:max_idx],
            "y": self.vehicle_path["y"][:max_idx],
            "theta": self.vehicle_path["theta"][:max_idx]
        }
    
    def get_point_cloud(self, timestamp: float) -> Dict[str, Any]:
        """Get a random point cloud at the specified timestamp."""
        # Generate new random points around the current vehicle position
        # based on the timestamp to simulate a point cloud
        random.seed(int(timestamp * 10))
        
        # Get current vehicle position
        vehicle = self.get_vehicle_path(timestamp)
        if not vehicle["x"]:
            vehicle_x, vehicle_y = 0.0, 0.0
        else:
            vehicle_x = vehicle["x"][-1]
            vehicle_y = vehicle["y"][-1]
        
        # Generate random points around the vehicle
        num_points = 20
        x_points = [vehicle_x + random.uniform(-5, 5) for _ in range(num_points)]
        y_points = [vehicle_y + random.uniform(-5, 5) for _ in range(num_points)]
        
        return {"x": x_points, "y": y_points}
    
    # Categorical signal handlers
    
    def get_status(self, timestamp: float) -> Dict[str, Any]:
        """Get the system status at the specified timestamp."""
        # Find the latest status before or at this timestamp
        if not self.status_timestamps:
            return {"value": "IDLE"}
            
        # Find the index of the last status change before this timestamp
        idx = 0
        while idx < len(self.status_timestamps) and self.status_timestamps[idx] <= timestamp:
            idx += 1
            
        if idx > 0:
            return {"value": self.status_values[idx - 1]}
        else:
            return {"value": "IDLE"}
    
    # Text signal handlers
    
    def get_log_messages(self, timestamp: float) -> Dict[str, Any]:
        """Get log messages up to the specified timestamp."""
        # Generate a few log messages based on the timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Add a new log message every 50 timestamp units
        if int(timestamp) % 50 == 0 and int(timestamp) > 0:
            status = self.get_status(timestamp)["value"]
            new_message = f"[{current_time}] Timestamp {int(timestamp)}: Status is {status}"
            self.log_messages.append(new_message)
            
            # Add some random events occasionally
            if random.random() < 0.3:
                event_type = random.choice(["INFO", "WARNING", "ERROR", "DEBUG"])
                event_message = random.choice([
                    "System check completed",
                    "Network connection fluctuating",
                    "Sensor data received",
                    "Memory usage increased",
                    "Processing delay detected"
                ])
                self.log_messages.append(f"[{current_time}] {event_type}: {event_message}")
        
        # Limit to last 100 messages
        if len(self.log_messages) > 100:
            self.log_messages = self.log_messages[-100:]
            
        return {"values": self.log_messages}
    
    # Statistical signal handlers
    
    def get_metrics(self, timestamp: float) -> Dict[str, Any]:
        """Get performance metrics at the specified timestamp."""
        # Generate metrics that change over time
        random.seed(int(timestamp * 5))
        
        # CPU usage oscillates between 20-80% with some noise
        cpu_base = 50.0 + 30.0 * math.sin(timestamp / 100.0)
        cpu_noise = random.uniform(-5.0, 5.0)
        cpu_usage = min(max(cpu_base + cpu_noise, 0.0), 100.0)
        
        # Memory usage increases over time then resets
        memory_cycle = (timestamp % 500) / 500.0  # 0.0 to 1.0 over 500 timestamp units
        memory_usage = 200.0 + 800.0 * memory_cycle + random.uniform(-50.0, 50.0)
        
        # FPS fluctuates around 30 with occasional dips
        fps_base = 30.0
        fps_noise = random.uniform(-3.0, 1.0)
        fps_dip = 0.0
        if random.random() < 0.1:  # 10% chance of FPS dip
            fps_dip = random.uniform(5.0, 15.0)
        fps = max(fps_base + fps_noise - fps_dip, 1.0)
        
        # Temperature increases with CPU usage
        temperature = 40.0 + (cpu_usage / 100.0) * 20.0 + random.uniform(-2.0, 2.0)
        
        # Store the current metrics
        self.metrics = {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "fps": fps,
            "temperature": temperature,
            "timestamp": timestamp
        }
        
        return self.metrics
    
    # Internal helper methods
    
    def _generate_data(self):
        """Generate example data for this plugin."""
        # Generate time values from 0 to 1000 in steps of 10
        self.time_values = list(range(0, 1000, 10))
        
        # Generate sine wave values
        self.sine_values = [math.sin(t / 100.0) for t in self.time_values]
        
        # Generate vehicle path (circular)
        radius = 100.0
        for t in self.time_values:
            angle = t / 100.0
            self.vehicle_path["x"].append(radius * math.cos(angle))
            self.vehicle_path["y"].append(radius * math.sin(angle))
            self.vehicle_path["theta"].append(angle + math.pi/2)  # Point tangent to circle
        
        # Generate random points
        for _ in range(100):
            self.random_points["x"].append(random.uniform(-200, 200))
            self.random_points["y"].append(random.uniform(-200, 200))
        
        # Generate status changes
        status_options = ["IDLE", "ACTIVE", "WARNING", "ERROR"]
        current_status = "IDLE"
        
        for t in range(0, 1000, 100):  # Status changes every 100 time units
            self.status_timestamps.append(float(t))
            
            # Prefer transitions to adjacent states
            if current_status == "IDLE":
                current_status = random.choice(["IDLE", "ACTIVE"])
            elif current_status == "ACTIVE":
                current_status = random.choice(["ACTIVE", "WARNING", "IDLE"])
            elif current_status == "WARNING":
                current_status = random.choice(["ACTIVE", "WARNING", "ERROR"])
            elif current_status == "ERROR":
                current_status = random.choice(["WARNING", "ERROR", "IDLE"])
                
            self.status_values.append(current_status)
    
    # Optional event handlers
    
    def on_load(self):
        """Called when the plugin is fully loaded."""
        print(f"Example Plugin loaded: {self.METADATA['name']} v{self.METADATA['version']}")
    
    def on_unload(self):
        """Called before the plugin is unloaded."""
        print(f"Example Plugin unloading: {self.METADATA['name']}")
    
    def on_timestamp_changed(self, timestamp: float):
        """Called when the global timestamp changes."""
        # This is called for all plugins when the timestamp slider changes
        # We could update internal state here if needed
        self.current_timestamp = timestamp

# This line is required to export the plugin class
plugin_class = ExamplePlugin
