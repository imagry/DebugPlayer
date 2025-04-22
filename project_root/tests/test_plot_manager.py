#!/usr/bin/env python3

"""
Test suite for the PlotManager class.

These tests verify that the PlotManager correctly manages plugins, signals, and plots.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add project root to Python path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

# Create QApplication instance for testing Qt widgets
import PySide6
from PySide6.QtWidgets import QApplication

# Create a QApplication instance
app = QApplication.instance()
if not app:
    app = QApplication([])

from core.plot_manager import PlotManager
from interfaces.PluginBase import PluginBase


@pytest.fixture
def mock_plugin():
    """
    Create a mock plugin with predefined signals for testing.
    """
    plugin = MagicMock(spec=PluginBase)
    plugin.has_signal.return_value = True
    plugin.signals = {
        "speed": {"func": lambda: 0, "type": "temporal"},
        "position": {"func": lambda: {"x": 0, "y": 0}, "type": "spatial"},
        "timestamps": {"func": lambda: [0, 1, 2, 3], "type": "temporal"}
    }
    return plugin


@pytest.fixture
def plot_manager():
    """
    Create a PlotManager instance for testing with mocked widgets.
    """
    # Patch the Qt widget classes to avoid creating real UI components
    with patch('core.plot_manager.TemporalPlotWidget_pg') as mock_temporal, \
         patch('core.plot_manager.SpatialPlotWidget') as mock_spatial:
        
        # Configure the mocks
        mock_temporal.return_value = MagicMock()
        mock_spatial.return_value = MagicMock()
        
        # Create the PlotManager instance with mocked components
        manager = PlotManager()
        
        return manager


@pytest.fixture
def plot_manager_with_plugin(plot_manager, mock_plugin):
    """
    Create a PlotManager with a mock plugin already registered.
    """
    # Ensure the mock plugin is properly configured to handle has_signal calls
    def has_signal_side_effect(signal):
        return signal in mock_plugin.signals
    
    mock_plugin.has_signal.side_effect = has_signal_side_effect
    
    # Register the plugin with PlotManager
    plot_manager.register_plugin("MockPlugin", mock_plugin)
    
    return plot_manager, mock_plugin


class TestPlotManager:
    """
    Test suite for the PlotManager class.
    """
    
    def test_initialization(self, plot_manager):
        """
        Test the PlotManager initializes with correct default values.
        """
        assert hasattr(plot_manager, "plots")
        assert hasattr(plot_manager, "signals")
        assert hasattr(plot_manager, "plugins")
        assert hasattr(plot_manager, "signal_plugins")
        
        # Verify initial empty state
        assert len(plot_manager.plots) == 0
        assert len(plot_manager.signals) == 0
        assert len(plot_manager.plugins) == 0
        assert len(plot_manager.signal_plugins) == 0
    
    def test_register_plugin(self, plot_manager, mock_plugin):
        """
        Test that a plugin can be registered with the PlotManager.
        """
        # Register plugin
        plot_manager.register_plugin("MockPlugin", mock_plugin)
        
        # Verify the plugin was added
        assert "MockPlugin" in plot_manager.plugins
        assert plot_manager.plugins["MockPlugin"] == mock_plugin
        
        # Verify signals were registered
        for signal in mock_plugin.signals:
            assert signal in plot_manager.signal_plugins
            assert plot_manager.signal_plugins[signal]["plugin"] == "MockPlugin"
    
    def test_register_plugin_with_invalid_signal_type(self, plot_manager):
        """
        Test handling of plugins with invalid signal types.
        """
        # Create a plugin with an invalid signal type
        plugin = MagicMock(spec=PluginBase)
        plugin.signals = {
            "invalid_signal": {"func": lambda: 0, "type": "invalid_type"}
        }
        
        # Register the plugin (should handle the error gracefully)
        plot_manager.register_plugin("InvalidPlugin", plugin)
        
        # Check that the signal is registered with a default type
        assert "invalid_signal" in plot_manager.signal_plugins
        assert plot_manager.signal_plugins["invalid_signal"]["type"] == "temporal"
    
    def test_request_data_direct(self, plot_manager):
        """
        Simplified test for request_data that directly sets up the minimal required state.
        """
        # Create a mock plugin with minimum required functionality
        mock_plugin = MagicMock()
        mock_plugin.has_signal.return_value = True
        mock_plugin.get_data_for_timestamp.return_value = {"value": 42}
        
        # Register it in the PlotManager manually
        plot_manager.plugins["TestPlugin"] = mock_plugin
        
        # Register a test signal pointing to this plugin (signal_plugins)
        plot_manager.signal_plugins["test_signal"] = {
            "plugin": "TestPlugin",
            "type": "temporal"
        }
        
        # CRITICAL: We also need to add the signal to self.signals dictionary
        # The request_data method iterates over self.signals.items()
        mock_plot = MagicMock()
        plot_manager.signals["test_signal"] = [mock_plot]
        
        # Request data for a timestamp
        plot_manager.request_data(12345)
        
        # Verify that has_signal was called correctly
        mock_plugin.has_signal.assert_called_with("test_signal")
        
        # Verify that get_data_for_timestamp was called correctly for our signal
        mock_plugin.get_data_for_timestamp.assert_called_with("test_signal", 12345)
    
    def test_request_data(self, plot_manager_with_plugin):
        """
        Test requesting data for a specific timestamp using the fixture.
        """
        plot_manager, mock_plugin = plot_manager_with_plugin
        
        # Verify signals were registered correctly
        assert "speed" in plot_manager.signal_plugins
        assert "position" in plot_manager.signal_plugins
        assert "timestamps" in plot_manager.signal_plugins
        
        # Ensure the signals are linked to our plugin
        for signal in ["speed", "position", "timestamps"]:
            assert plot_manager.signal_plugins[signal]["plugin"] == "MockPlugin"
            
        # Set up the mock plugin to return test data for each timestamp
        test_data = {"value": 30}
        mock_plugin.get_data_for_timestamp.return_value = test_data

        # We need to ensure the mock has the right behavior
        # This is critical for the test to work properly
        mock_plugin.has_signal.return_value = True  # Ensure this returns True for any signal
        
        # CRITICAL: Make sure signals are in the signals dictionary
        # The PlotManager's signals dictionary must have entries for our test to work
        # Normally register_plugin doesn't add entries to the signals dictionary
        mock_plot = MagicMock()
        for signal in ["speed", "position", "timestamps"]:
            if signal not in plot_manager.signals:
                plot_manager.signals[signal] = [mock_plot]
        
        # Request data at a specific timestamp
        timestamp = 123456
        plot_manager.request_data(timestamp)
        
        # Now the methods should be called
        assert mock_plugin.has_signal.call_count > 0, "has_signal was never called"
        assert mock_plugin.get_data_for_timestamp.call_count > 0, "get_data_for_timestamp was never called"
    
    def test_request_data_for_nonexistent_signal(self, plot_manager):
        """
        Test requesting data for a signal that doesn't exist.
        """
        # This should not raise an exception
        plot_manager.request_data(123456)
        
        # Add signal without a plugin
        plot_manager.signal_plugins["nonexistent_signal"] = {"plugin": "NonexistentPlugin"}
        
        # This should handle the missing plugin gracefully
        plot_manager.request_data(123456)
    
    def test_load_plugin_from_file(self, plot_manager):
        """
        Test loading a plugin from a file.
        
        This uses patching to avoid actual file I/O.
        """
        # Mock importlib.util.spec_from_file_location and importlib.util.module_from_spec
        with patch('importlib.util.spec_from_file_location') as mock_spec, \
             patch('importlib.util.module_from_spec') as mock_module:
            
            # Set up the mocks
            mock_module_obj = MagicMock()
            mock_module.return_value = mock_module_obj
            
            # Create a mock plugin class with the minimum implementation
            mock_plugin_class = MagicMock(return_value=MagicMock(spec=PluginBase))
            mock_plugin_class.return_value.signals = {"test_signal": {"func": lambda: 0, "type": "temporal"}}
            
            # Set the plugin_class attribute on the mock module
            mock_module_obj.plugin_class = mock_plugin_class
            
            # Call the method
            plot_manager.load_plugin_from_file(
                "test_plugin", 
                "/path/to/test_plugin.py", 
                {"file_path": "/test/data/path"}
            )
            
            # Verify plugin was instantiated with the provided arguments
            mock_plugin_class.assert_called_once_with(file_path="/test/data/path")
            
            # Verify plugin was registered
            assert "test_plugin" in plot_manager.plugins


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
