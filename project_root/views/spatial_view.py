#!/usr/bin/env python3

"""
Spatial View for the Debug Player.

This module provides a specialized view for displaying spatial (2D) data.
"""

from typing import Dict, Any, List, Optional, Set, Union, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox
from PySide6.QtCore import Qt, Signal as QtSignal, Slot
import pyqtgraph as pg
import numpy as np

from core.view_manager import ViewBase

class SpatialView(ViewBase):
    """
    View for displaying 2D spatial data.
    
    This view visualizes spatial signals like vehicle positions, paths, and
    other 2D geometries. It supports multiple layers, customizable styling,
    and interactive features like zooming, panning, and rotation.
    """
    
    # Custom signals
    signal_toggled = QtSignal(str, bool)
    view_config_changed = QtSignal(dict)
    
    def __init__(self, view_id: str, parent: Optional[QWidget] = None):
        """
        Initialize a new spatial view.
        
        Args:
            view_id: Unique identifier for this view
            parent: Optional parent widget
        """
        super().__init__(view_id, parent)
        
        # Set supported signal types
        self.supported_signal_types = {"spatial"}
        
        # Initialize data storage
        self.data: Dict[str, Dict] = {}
        self.signal_colors: Dict[str, tuple] = {}
        self.signal_pens: Dict[str, pg.mkPen] = {}
        self.signal_brushes: Dict[str, pg.mkBrush] = {}
        self.visible_signals: Dict[str, bool] = {}
        self.signal_items: Dict[str, List[pg.GraphicsItem]] = {}
        self.aspect_locked: bool = True
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components for this view."""
        # Create main widget
        self.widget = QWidget()
        main_layout = QVBoxLayout(self.widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls section
        controls_box = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_box)
        
        # Layer visibility controls (will be populated as signals are added)
        self.layers_box = QGroupBox("Layers")
        self.layers_layout = QVBoxLayout(self.layers_box)
        
        # View settings
        settings_layout = QHBoxLayout()
        self.aspect_ratio_check = QCheckBox("Lock Aspect Ratio")
        self.aspect_ratio_check.setChecked(self.aspect_locked)
        self.aspect_ratio_check.stateChanged.connect(self._on_aspect_ratio_changed)
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(self._on_grid_changed)
        settings_layout.addWidget(self.aspect_ratio_check)
        settings_layout.addWidget(self.grid_check)
        settings_layout.addStretch()
        
        # Add controls to layout
        controls_layout.addLayout(settings_layout)
        controls_layout.addWidget(self.layers_box)
        
        # Plot widget (for spatial data)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'X', units='m')
        self.plot_widget.setLabel('left', 'Y', units='m')
        self.plot_widget.setAspectLocked(self.aspect_locked)
        
        # Add a legend
        self.legend = self.plot_widget.addLegend()
        
        # Add widgets to layout
        main_layout.addWidget(controls_box)
        main_layout.addWidget(self.plot_widget)
        
        # Set default stretch to give more space to the plot
        main_layout.setStretchFactor(controls_box, 0)
        main_layout.setStretchFactor(self.plot_widget, 1)
        
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
                                     units=config.get("x_units", "m"))
        
        if "y_label" in config:
            self.plot_widget.setLabel('left', config["y_label"], 
                                     units=config.get("y_units", "m"))
            
        # Apply axis ranges if provided
        if "x_range" in config:
            x_min, x_max = config["x_range"]
            self.plot_widget.setXRange(x_min, x_max)
            
        if "y_range" in config:
            y_min, y_max = config["y_range"]
            self.plot_widget.setYRange(y_min, y_max)
            
        # Apply aspect ratio lock setting
        if "aspect_locked" in config:
            self.aspect_locked = config["aspect_locked"]
            self.aspect_ratio_check.setChecked(self.aspect_locked)
            self.plot_widget.setAspectLocked(self.aspect_locked)
            
        # Apply grid setting
        if "show_grid" in config:
            show_grid = config["show_grid"]
            self.grid_check.setChecked(show_grid)
            self.plot_widget.showGrid(show_grid, show_grid)
            
    def update_data(self, signal_name: str, data: Any) -> bool:
        """
        Update the view with new data.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display (expected to contain x and y coordinates)
            
        Returns:
            True if the update was successful, False otherwise
        """
        if not isinstance(data, dict):
            print(f"Warning: Expected dict data for signal {signal_name}, got {type(data)}")
            return False
            
        # Check for required data fields
        if "x" not in data or "y" not in data:
            print(f"Warning: Spatial data for {signal_name} must contain 'x' and 'y' coordinates")
            return False
            
        # Store the data
        self.data[signal_name] = data
        
        # Add to visible signals if new
        if signal_name not in self.visible_signals:
            self.visible_signals[signal_name] = True
            self._add_layer_control(signal_name)
            
        # Plot the data
        self._plot_data()
        
        return True
        
    def clear(self):
        """Clear all data from the view."""
        self.data.clear()
        self.visible_signals.clear()
        self.signal_items.clear()
        
        # Clear layer controls
        while self.layers_layout.count():
            item = self.layers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear the plot
        self.plot_widget.clear()
        
        # Re-add the legend
        if hasattr(self, 'legend') and self.legend is not None:
            self.legend.scene().removeItem(self.legend)
        self.legend = self.plot_widget.addLegend()
        
    def set_signal_visible(self, signal_name: str, visible: bool):
        """
        Set the visibility of a signal layer.
        
        Args:
            signal_name: Name of the signal
            visible: Whether the signal should be visible
        """
        if signal_name in self.visible_signals:
            self.visible_signals[signal_name] = visible
            self._plot_data()
            self.signal_toggled.emit(signal_name, visible)
            
    def _add_layer_control(self, signal_name: str):
        """
        Add a control checkbox for a new signal layer.
        
        Args:
            signal_name: Name of the signal layer to add
        """
        # Create a checkbox for this layer
        layer_check = QCheckBox(signal_name)
        layer_check.setChecked(self.visible_signals.get(signal_name, True))
        
        # Connect the checkbox to the visibility control
        layer_check.stateChanged.connect(
            lambda state: self.set_signal_visible(signal_name, state == Qt.CheckState.Checked)
        )
        
        # Add to the layers layout
        self.layers_layout.addWidget(layer_check)
        
    def _plot_data(self):
        """
        Plot all visible signal data.
        """
        # Clear the plot but keep settings
        self.plot_widget.clear()
        
        # Reset the legend
        if hasattr(self, 'legend') and self.legend is not None:
            self.legend.scene().removeItem(self.legend)
        self.legend = self.plot_widget.addLegend()
        
        # Clear previous items
        self.signal_items = {}
        
        # Plot each visible signal
        for signal_name, visible in self.visible_signals.items():
            if not visible or signal_name not in self.data:
                continue
                
            # Ensure we have a color for this signal
            if signal_name not in self.signal_colors:
                # Assign a color from our default colors
                index = len(self.signal_colors) % len(self.default_colors)
                self.signal_colors[signal_name] = self.default_colors[index]
                
            # Create pen and brush if needed
            if signal_name not in self.signal_pens:
                self.signal_pens[signal_name] = pg.mkPen(
                    color=self.signal_colors[signal_name], 
                    width=2
                )
                
            if signal_name not in self.signal_brushes:
                # Semi-transparent brush using the same color
                color = self.signal_colors[signal_name]
                self.signal_brushes[signal_name] = pg.mkBrush(color[0], color[1], color[2], 50)
                
            # Get the data for this signal
            signal_data = self.data[signal_name]
            x_data = signal_data["x"]
            y_data = signal_data["y"]
            
            # Convert to numpy arrays if needed
            if not isinstance(x_data, (np.ndarray, list)):
                x_data = [x_data]
            if not isinstance(y_data, (np.ndarray, list)):
                y_data = [y_data]
                
            # Create a list to store plot items for this signal
            items = []
            
            # Handle different spatial data types based on metadata
            data_type = signal_data.get("type", "point")
            
            if data_type == "point" or data_type == "points":
                # Plot as scatter points
                scatter = pg.ScatterPlotItem(
                    x=x_data, 
                    y=y_data, 
                    pen=self.signal_pens[signal_name], 
                    brush=self.signal_brushes[signal_name],
                    size=8,
                    name=signal_name
                )
                self.plot_widget.addItem(scatter)
                items.append(scatter)
                
            elif data_type == "line" or data_type == "path":
                # Plot as a line
                line = pg.PlotDataItem(
                    x=x_data, 
                    y=y_data, 
                    pen=self.signal_pens[signal_name],
                    name=signal_name
                )
                self.plot_widget.addItem(line)
                items.append(line)
                
            elif data_type == "polygon":
                # Plot as a filled polygon
                polygon = pg.PlotDataItem(
                    x=x_data, 
                    y=y_data, 
                    pen=self.signal_pens[signal_name],
                    fillBrush=self.signal_brushes[signal_name],
                    fillLevel=0,
                    name=signal_name
                )
                self.plot_widget.addItem(polygon)
                items.append(polygon)
                
            else:
                # Default to line plot
                line = pg.PlotDataItem(
                    x=x_data, 
                    y=y_data, 
                    pen=self.signal_pens[signal_name],
                    name=signal_name
                )
                self.plot_widget.addItem(line)
                items.append(line)
                
            # Store the items for this signal
            self.signal_items[signal_name] = items
            
            # Handle orientation if provided (e.g., for vehicle pose)
            if "theta" in signal_data:
                theta = signal_data["theta"]
                if not isinstance(theta, (np.ndarray, list)):
                    theta = [theta]
                    
                # Only add arrows if we have orientation data
                if len(theta) > 0:
                    # Create arrows for orientation
                    arrow_length = signal_data.get("arrow_length", 1.0)
                    for i in range(min(len(x_data), len(y_data), len(theta))):
                        # Create an arrow to show orientation
                        dx = arrow_length * np.cos(theta[i])
                        dy = arrow_length * np.sin(theta[i])
                        
                        arrow = pg.ArrowItem(
                            pos=(x_data[i], y_data[i]),
                            angle=theta[i] * 180 / np.pi - 90,  # Convert to degrees and adjust
                            headLen=15, 
                            tailLen=30,
                            tailWidth=2,
                            pen=self.signal_pens[signal_name],
                            brush=self.signal_colors[signal_name]
                        )
                        self.plot_widget.addItem(arrow)
                        items.append(arrow)
                        
    def _on_aspect_ratio_changed(self, state):
        """Handle changes to the aspect ratio lock setting."""
        self.aspect_locked = state == Qt.CheckState.Checked
        self.plot_widget.setAspectLocked(self.aspect_locked)
        self.view_config_changed.emit({"aspect_locked": self.aspect_locked})
        
    def _on_grid_changed(self, state):
        """Handle changes to the grid visibility setting."""
        show_grid = state == Qt.CheckState.Checked
        self.plot_widget.showGrid(show_grid, show_grid)
        self.view_config_changed.emit({"show_grid": show_grid})
