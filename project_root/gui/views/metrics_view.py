#!/usr/bin/env python3

"""
MetricsView component for the Debug Player.

This module provides a widget for displaying key metrics, statistics,
and performance indicators in a compact and readable format.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFrame, QSizePolicy, QScrollArea, QComboBox, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QColor, QPalette, QFont, QFontMetrics

from core.view_manager import ViewBase


class MetricWidget(QFrame):
    """
    Widget for displaying a single metric with title, value, and optional trend.
    """
    # Signal emitted when the metric is clicked
    clicked = Signal(str)  # Emits metric_id
    
    def __init__(self, metric_id: str, title: str, parent=None):
        super().__init__(parent)
        self.metric_id = metric_id
        self.title = title
        self.history: List[float] = []  # For tracking value history and trends
        self.max_history = 10  # Number of historical values to track
        
        self._setup_ui()
        
    def _setup_ui(self):
        """
        Set up the user interface for the metric widget.
        """
        # Set frame style and make it clickable
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set minimum size
        self.setMinimumSize(120, 80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title label (smaller font)
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(9)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Value label (larger font)
        self.value_label = QLabel("N/A")
        self.value_label.setAlignment(Qt.AlignCenter)
        value_font = self.value_label.font()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        layout.addWidget(self.value_label)
        
        # Trend/unit label
        self.trend_label = QLabel()
        self.trend_label.setAlignment(Qt.AlignCenter)
        trend_font = self.trend_label.font()
        trend_font.setPointSize(8)
        self.trend_label.setFont(trend_font)
        layout.addWidget(self.trend_label)
        
    def set_value(self, value: Union[float, int, str], unit: str = "", precision: int = 2):
        """
        Set the current value of the metric.
        
        Args:
            value: The numeric or string value
            unit: Optional unit to display
            precision: Decimal precision for numeric values
        """
        # Format the value based on its type
        if isinstance(value, (float, int)):
            # Store value in history for trend calculation
            numeric_value = float(value)
            if len(self.history) >= self.max_history:
                self.history.pop(0)  # Remove oldest value
            self.history.append(numeric_value)
            
            # Format the displayed value
            if isinstance(value, int) or value.is_integer():
                self.value_label.setText(f"{int(value)}")
            else:
                self.value_label.setText(f"{value:.{precision}f}")
                
            # Set the trend indicator
            self._update_trend(unit)
        else:
            # Handle string or other values
            self.value_label.setText(str(value))
            if unit:
                self.trend_label.setText(unit)
            else:
                self.trend_label.setText("")
    
    def set_color(self, color: QColor):
        """
        Set the color for the value text.
        
        Args:
            color: Color to use for the value
        """
        palette = self.value_label.palette()
        palette.setColor(QPalette.WindowText, color)
        self.value_label.setPalette(palette)
    
    def _update_trend(self, unit: str):
        """
        Update the trend indicator based on value history.
        
        Args:
            unit: Unit to display alongside the trend
        """
        if len(self.history) < 2:
            if unit:
                self.trend_label.setText(unit)
            else:
                self.trend_label.setText("")
            return
            
        # Calculate trend direction
        current = self.history[-1]
        previous = self.history[-2]
        diff = current - previous
        
        # Calculate percent change
        if previous != 0:
            percent = 100 * diff / abs(previous)
            
            # Show trend with arrow and percentage
            if diff > 0:
                if unit:
                    self.trend_label.setText(f"↑ {percent:.1f}% {unit}")
                else:
                    self.trend_label.setText(f"↑ {percent:.1f}%")
                # Set color to green for positive trend
                palette = self.trend_label.palette()
                palette.setColor(QPalette.WindowText, QColor(0, 170, 0))
                self.trend_label.setPalette(palette)
            elif diff < 0:
                if unit:
                    self.trend_label.setText(f"↓ {abs(percent):.1f}% {unit}")
                else:
                    self.trend_label.setText(f"↓ {abs(percent):.1f}%")
                # Set color to red for negative trend
                palette = self.trend_label.palette()
                palette.setColor(QPalette.WindowText, QColor(200, 0, 0))
                self.trend_label.setPalette(palette)
            else:
                if unit:
                    self.trend_label.setText(f"− 0% {unit}")
                else:
                    self.trend_label.setText("− 0%")
                # Reset to default color
                self.trend_label.setPalette(QPalette())
        else:
            # Can't calculate percentage if previous was zero
            if unit:
                self.trend_label.setText(unit)
            else:
                self.trend_label.setText("")
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events to emit the clicked signal.
        """
        self.clicked.emit(self.metric_id)
        super().mousePressEvent(event)


class MetricsView(ViewBase):
    """
    View for displaying key metrics and statistics.
    
    This view provides a dashboard-like display for important metrics,
    with support for different layouts, trends, and visual cues.
    """
    # Signal emitted when a metric is clicked
    metric_clicked = Signal(str)  # Emits metric_id
    
    def __init__(self, view_id: str, parent=None):
        super().__init__(view_id, parent)
        
        # Set supported signal types
        self.supported_signal_types = {'temporal', 'categorical', 'statistical'}
        
        # Initialize data structures
        self.signal_data: Dict[str, Any] = {}
        self.signal_metadata: Dict[str, Dict[str, Any]] = {}
        self.active_signal: Optional[str] = None
        
        # Metrics configuration
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.layout_columns = 3  # Number of columns in the grid layout
        
        # Create the widget
        self._setup_ui()
        
        # Set up auto-refresh timer (for real-time displays)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_metrics)
        
    def _setup_ui(self):
        """
        Set up the user interface for the metrics view.
        """
        # Main widget
        self.widget = QWidget()
        main_layout = QVBoxLayout()
        self.widget.setLayout(main_layout)
        
        # Add controls section at the top
        controls_layout = QHBoxLayout()
        
        # Signal selector
        controls_layout.addWidget(QLabel("Data Source:"))
        self.signal_combo = QComboBox()
        self.signal_combo.currentTextChanged.connect(self._on_signal_changed)
        controls_layout.addWidget(self.signal_combo)
        
        # Layout selector
        controls_layout.addWidget(QLabel("Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["1 Column", "2 Columns", "3 Columns", "4 Columns"])
        self.layout_combo.setCurrentIndex(2)  # Default to 3 columns
        self.layout_combo.currentIndexChanged.connect(self._on_layout_changed)
        controls_layout.addWidget(self.layout_combo)
        
        # Add stretch to push controls to the left
        controls_layout.addStretch(1)
        
        main_layout.addLayout(controls_layout)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Scroll area for metrics
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(self.scroll_area)
        
        # Container for metrics
        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout(self.metrics_container)
        self.metrics_layout.setSpacing(8)
        self.scroll_area.setWidget(self.metrics_container)
        
        # Status label
        self.status_label = QLabel("No metrics available")
        main_layout.addWidget(self.status_label)
    
    def _on_signal_changed(self, signal_name: str):
        """
        Handle signal selection change.
        
        Args:
            signal_name: The newly selected signal name
        """
        if not signal_name or signal_name not in self.signal_data:
            return
            
        self.active_signal = signal_name
        self._refresh_metrics()
            
    def _on_layout_changed(self, index: int):
        """
        Handle layout selection change.
        
        Args:
            index: Index of the selected layout option
        """
        # Convert index to number of columns (index 0 = 1 column)
        self.layout_columns = index + 1
        
        # Refresh the metrics layout
        self._refresh_metrics()
    
    def _refresh_metrics(self):
        """
        Refresh the metrics display with current data.
        """
        if not self.active_signal or self.active_signal not in self.signal_data:
            return
            
        # Get the current data
        data = self.signal_data[self.active_signal]
        if not isinstance(data, dict):
            # Try to convert data to dictionary if possible
            if hasattr(data, '__dict__'):
                data = vars(data)
            elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], dict):
                # Use the first item if it's a list of dicts
                data = data[0]
            else:
                # Can't display this type of data as metrics
                self.status_label.setText(f"Cannot display {type(data).__name__} as metrics")
                return
            
        # Clear existing metrics widgets
        self._clear_metrics_layout()
        
        # Add metrics widgets based on current data
        row, col = 0, 0
        
        for key, value in data.items():
            # Create or get metric widget
            metric_id = f"{self.active_signal}_{key}"
            if metric_id not in self.metrics:
                metric_widget = MetricWidget(metric_id, key)
                metric_widget.clicked.connect(self._on_metric_clicked)
                self.metrics[metric_id] = {
                    "widget": metric_widget,
                    "key": key
                }
            else:
                metric_widget = self.metrics[metric_id]["widget"]
            
            # Get metadata for this metric
            metadata = self.signal_metadata.get(self.active_signal, {})
            precision = metadata.get("precision", 2)
            unit = ""
            
            # Check if units are specified for this metric
            if "units" in metadata:
                if isinstance(metadata["units"], dict) and key in metadata["units"]:
                    unit = metadata["units"][key]
                elif isinstance(metadata["units"], str):
                    unit = metadata["units"]
            
            # Set the metric value
            metric_widget.set_value(value, unit, precision)
            
            # Set color based on critical values if defined
            if "critical_values" in metadata and isinstance(metadata["critical_values"], dict):
                if key in metadata["critical_values"] and isinstance(value, (int, float)):
                    critical_value = metadata["critical_values"][key]
                    if isinstance(critical_value, dict):
                        # Check range
                        min_val = critical_value.get("min")
                        max_val = critical_value.get("max")
                        
                        if min_val is not None and value < min_val:
                            metric_widget.set_color(QColor(200, 0, 0))  # Red for below min
                        elif max_val is not None and value > max_val:
                            metric_widget.set_color(QColor(200, 0, 0))  # Red for above max
                        else:
                            metric_widget.set_color(QColor(0, 170, 0))  # Green for normal
                    elif isinstance(critical_value, (int, float)):
                        # Check exact value
                        if abs(value - critical_value) < 0.001:  # Close enough
                            metric_widget.set_color(QColor(200, 0, 0))  # Red for critical
            
            # Add to layout
            self.metrics_layout.addWidget(metric_widget, row, col)
            
            # Update position for next metric
            col += 1
            if col >= self.layout_columns:
                col = 0
                row += 1
        
        # Update status
        self.status_label.setText(f"{self.active_signal}: {len(data)} metrics")
    
    def _clear_metrics_layout(self):
        """
        Clear all widgets from the metrics layout.
        """
        # Remove all widgets from the layout
        while self.metrics_layout.count():
            item = self.metrics_layout.takeAt(0)
            if item.widget() is not None:
                # Don't delete the widget, just remove from layout
                self.metrics_layout.removeWidget(item.widget())
                item.widget().setParent(None)
    
    def _on_metric_clicked(self, metric_id: str):
        """
        Handle metric widget click.
        
        Args:
            metric_id: ID of the clicked metric
        """
        self.metric_clicked.emit(metric_id)
    
    def update_data(self, signal_name: str, data: Any) -> bool:
        """
        Update the view with new data for a signal.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Store the data
            self.signal_data[signal_name] = data
            
            # Update the signal selector if needed
            if signal_name not in [self.signal_combo.itemText(i) for i in range(self.signal_combo.count())]:
                self.signal_combo.addItem(signal_name)
            
            # If this is the first signal or the active signal, update the display
            if self.active_signal is None or signal_name == self.active_signal:
                self.active_signal = signal_name
                self.signal_combo.setCurrentText(signal_name)
                self._refresh_metrics()
            
            return True
        except Exception as e:
            print(f"Error updating metrics view with signal {signal_name}: {str(e)}")
            return False
    
    def get_widget(self) -> QWidget:
        """
        Get the Qt widget for this view.
        
        Returns:
            The QWidget that displays this view
        """
        return self.widget
    
    def set_signal_metadata(self, signal_name: str, metadata: Dict[str, Any]):
        """
        Set metadata for a signal.
        
        Args:
            signal_name: Name of the signal
            metadata: Metadata dictionary
        """
        self.signal_metadata[signal_name] = metadata
        
        # Refresh if this is the active signal
        if signal_name == self.active_signal:
            self._refresh_metrics()
    
    def start_auto_refresh(self, interval_ms: int = 1000):
        """
        Start auto-refreshing metrics display.
        
        Args:
            interval_ms: Refresh interval in milliseconds
        """
        self.refresh_timer.start(interval_ms)
    
    def stop_auto_refresh(self):
        """
        Stop auto-refreshing metrics display.
        """
        self.refresh_timer.stop()
    
    def clear(self):
        """
        Clear all data from the view.
        """
        self.signal_data.clear()
        self.active_signal = None
        self.signal_combo.clear()
        self._clear_metrics_layout()
        self.status_label.setText("No metrics available")
