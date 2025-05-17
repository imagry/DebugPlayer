"""
Timeline controller for managing playback state and time synchronization.

This module provides the TimelineController class which manages the current playback state,
time range, and coordinates updates between data sources and visualization components.
"""

from typing import Optional, Tuple, Dict, Any, List, Callable
from PySide6.QtCore import QObject, QTimer, Signal, Slot, QTime
import numpy as np
import time

class TimelineController(QObject):
    """
    Controller class for managing the timeline and playback state.
    
    This class handles:
    - Current time tracking
    - Playback state (playing/paused)
    - Time range management
    - Playback speed control
    - Coordination between data sources and visualization
    """
    
    # Signal emitted when the current time changes
    timeChanged = Signal(float)
    
    # Signal emitted when the time range is updated
    timeRangeChanged = Signal(float, float)
    
    # Signal emitted when playback state changes (playing/paused)
    playbackStateChanged = Signal(bool)
    
    def __init__(self, plot_manager=None, update_interval: int = 50):
        """
        Initialize the timeline controller.
        
        Args:
            plot_manager: Reference to the PlotManager instance (optional)
            update_interval: Time between updates in milliseconds
        """
        super().__init__()
        self._current_time = 0.0
        self._min_time = 0.0
        self._max_time = 1.0  # Default to avoid division by zero
        self._playback_speed = 1.0
        self._is_playing = False
        self._last_update_time = 0.0
        self._plot_manager = plot_manager
        
        # Set up update timer
        self._update_timer = QTimer()
        self._update_timer.setInterval(update_interval)
        self._update_timer.timeout.connect(self._on_update_timer)
        
        # Keep track of time when playback starts/pauses for smooth resuming
        self._playback_start_time = 0.0
        
    @property
    def current_time(self) -> float:
        """Get the current time in seconds."""
        return self._current_time
    
    @current_time.setter
    def current_time(self, value: float):
        """Set the current time in seconds and emit timeChanged signal."""
        if value != self._current_time:
            self._current_time = max(self._min_time, min(value, self._max_time))
            self.timeChanged.emit(self._current_time)
    
    @property
    def min_time(self) -> float:
        """Get the minimum time in the timeline."""
        return self._min_time
    
    @property
    def max_time(self) -> float:
        """Get the maximum time in the timeline."""
        return self._max_time
    
    @property
    def duration(self) -> float:
        """Get the total duration of the timeline."""
        return self._max_time - self._min_time
    
    @property
    def playback_speed(self) -> float:
        """Get the current playback speed multiplier."""
        return self._playback_speed
    
    @playback_speed.setter
    def playback_speed(self, speed: float):
        """Set the playback speed multiplier."""
        if speed <= 0:
            raise ValueError("Playback speed must be positive")
        self._playback_speed = speed
    
    @property
    def is_playing(self) -> bool:
        """Check if playback is currently active."""
        return self._is_playing
    
    def update_time_range(self, min_time: float, max_time: float):
        """
        Update the time range of the timeline.
        
        Args:
            min_time: New minimum time in seconds
            max_time: New maximum time in seconds (must be > min_time)
        """
        if max_time <= min_time:
            raise ValueError("max_time must be greater than min_time")
            
        # Update time range
        self._min_time = min_time
        self._max_time = max_time
        
        # Clamp current time to new range
        self.current_time = max(min_time, min(self._current_time, max_time))
        
        # Emit signal with new range
        self.timeRangeChanged.emit(self._min_time, self._max_time)
    
    def seek(self, time_sec: float):
        """
        Seek to a specific time in the timeline.
        
        Args:
            time_sec: Time to seek to in seconds
        """
        self.current_time = time_sec
        self._last_update_time = time.time()
    
    def play(self):
        """Start or resume playback."""
        if not self._is_playing:
            self._is_playing = True
            self._playback_start_time = time.time() - (self._current_time - self._min_time) / self._playback_speed
            self._update_timer.start()
            self.playbackStateChanged.emit(True)
    
    def pause(self):
        """Pause playback."""
        if self._is_playing:
            self._is_playing = False
            self._update_timer.stop()
            self.playbackStateChanged.emit(False)
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self._is_playing:
            self.pause()
        else:
            self.play()
    
    def step_forward(self, step_sec: float = 0.1):
        """
        Step forward by a fixed time increment.
        
        Args:
            step_sec: Time step in seconds
        """
        self.pause()
        self.seek(min(self._current_time + step_sec, self._max_time))
    
    def step_backward(self, step_sec: float = 0.1):
        """
        Step backward by a fixed time increment.
        
        Args:
            step_sec: Time step in seconds
        """
        self.pause()
        self.seek(max(self._current_time - step_sec, self._min_time))
    
    def _on_update_timer(self):
        """Handle timer updates during playback."""
        if not self._is_playing:
            return
            
        current_real_time = time.time()
        
        # Initialize playback start time if this is the first update
        if self._playback_start_time == 0.0:
            self._playback_start_time = current_real_time - self._current_time / self._playback_speed
            
        # Calculate the new time based on real time elapsed and playback speed
        elapsed = (current_real_time - self._playback_start_time) * self._playback_speed
        new_time = self._min_time + elapsed
        
        # Check if we've reached the end
        if new_time >= self._max_time:
            new_time = self._max_time
            self.pause()
        
        # Update current time
        self.current_time = new_time
        self._last_update_time = current_real_time
        
        # Request data updates from plot manager if available
        if self._plot_manager is not None:
            self._update_plots()
    
    def _update_plots(self):
        """Update all plots with current time data."""
        if self._plot_manager is None:
            return
            
        # Calculate time window for data requests
        # This could be optimized based on plot requirements
        time_window = 1.0  # seconds
        start_time = max(self._min_time, self._current_time - time_window/2)
        end_time = min(self._max_time, self._current_time + time_window/2)
        
        # Notify plot manager to update plots
        # The actual data fetching will be handled by the plot manager and plugins
        for plot in getattr(self._plot_manager, 'plots', []):
            if hasattr(plot, 'update_time_range'):
                plot.update_time_range(start_time, end_time, self._current_time)
