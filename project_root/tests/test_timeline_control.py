"""
Tests for the timeline control functionality.

These tests verify that the TimelineController correctly manages playback state,
time ranges, and coordinates with the plot manager.
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QCoreApplication, QTimer

# Import the timeline controller
from core.timeline import TimelineController

# Create a QApplication instance for testing
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for testing."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app

class TestTimelineControl:
    """Test suite for the TimelineController class."""
    
    @pytest.fixture
    def mock_plot_manager(self):
        """Create a mock PlotManager with basic functionality."""
        pm = MagicMock()
        pm.signals = {}
        pm.plots = []
        pm.plugins = {}
        pm.signal_plugins = {}
        return pm
    
    @pytest.fixture
    def timeline(self, mock_plot_manager):
        """Create a TimelineController instance for testing."""
        return TimelineController(plot_manager=mock_plot_manager, update_interval=10)
    
    def test_initial_state(self, timeline):
        """Test that timeline initializes with default values."""
        assert timeline.current_time == 0.0
        assert timeline.min_time == 0.0
        assert timeline.max_time == 1.0  # Default max time
        assert timeline.playback_speed == 1.0
        assert not timeline.is_playing
    
    def test_time_range_updates(self, timeline):
        """Test updating the time range."""
        # Test initial range
        timeline.update_time_range(0.0, 10.0)
        assert timeline.min_time == 0.0
        assert timeline.max_time == 10.0
        
        # Test expanding range
        timeline.update_time_range(-5.0, 15.0)
        assert timeline.min_time == -5.0
        assert timeline.max_time == 15.0
        
        # Test invalid range
        with pytest.raises(ValueError):
            timeline.update_time_range(10.0, 5.0)
    
    def test_seek(self, timeline):
        """Test seeking to a specific time."""
        timeline.update_time_range(0.0, 10.0)
        
        # Seek within range
        timeline.seek(5.0)
        assert timeline.current_time == 5.0
        
        # Seek below min time (should clamp to min)
        timeline.seek(-5.0)
        assert timeline.current_time == 0.0
        
        # Seek above max time (should clamp to max)
        timeline.seek(15.0)
        assert timeline.current_time == 10.0
    
    def test_play_pause(self, timeline, qapp):
        """Test play/pause functionality."""
        timeline.update_time_range(0.0, 10.0)
        
        # Start playback and process events to let timer start
        timeline.play()
        assert timeline.is_playing
        
        # Process events to ensure the timer is running
        qapp.processEvents()
        
        # Let it run for a short time
        time.sleep(0.1)
        
        # Process events again to allow timer to trigger
        qapp.processEvents()
        
        # Pause and check time has advanced
        timeline.pause()
        assert not timeline.is_playing
        
        # The time should have advanced (use a small delta to account for timing variations)
        assert timeline.current_time > 0.0, f"Expected time > 0.0, got {timeline.current_time}"
        
        # Record current time and resume
        current_time = timeline.current_time
        timeline.play()
        
        # Process events and wait
        qapp.processEvents()
        time.sleep(0.1)
        qapp.processEvents()
        
        timeline.pause()
        assert timeline.current_time > current_time, \
            f"Expected time > {current_time}, got {timeline.current_time}"
    
    def test_playback_speed(self, timeline):
        """Test changing playback speed."""
        # Test valid speed changes
        timeline.playback_speed = 2.0
        assert timeline.playback_speed == 2.0
        
        # Test invalid speed
        with pytest.raises(ValueError):
            timeline.playback_speed = 0.0
        
        with pytest.raises(ValueError):
            timeline.playback_speed = -1.0
    
    def test_step_functions(self, timeline):
        """Test step forward/backward functionality."""
        timeline.update_time_range(0.0, 10.0)
        timeline.seek(5.0)
        
        # Step forward
        timeline.step_forward(1.0)
        assert timeline.current_time == 6.0
        
        # Step backward
        timeline.step_backward(2.0)
        assert timeline.current_time == 4.0
        
        # Test clamping at boundaries
        timeline.seek(9.5)
        timeline.step_forward(1.0)  # Should clamp to 10.0
        assert timeline.current_time == 10.0
        
        timeline.seek(0.5)
        timeline.step_backward(1.0)  # Should clamp to 0.0
        assert timeline.current_time == 0.0
    
    def test_plot_updates(self, timeline, mock_plot_manager):
        """Test that plot updates are requested correctly."""
        # Create a mock plot with update_time_range method
        mock_plot = MagicMock()
        mock_plot.update_time_range = MagicMock()
        mock_plot_manager.plots = [mock_plot]
        
        # Set up the plot manager to return our mock plot
        mock_plot_manager.plots = [mock_plot]
        
        # Update time range
        timeline.update_time_range(0.0, 10.0)
        
        # Manually trigger a plot update
        timeline._update_plots()
        
        # Check that update_time_range was called
        mock_plot.update_time_range.assert_called()
        
        # Get the call arguments
        args, _ = mock_plot.update_time_range.call_args
        start_time, end_time, current_time = args
        
        # Verify the time range is valid
        assert start_time <= current_time <= end_time
        assert end_time > start_time  # Should have a positive time window
        assert current_time == timeline.current_time
    
    def test_playback_completion(self, timeline, qapp):
        """Test that playback stops when reaching the end."""
        timeline.update_time_range(0.0, 1.0)
        timeline.seek(0.9)  # Start near the end
        
        # Start playback
        timeline.play()
        
        # Process events until playback should be done
        start_time = time.time()
        while timeline.is_playing and (time.time() - start_time) < 2.0:  # 2 second timeout
            qapp.processEvents()
            time.sleep(0.01)
        
        # Should have stopped at max time
        assert not timeline.is_playing
        assert timeline.current_time == 1.0
