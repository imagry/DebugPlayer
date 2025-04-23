#!/usr/bin/env python3
"""
Timestamp slider widget for the Debug Player application.

This module provides a slider-based control for navigating through time series data,
with playback controls and view range management functionality.
"""

from PySide6.QtWidgets import (QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QComboBox, QLineEdit)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon


class TimestampSlider(QWidget):
    """
    Widget for controlling timestamp playback and navigation.
    
    This widget provides slider-based navigation through time series data,
    with additional controls for playback, timestep control, and zoom functionality.
    """
    # Signals
    timestamp_changed = Signal(float)  # Signal emitted when timestamp changes
    range_changed = Signal(float, float)  # Signal emitted when view range changes
    
    def __init__(self, plot_manager, view_manager=None, current_timestamp=0.0, parent=None):
        """
        Initialize the timestamp slider with the given plot manager.
        
        Args:
            plot_manager: The plot manager that will receive timestamp updates
            view_manager: Optional view manager that will receive timestamp updates
            current_timestamp: Initial timestamp value
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.plot_manager = plot_manager
        self.view_manager = view_manager
        self.time_range = (0.0, 100.0)  # Default range if no data
        self.view_range = (0.0, 10.0)   # Default view window (zoomed in portion)
        self.step_size = 0.1  # Default step size in seconds
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create slider controls
        slider_controls = QHBoxLayout()
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)  # Use 1000 for fine-grained control, we'll scale the values
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(100)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        slider_controls.addWidget(self.slider)
        
        # Create timestamp display
        self.timestamp_display = QLineEdit()
        self.timestamp_display.setFixedWidth(100)
        self.timestamp_display.setAlignment(Qt.AlignRight)
        self.timestamp_display.setText(str(current_timestamp))
        self.timestamp_display.editingFinished.connect(self.on_timestamp_edited)
        slider_controls.addWidget(self.timestamp_display)
        
        slider_controls.addWidget(QLabel("s"))  # Add second units label
        
        layout.addLayout(slider_controls)
        
        # Create range display
        range_controls = QHBoxLayout()
        
        range_controls.addWidget(QLabel("View Range:"))
        self.start_time_display = QLineEdit()
        self.start_time_display.setFixedWidth(70)
        self.start_time_display.setAlignment(Qt.AlignRight)
        self.start_time_display.setText(str(self.view_range[0]))
        self.start_time_display.editingFinished.connect(self.on_range_edited)
        range_controls.addWidget(self.start_time_display)
        
        range_controls.addWidget(QLabel("to"))
        
        self.end_time_display = QLineEdit()
        self.end_time_display.setFixedWidth(70)
        self.end_time_display.setAlignment(Qt.AlignRight)
        self.end_time_display.setText(str(self.view_range[1]))
        self.end_time_display.editingFinished.connect(self.on_range_edited)
        range_controls.addWidget(self.end_time_display)
        
        range_controls.addWidget(QLabel("s"))  # Add second units label
        
        # Add zoom buttons
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.on_zoom_in_clicked)
        range_controls.addWidget(self.zoom_in_button)
        
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.on_zoom_out_clicked)
        range_controls.addWidget(self.zoom_out_button)
        
        # Add spacer
        range_controls.addStretch(1)
        
        layout.addLayout(range_controls)
        
        # Create playback controls
        playback_controls = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.on_play_clicked)
        playback_controls.addWidget(self.play_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        playback_controls.addWidget(self.stop_button)
        
        # Add speed control
        playback_controls.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x", "4x"])
        self.speed_combo.setCurrentText("1x")
        playback_controls.addWidget(self.speed_combo)
        
        self.step_backward_button = QPushButton("Step <")
        self.step_backward_button.clicked.connect(self.on_step_backward_clicked)
        playback_controls.addWidget(self.step_backward_button)
        
        self.step_forward_button = QPushButton("Step >")
        self.step_forward_button.clicked.connect(self.on_step_forward_clicked)
        playback_controls.addWidget(self.step_forward_button)
        
        # Add spacer to push buttons to the left
        playback_controls.addStretch(1)
        
        layout.addLayout(playback_controls)
        
        # Playing state
        self.is_playing = False
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.on_play_timer)
        
        # Initialize with the provided timestamp
        self.set_timestamp(current_timestamp)
    
    def set_time_range(self, start_time, end_time):
        """
        Set the total time range covered by the data.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
        """
        self.time_range = (start_time, end_time)
        
        # Adjust view range if necessary
        if self.view_range[0] < start_time:
            self.view_range = (start_time, start_time + (self.view_range[1] - self.view_range[0]))
        
        if self.view_range[1] > end_time:
            self.view_range = (max(start_time, end_time - (self.view_range[1] - self.view_range[0])), end_time)
        
        # Update displays
        self.start_time_display.setText(str(self.view_range[0]))
        self.end_time_display.setText(str(self.view_range[1]))
        
        # If current timestamp is outside range, adjust it
        current_timestamp = float(self.timestamp_display.text())
        if current_timestamp < start_time or current_timestamp > end_time:
            self.set_timestamp((start_time + end_time) / 2)
    
    def set_view_range(self, start_time, end_time):
        """
        Set the visible time range (zoom window).
        
        Args:
            start_time: Start time of visible range in seconds
            end_time: End time of visible range in seconds
        """
        # Clamp to valid range
        start_time = max(self.time_range[0], min(start_time, self.time_range[1]))
        end_time = max(start_time, min(end_time, self.time_range[1]))
        
        self.view_range = (start_time, end_time)
        
        # Update the UI
        self.start_time_display.setText(f"{start_time:.2f}")
        self.end_time_display.setText(f"{end_time:.2f}")
        
        # Emit signal for other components
        self.range_changed.emit(start_time, end_time)
    
    def set_timestamp(self, timestamp):
        """
        Set the current timestamp and update the UI.
        
        Args:
            timestamp: Current timestamp in seconds
        """
        # Clamp timestamp to valid range
        timestamp = max(self.time_range[0], min(timestamp, self.time_range[1]))
        
        # Update UI
        self.timestamp_display.setText(f"{timestamp:.2f}")
        
        # Update slider position without triggering value change signal
        self.slider.blockSignals(True)
        slider_pos = self._time_to_slider_pos(timestamp)
        self.slider.setValue(slider_pos)
        self.slider.blockSignals(False)
        
        # Emit signal and request data update
        self.timestamp_changed.emit(timestamp)
        
        # Update plot data
        if self.plot_manager:
            self.plot_manager.request_data(timestamp)
    
    def _time_to_slider_pos(self, timestamp):
        """
        Convert a timestamp to a slider position.
        
        Args:
            timestamp: Timestamp in seconds
            
        Returns:
            Integer slider position
        """
        time_range = self.time_range[1] - self.time_range[0]
        if time_range <= 0:
            return 0
        
        normalized_pos = (timestamp - self.time_range[0]) / time_range
        return int(normalized_pos * self.slider.maximum())
    
    def _slider_pos_to_time(self, pos):
        """
        Convert a slider position to a timestamp.
        
        Args:
            pos: Integer slider position
            
        Returns:
            Timestamp in seconds
        """
        time_range = self.time_range[1] - self.time_range[0]
        normalized_pos = pos / self.slider.maximum()
        return self.time_range[0] + (normalized_pos * time_range)
    
    def on_slider_value_changed(self, value):
        """
        Handle slider value changes.
        
        Args:
            value: The new slider position
        """
        timestamp = self._slider_pos_to_time(value)
        
        # Update timestamp display without triggering editingFinished signal
        self.timestamp_display.blockSignals(True)
        self.timestamp_display.setText(f"{timestamp:.2f}")
        self.timestamp_display.blockSignals(False)
        
        # Emit signal and request data update
        self.timestamp_changed.emit(timestamp)
        
        # Update plot data
        if self.plot_manager:
            self.plot_manager.request_data(timestamp)
    
    def on_timestamp_edited(self):
        """
        Handle manual edits to the timestamp display.
        """
        try:
            timestamp = float(self.timestamp_display.text())
            self.set_timestamp(timestamp)
        except ValueError:
            # Revert to current slider value if input is invalid
            current_time = self._slider_pos_to_time(self.slider.value())
            self.timestamp_display.setText(f"{current_time:.2f}")
    
    def on_range_edited(self):
        """
        Handle manual edits to the view range displays.
        """
        try:
            start_time = float(self.start_time_display.text())
            end_time = float(self.end_time_display.text())
            
            if start_time < end_time:
                self.set_view_range(start_time, end_time)
            else:
                # Revert to current values if range is invalid
                self.start_time_display.setText(f"{self.view_range[0]:.2f}")
                self.end_time_display.setText(f"{self.view_range[1]:.2f}")
        except ValueError:
            # Revert to current values if input is invalid
            self.start_time_display.setText(f"{self.view_range[0]:.2f}")
            self.end_time_display.setText(f"{self.view_range[1]:.2f}")
    
    def on_zoom_in_clicked(self):
        """
        Zoom in on the current position (reduce view range).
        """
        current_time = float(self.timestamp_display.text())
        view_width = self.view_range[1] - self.view_range[0]
        new_width = max(1.0, view_width * 0.5)  # At least 1 second wide
        
        # Center on current timestamp
        new_start = max(self.time_range[0], current_time - (new_width / 2))
        new_end = min(self.time_range[1], new_start + new_width)
        
        # If we hit the end, adjust start to maintain width
        if new_end >= self.time_range[1]:
            new_start = max(self.time_range[0], self.time_range[1] - new_width)
        
        self.set_view_range(new_start, new_end)
    
    def on_zoom_out_clicked(self):
        """
        Zoom out from the current position (increase view range).
        """
        current_time = float(self.timestamp_display.text())
        view_width = self.view_range[1] - self.view_range[0]
        new_width = min(self.time_range[1] - self.time_range[0], view_width * 2)  # At most full range
        
        # Center on current timestamp
        new_start = max(self.time_range[0], current_time - (new_width / 2))
        new_end = min(self.time_range[1], new_start + new_width)
        
        # If we hit the end, adjust start to maintain width
        if new_end >= self.time_range[1]:
            new_start = max(self.time_range[0], self.time_range[1] - new_width)
        
        self.set_view_range(new_start, new_end)
    
    def on_play_clicked(self):
        """
        Start playback of the timeline.
        """
        if not self.is_playing:
            self.is_playing = True
            self.play_button.setText("Pause")
            self.stop_button.setEnabled(True)
            
            # Start the timer for playback
            self.play_timer.start(50)  # Update approximately every 50ms
    
    def on_stop_clicked(self):
        """
        Stop playback and reset to the beginning of the view range.
        """
        if self.is_playing:
            self.play_timer.stop()
            self.is_playing = False
            
        self.play_button.setText("Play")
        self.stop_button.setEnabled(False)
        
        # Reset to beginning of view range
        self.set_timestamp(self.view_range[0])
    
    def on_play_timer(self):
        """
        Update timestamp during playback.
        """
        if not self.is_playing:
            return
        
        current_time = float(self.timestamp_display.text())
        
        # Get playback speed multiplier
        speed_text = self.speed_combo.currentText()
        speed_multiplier = float(speed_text.rstrip('x'))
        
        # Calculate new timestamp
        new_time = current_time + (self.step_size * speed_multiplier)
        
        # If we reached the end of view range, loop or stop
        if new_time > self.view_range[1]:
            new_time = self.view_range[0]  # Loop back to beginning
        
        # Update the timestamp
        self.set_timestamp(new_time)
    
    def on_step_forward_clicked(self):
        """
        Step forward by one time step.
        """
        current_time = float(self.timestamp_display.text())
        new_time = min(self.time_range[1], current_time + self.step_size)
        self.set_timestamp(new_time)
    
    def on_step_backward_clicked(self):
        """
        Step backward by one time step.
        """
        current_time = float(self.timestamp_display.text())
        new_time = max(self.time_range[0], current_time - self.step_size)
        self.set_timestamp(new_time)
