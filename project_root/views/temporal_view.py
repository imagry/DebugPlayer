#!/usr/bin/env python3

"""
Temporal View for the Debug Player.

This module provides a specialized view for displaying time-series data.
"""

from typing import Dict, Any, List, Optional, Set, Union
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, Signal as QtSignal, Slot
import pyqtgraph as pg
import numpy as np

from core.view_manager import ViewBase

class TemporalView(ViewBase):
    """
    View for displaying time-series data.
    
    This view visualizes temporal signals in a line plot using PyQtGraph.
    It supports multiple signals overlaid on the same plot, customizable
    colors, legends, and interactive features like zooming and panning.
    """
    
    # Custom signals
    signal_selected = QtSignal(str)
    time_marker_moved = QtSignal(float)
    
    def __init__(self, view_id: str, parent: Optional[QWidget] = None):
        """
        Initialize a new temporal view.
        
        Args:
            view_id: Unique identifier for this view
            parent: Optional parent widget
        """
        super().__init__(view_id, parent)
        
        # Set supported signal types
        self.supported_signal_types = {"temporal"}
        
        # Initialize data storage
        self.data: Dict[str, Dict] = {}
        self.timestamps: List[float] = []
        self.current_timestamp: Optional[float] = None
        self.signal_colors: Dict[str, tuple] = {}
        self.signal_pens: Dict[str, pg.mkPen] = {}
        self.visible_signals: Set[str] = set()
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components for this view."""
        # Create main widget
        self.widget = QWidget()
        main_layout = QVBoxLayout(self.widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create controls
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Signal selector
        selector_layout = QVBoxLayout()
        selector_label = QLabel("Signal:")
        self.signal_selector = QComboBox()
        self.signal_selector.currentTextChanged.connect(self._on_signal_selected)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.signal_selector)
        control_layout.addLayout(selector_layout)
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Time', units='ms')
        self.plot_widget.setLabel('left', 'Value')
        
        # Time marker (vertical line at current timestamp)
        self.time_marker = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            pen=pg.mkPen(color=(255, 0, 0), width=2),
            movable=True
        )
        self.time_marker.sigPositionChanged.connect(self._on_time_marker_moved)
        self.plot_widget.addItem(self.time_marker)
        
        # Legend
        self.legend = self.plot_widget.addLegend()
        
        # Add widgets to layout
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.plot_widget)
        
        # Set default colors for signals
        self.default_colors = [
            (31, 119, 180),  # Blue
            (255, 127, 14),  # Orange
            (44, 160, 44),   # Green
            (214, 39, 40),   # Red
            (148, 103, 189), # Purple
            (140, 86, 75),   # Brown
            (227, 119, 194), # Pink
            (127, 127, 127), # Gray
            (188, 189, 34),  # Yellow-green
            (23, 190, 207)   # Cyan
        ]
        
    def configure(self, config: Dict[str, Any]):
        """
        Configure the view with custom settings.
        
        Args:
            config: Dictionary of configuration options
        """
        # Apply title if provided
        if "title" in config:
            self.plot_widget.setTitle(config["title"])
            
        # Apply axis labels if provided
        if "x_label" in config:
            self.plot_widget.setLabel('bottom', config["x_label"], 
                                     units=config.get("x_units"))
        
        if "y_label" in config:
            self.plot_widget.setLabel('left', config["y_label"], 
                                     units=config.get("y_units"))
            
        # Apply y-axis range if provided
        if "y_range" in config:
            y_min, y_max = config["y_range"]
            self.plot_widget.setYRange(y_min, y_max)
            
        # Apply other custom configurations as needed
        
    def update_data(self, signal_name: str, data: Any, timestamp: Optional[float] = None) -> bool:
        """
        Update the view with new data.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display (expected to contain timestamp and value)
            timestamp: Current timestamp (if different from the data timestamp)
            
        Returns:
            True if the update was successful, False otherwise
        """
        if not isinstance(data, dict):
            print(f"Warning: Expected dict data for signal {signal_name}, got {type(data)}")
            return False
            
        # Store the data
        self.data[signal_name] = data
        
        # Update current timestamp if provided
        if timestamp is not None:
            self.current_timestamp = timestamp
            
        # Update signal selector if this is a new signal
        if signal_name not in self.visible_signals:
            self.visible_signals.add(signal_name)
            current_text = self.signal_selector.currentText()
            self.signal_selector.clear()
            self.signal_selector.addItems(sorted(self.visible_signals))
            if current_text in self.visible_signals:
                self.signal_selector.setCurrentText(current_text)
            
        # If this is the only signal, select it
        if len(self.visible_signals) == 1:
            self.signal_selector.setCurrentText(signal_name)
            
        # Plot the data
        self._plot_data()
        
        return True
        
    def clear(self):
        """Clear all data from the view."""
        self.data.clear()
        self.visible_signals.clear()
        self.signal_selector.clear()
        self.plot_widget.clear()
        
        # Re-add the time marker
        self.plot_widget.addItem(self.time_marker)
        
    def set_current_timestamp(self, timestamp: float):
        """
        Set the current timestamp and update the time marker.
        
        Args:
            timestamp: The new timestamp value
        """
        self.current_timestamp = timestamp
        self.time_marker.setValue(timestamp)
        
    def _plot_data(self):
        """
        Plot the currently selected signal.
        """
        # Get the selected signal
        signal = self.signal_selector.currentText()
        if not signal or signal not in self.data:
            return
            
        # Clear previous plots but keep the time marker
        self.plot_widget.clear()
        self.plot_widget.addItem(self.time_marker)
        
        # Reset the legend
        if hasattr(self, 'legend') and self.legend is not None:
            self.legend.scene().removeItem(self.legend)
        self.legend = self.plot_widget.addLegend()
        
        # Ensure we have a color for this signal
        if signal not in self.signal_colors:
            # Assign a color from our default colors
            index = len(self.signal_colors) % len(self.default_colors)
            self.signal_colors[signal] = self.default_colors[index]
            
        if signal not in self.signal_pens:
            # Create a pen for this signal
            self.signal_pens[signal] = pg.mkPen(
                color=self.signal_colors[signal], 
                width=2
            )
            
        # Get the data for this signal
        signal_data = self.data[signal]
        
        # Handle different data formats
        x_data = None
        y_data = None
        
        if "timestamp" in signal_data and "value" in signal_data:
            # Single value format
            x_data = signal_data["timestamp"]
            y_data = signal_data["value"]
            
        elif "timestamps" in signal_data and "values" in signal_data:
            # Multiple values format
            x_data = signal_data["timestamps"]
            y_data = signal_data["values"]
            
        else:
            # Try to extract data from keys
            print(f"Warning: Unknown data format for signal {signal}")
            return
            
        # Convert to numpy arrays if needed
        if not isinstance(x_data, (np.ndarray, list)):
            x_data = [x_data]
        if not isinstance(y_data, (np.ndarray, list)):
            y_data = [y_data]
            
        # Plot the data
        self.plot_widget.plot(
            x_data, 
            y_data, 
            name=signal,
            pen=self.signal_pens[signal]
        )
        
        # Update the time marker
        if self.current_timestamp is not None:
            self.time_marker.setValue(self.current_timestamp)
            
    def _on_signal_selected(self, signal: str):
        """
        Handle signal selection changes.
        
        Args:
            signal: The newly selected signal
        """
        if signal and signal in self.visible_signals:
            self._plot_data()
            self.signal_selected.emit(signal)
            
    def _on_time_marker_moved(self):
        """Handle time marker movements by the user."""
        new_timestamp = self.time_marker.value()
        self.current_timestamp = new_timestamp
        self.time_marker_moved.emit(new_timestamp)
