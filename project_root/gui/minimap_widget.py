#!/usr/bin/env python3

"""
Minimap widget for the Debug Player.

This module provides a minimap widget that shows a zoomed-out overview
of temporal data, allowing users to quickly navigate through large datasets.
"""

from typing import List, Dict, Any, Optional, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSizeF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
import numpy as np

from core.bookmark_manager import BookmarkManager


class MinimapWidget(QWidget):
    """
    Widget that displays a zoomed-out overview of temporal data with navigation capabilities.
    
    This widget shows a compact representation of the entire timeline, with the
    current view highlighted. Users can click or drag on the minimap to navigate
    to different parts of the timeline.
    """
    # Signal emitted when the user navigates using the minimap
    navigation_requested = Signal(float)  # timestamp in seconds
    zoom_changed = Signal(float, float)  # start_time, end_time in seconds
    
    def __init__(self, parent=None, bookmark_manager: Optional[BookmarkManager] = None):
        super().__init__(parent)
        
        # Initialize bookmark manager if provided
        self.bookmark_manager = bookmark_manager
        
        # Data tracking
        self.data_series: Dict[str, Dict[str, np.ndarray]] = {}
        self.current_timestamp = 0.0
        self.start_time = 0.0
        self.end_time = 100.0
        self.view_start = 0.0
        self.view_end = 10.0
        self.timeline_height = 20
        self.graph_height = 50
        self.is_dragging = False
        self.drag_start_x = 0
        self.selected_series = set()  # Names of series to display
        
        # UI setup
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        self.setMouseTracking(True)
        
        # Background and foreground colors
        self.background_color = QColor(40, 44, 52)  # Dark background
        self.timeline_color = QColor(60, 64, 72)    # Darker for timeline
        self.view_rect_color = QColor(65, 105, 225, 100)  # Semi-transparent blue
        self.current_time_color = QColor(255, 50, 50)  # Bright red for current time
        self.bookmark_color = QColor(50, 205, 50)  # Green for bookmarks
        
        # Series colors (will cycle for multiple series)
        self.series_colors = [
            QColor(52, 152, 219),  # Blue
            QColor(46, 204, 113),  # Green
            QColor(155, 89, 182),  # Purple
            QColor(241, 196, 15),  # Yellow
            QColor(231, 76, 60),   # Red
            QColor(26, 188, 156),  # Turquoise
        ]
    
    def add_data_series(self, name: str, timestamps: np.ndarray, values: np.ndarray):
        """
        Add a data series to be displayed in the minimap.
        
        Args:
            name: Identifier for this data series
            timestamps: Array of timestamps (in seconds)
            values: Array of values corresponding to the timestamps
        """
        # Ensure data is valid
        if len(timestamps) != len(values):
            print(f"Warning: Timestamps and values must have the same length for series {name}")
            return
            
        if len(timestamps) == 0:
            print(f"Warning: Empty data series {name}")
            return
        
        # Store the data
        self.data_series[name] = {
            "timestamps": timestamps,
            "values": values,
            "min": np.min(values),
            "max": np.max(values)
        }
        
        # Add to selected series
        self.selected_series.add(name)
        
        # Update time range if needed
        self.start_time = min(self.start_time, timestamps[0])
        self.end_time = max(self.end_time, timestamps[-1])
        
        # Force redraw
        self.update()
    
    def clear_data(self):
        """
        Clear all data series.
        """
        self.data_series.clear()
        self.selected_series.clear()
        self.start_time = 0.0
        self.end_time = 100.0
        self.update()
    
    def set_current_timestamp(self, timestamp: float):
        """
        Set the current timestamp indicator.
        
        Args:
            timestamp: Current timestamp in seconds
        """
        self.current_timestamp = timestamp
        self.update()
    
    def set_view_range(self, start_time: float, end_time: float):
        """
        Set the currently visible time range.
        
        Args:
            start_time: Start of visible range in seconds
            end_time: End of visible range in seconds
        """
        self.view_start = start_time
        self.view_end = end_time
        self.update()
    
    def _time_to_x(self, time: float) -> float:
        """
        Convert a timestamp to an x-coordinate in the widget.
        
        Args:
            time: Timestamp in seconds
            
        Returns:
            X-coordinate in the widget
        """
        time_range = max(0.1, self.end_time - self.start_time)
        widget_width = self.width()
        return ((time - self.start_time) / time_range) * widget_width
    
    def _x_to_time(self, x: float) -> float:
        """
        Convert an x-coordinate to a timestamp.
        
        Args:
            x: X-coordinate in the widget
            
        Returns:
            Timestamp in seconds
        """
        time_range = max(0.1, self.end_time - self.start_time)
        widget_width = self.width()
        return self.start_time + (x / widget_width) * time_range
    
    def _value_to_y(self, value: float, min_val: float, max_val: float) -> float:
        """
        Convert a data value to a y-coordinate in the graph area.
        
        Args:
            value: Data value
            min_val: Minimum value in the data series
            max_val: Maximum value in the data series
            
        Returns:
            Y-coordinate in the widget
        """
        value_range = max(0.1, max_val - min_val)
        y_offset = self.timeline_height
        return y_offset + self.graph_height - ((value - min_val) / value_range) * self.graph_height
    
    def paintEvent(self, event):
        """
        Draw the minimap widget.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(event.rect(), self.background_color)
        
        # Draw timeline background
        timeline_rect = QRectF(0, 0, self.width(), self.timeline_height)
        painter.fillRect(timeline_rect, self.timeline_color)
        
        # Draw view range rectangle
        view_start_x = self._time_to_x(self.view_start)
        view_end_x = self._time_to_x(self.view_end)
        view_rect = QRectF(view_start_x, 0, view_end_x - view_start_x, self.timeline_height)
        painter.fillRect(view_rect, self.view_rect_color)
        
        # Draw time indicators (ticks)
        self._draw_time_ticks(painter)
        
        # Draw bookmarks if available
        if self.bookmark_manager:
            self._draw_bookmarks(painter)
        
        # Draw data series
        self._draw_data_series(painter)
        
        # Draw current timestamp indicator
        current_x = self._time_to_x(self.current_timestamp)
        if 0 <= current_x <= self.width():
            painter.setPen(QPen(self.current_time_color, 2))
            painter.drawLine(QPointF(current_x, 0), QPointF(current_x, self.height()))
    
    def _draw_time_ticks(self, painter: QPainter):
        """
        Draw time tick marks on the timeline.
        
        Args:
            painter: QPainter to use for drawing
        """
        time_range = self.end_time - self.start_time
        
        # Determine appropriate tick interval based on range
        if time_range <= 10:
            interval = 1.0  # 1 second
        elif time_range <= 60:
            interval = 5.0  # 5 seconds
        elif time_range <= 300:
            interval = 30.0  # 30 seconds
        elif time_range <= 3600:
            interval = 300.0  # 5 minutes
        else:
            interval = 3600.0  # 1 hour
        
        # Draw ticks
        painter.setPen(QPen(Qt.lightGray, 1))
        
        tick_start = math.ceil(self.start_time / interval) * interval
        tick_end = self.end_time
        
        for t in np.arange(tick_start, tick_end, interval):
            x = self._time_to_x(t)
            painter.drawLine(QPointF(x, 0), QPointF(x, self.timeline_height))
    
    def _draw_bookmarks(self, painter: QPainter):
        """
        Draw bookmark indicators on the timeline.
        
        Args:
            painter: QPainter to use for drawing
        """
        bookmarks = self.bookmark_manager.get_bookmarks()
        
        for bookmark in bookmarks:
            x = self._time_to_x(bookmark.timestamp)
            if 0 <= x <= self.width():
                # Create a small triangle pointing down
                path = QPainterPath()
                path.moveTo(x, 0)
                path.lineTo(x - 5, -5)
                path.lineTo(x + 5, -5)
                path.closeSubpath()
                
                # Draw with bookmark color
                color = QColor(bookmark.color)
                painter.fillPath(path, color)
                
                # Draw a line from triangle to bottom of timeline
                painter.setPen(QPen(color, 1, Qt.DashLine))
                painter.drawLine(QPointF(x, 0), QPointF(x, self.timeline_height))
    
    def _draw_data_series(self, painter: QPainter):
        """
        Draw data series as mini-graphs.
        
        Args:
            painter: QPainter to use for drawing
        """
        if not self.data_series or not self.selected_series:
            return
        
        # Draw each selected series
        for i, name in enumerate(self.selected_series):
            if name not in self.data_series:
                continue
                
            series = self.data_series[name]
            color = self.series_colors[i % len(self.series_colors)]
            
            timestamps = series["timestamps"]
            values = series["values"]
            min_val = series["min"]
            max_val = series["max"]
            
            # Create a path for the line
            path = QPainterPath()
            
            # Move to first point
            x = self._time_to_x(timestamps[0])
            y = self._value_to_y(values[0], min_val, max_val)
            path.moveTo(x, y)
            
            # Add lines to each point
            for j in range(1, len(timestamps)):
                x = self._time_to_x(timestamps[j])
                y = self._value_to_y(values[j], min_val, max_val)
                path.lineTo(x, y)
            
            # Draw the path
            painter.setPen(QPen(color, 1))
            painter.drawPath(path)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press for navigation.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_x = event.pos().x()
            
            # If clicked in the timeline area, jump to that time
            if event.pos().y() <= self.timeline_height:
                timestamp = self._x_to_time(event.pos().x())
                self.navigation_requested.emit(timestamp)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse movement for drag navigation.
        
        Args:
            event: Mouse event
        """
        if self.is_dragging:
            # Calculate time difference from drag
            current_x = event.pos().x()
            dx = current_x - self.drag_start_x
            
            if dx != 0:
                # Calculate time delta based on drag distance
                time_range = self.end_time - self.start_time
                time_delta = (dx / self.width()) * time_range
                
                # Calculate new view range
                view_width = self.view_end - self.view_start
                new_start = max(self.start_time, self.view_start - time_delta)
                new_end = min(self.end_time, new_start + view_width)
                
                # Adjust if we hit the edge
                if new_end >= self.end_time:
                    new_start = self.end_time - view_width
                
                if new_start <= self.start_time:
                    new_start = self.start_time
                    new_end = new_start + view_width
                
                # Update the view range
                self.zoom_changed.emit(new_start, new_end)
                self.view_start = new_start
                self.view_end = new_end
                self.update()
                
                # Reset drag start for continuous dragging
                self.drag_start_x = current_x
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release to end dragging.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self.is_dragging = False


# Add import at the top to ensure the widget works correctly
import math  # For ceil function used in _draw_time_ticks
