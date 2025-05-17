"""
Integration tests for the playback flow in Debug Player.

These tests verify that the different components work together correctly
to provide a smooth playback experience.
"""

import time
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, call

# Import the components we'll be testing
from core.plot_manager import PlotManager
from core.timeline import TimelineController

class TestPlaybackFlow:
    """Test suite for the playback flow integration."""
    
    @pytest.fixture
    def mock_plugin(self):
        """Create a mock plugin that provides test signals."""
        class MockPlugin:
            def __init__(self):
                self.signals = {
                    "test_signal": {
                        "type": "temporal",
                        "description": "Test signal",
                        "unit": "m/s"
                    },
                    "position_x": {
                        "type": "spatial",
                        "description": "X position",
                        "unit": "m"
                    }
                }
                
            def get_data(self, signal_name, start_time, end_time):
                """Generate test data for the given time range."""
                timestamps = np.linspace(start_time, end_time, 10)
                if signal_name == "test_signal":
                    values = np.sin(timestamps)
                else:  # position_x
                    values = timestamps * 0.5  # Linear position
                return timestamps, values
        
        return MockPlugin()
    
    @pytest.fixture
    def playback_setup(self, mock_plugin, qtbot):
        """Set up a complete playback environment for testing."""
        # Create plot manager with mocked plots to avoid Qt initialization issues
        plot_manager = PlotManager()
        
        # Create timeline controller
        timeline = TimelineController(plot_manager=plot_manager, update_interval=10)
        
        # Register the mock plugin
        plot_manager.register_plugin("test_plugin", mock_plugin)
        
        # Create mock plots - use MagicMock for all plot interactions
        temporal_plot = MagicMock()
        spatial_plot = MagicMock()
        
        # Configure the plots to be returned by the plot manager
        plot_manager.plots = [temporal_plot, spatial_plot]
        
        # Mock the plot widgets to avoid Qt initialization
        with patch('gui.custom_plot_widget.TemporalPlotWidget_pg') as mock_temporal_widget, \
             patch('gui.custom_plot_widget.SpatialPlotWidget') as mock_spatial_widget:
            # Configure the mocks to return our mock plots
            mock_temporal_widget.return_value = temporal_plot
            mock_spatial_widget.return_value = spatial_plot
            
            # Set up time range
            timeline.update_time_range(0.0, 10.0)
            
            # No need to add mock widgets to qtbot
            yield {
                'plot_manager': plot_manager,
                'timeline': timeline,
                'temporal_plot': temporal_plot,
                'spatial_plot': spatial_plot,
                'plugin': mock_plugin
            }
    
    def test_initial_playback_state(self, playback_setup):
        """Test that the initial playback state is correct."""
        timeline = playback_setup['timeline']
        
        # Check initial state
        assert timeline.current_time == 0.0
        assert timeline.min_time == 0.0
        assert timeline.max_time == 10.0
        assert not timeline.is_playing
    
    def test_playback_controls(self, playback_setup, qtbot):
        """Test basic playback controls (play, pause, seek)."""
        timeline = playback_setup['timeline']
        
        # Start playback
        timeline.play()
        assert timeline.is_playing
        
        # Process events to ensure the timer starts
        qtbot.wait(100)  # Wait for 100ms
        
        # Pause and check time has advanced
        timeline.pause()
        assert not timeline.is_playing
        assert timeline.current_time > 0.0, "Time should advance during playback"
        
        # Record current time and resume
        current_time = timeline.current_time
        timeline.play()
        
        # Process events to let the timer run
        qtbot.wait(100)  # Wait for another 100ms
        
        timeline.pause()
        assert timeline.current_time > current_time, "Time should continue advancing after resuming"
        
        # Test seeking
        seek_time = 5.0
        timeline.seek(seek_time)
        assert timeline.current_time == seek_time, f"Seek to {seek_time} failed"
        
        # Test step functions
        step_size = 1.0
        timeline.step_forward(step_size)
        expected_time = seek_time + step_size
        assert abs(timeline.current_time - expected_time) < 0.001, \
            f"Step forward by {step_size} from {seek_time} failed"
        
        step_back = 2.0
        timeline.step_backward(step_back)
        expected_time = expected_time - step_back
        assert abs(timeline.current_time - expected_time) < 0.001, \
            f"Step backward by {step_back} failed"
    
    def test_plot_updates_during_playback(self, playback_setup, qtbot):
        """Test that plots are updated during playback."""
        timeline = playback_setup['timeline']
        temporal_plot = playback_setup['temporal_plot']
        spatial_plot = playback_setup['spatial_plot']
        
        # Reset mock call counts
        temporal_plot.update_time_range.reset_mock()
        spatial_plot.update_time_range.reset_mock()
        
        # Start playback and process events
        timeline.play()
        qtbot.wait(200)  # Wait for 200ms
        
        # Pause and process any remaining events
        timeline.pause()
        qtbot.wait(100)  # Ensure all events are processed
        
        # Verify plot updates were called
        assert temporal_plot.update_time_range.called, \
            "Temporal plot should be updated during playback"
        assert spatial_plot.update_time_range.called, \
            "Spatial plot should be updated during playback"
            
        # Verify plot manager is properly set up
        assert timeline._plot_manager is not None, \
            "Plot manager should be available"
        
        # Get the last call to update_time_range
        temporal_calls = temporal_plot.update_time_range.call_args_list
        spatial_calls = spatial_plot.update_time_range.call_args_list
        
        # Check that we have at least one update
        assert len(temporal_calls) > 0
        assert len(spatial_calls) > 0
        
        # Check the arguments of the last call
        last_temporal_args = temporal_calls[-1][0]
        last_spatial_args = spatial_calls[-1][0]
        
        # Check that the time range is valid
        start_time, end_time, current_time = last_temporal_args
        assert start_time <= current_time <= end_time
        assert end_time - start_time > 0  # Positive time window
        
        # Check that spatial plot got the same current time
        assert last_spatial_args[2] == current_time
    
    def test_playback_completion(self, playback_setup, qtbot):
        """Test that playback stops when reaching the end."""
        timeline = playback_setup['timeline']
        
        # Start near the end
        seek_position = timeline.max_time - 0.5  # 0.5 seconds before end
        timeline.seek(seek_position)
        timeline.play()
        
        # Wait for playback to complete (should take about 0.5 seconds at 1x speed)
        # Use qtbot.waitUntil to wait for the playback to stop
        def playback_finished():
            return not timeline.is_playing
            
        # Wait up to 2 seconds for playback to complete
        qtbot.waitUntil(playback_finished, timeout=2000)
        
        # Verify playback stopped at the end
        assert not timeline.is_playing, "Playback should have stopped at the end"
        assert abs(timeline.current_time - timeline.max_time) < 0.01, \
            f"Playback should stop at max time ({timeline.max_time}), got {timeline.current_time}"
    
    def test_playback_speed(self, playback_setup, qtbot):
        """Test that playback speed affects the rate of time progression."""
        timeline = playback_setup['timeline']
        
        def test_speed(speed_multiplier, test_duration):
            """Helper function to test a specific playback speed."""
            expected_progress = speed_multiplier * test_duration
            
            timeline.playback_speed = speed_multiplier
            timeline.seek(0.0)
            timeline.play()
            
            # Wait for the specified duration while processing events
            qtbot.wait(int(test_duration * 1000))  # Convert to milliseconds
            
            # Pause and check progress
            timeline.pause()
            
            # Calculate the expected range (allowing ±10% variance)
            min_expected = expected_progress * 0.9
            max_expected = expected_progress * 1.1
            actual_progress = timeline.current_time
            
            assert min_expected <= actual_progress <= max_expected, \
                f"At {speed_multiplier}x speed, expected {min_expected}-{max_expected}s progress, got {actual_progress}s"
        
        # Test at 2x speed
        test_speed(2.0, 0.5)  # Should advance ~1.0s in 0.5s real time
        
        # Test at 0.5x speed
        test_speed(0.5, 1.0)  # Should advance ~0.5s in 1.0s real time
