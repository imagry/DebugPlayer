#!/usr/bin/env python3

"""
Test suite for the CarPosePlugin.

These tests verify that the CarPosePlugin correctly implements the PluginBase interface
and provides the expected signals and data.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

# Add project root to Python path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from plugins.CarPosePlugin import CarPosePlugin
from interfaces.PluginBase import PluginBase
from core.plot_manager import PlotManager


@pytest.fixture
def mock_car_pose():
    """
    Mock the CarPose class to avoid file I/O during testing.
    """
    with patch('plugins.CarPosePlugin.CarPose') as mock_car_pose_class:
        # Configure the mock CarPose instance
        mock_instance = MagicMock()
        mock_car_pose_class.return_value = mock_instance
        
        # Set up route data
        mock_instance.route = {
            'cp_x': np.array([1.0, 2.0, 3.0]),
            'cp_y': np.array([4.0, 5.0, 6.0])
        }
        mock_instance.df_car_pose = {
            'cp_yaw_deg': np.array([10.0, 20.0, 30.0])
        }
        
        # Set up timestamp data
        mock_instance.get_timestamps_milliseconds.return_value = np.array([100, 200, 300])
        
        # Set up route handler
        mock_instance.get_route.return_value = np.array([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
        
        # Set up car pose retrieval
        mock_instance.get_car_pose_at_timestamp.return_value = (2.0, 5.0, 20.0)
        
        yield mock_instance


@pytest.fixture
def car_pose_plugin(mock_car_pose):
    """
    Create a CarPosePlugin instance for testing.
    """
    return CarPosePlugin("/path/to/test/data")


class TestCarPosePlugin:
    """
    Test suite for the CarPosePlugin class.
    """
    
    def test_inheritance(self):
        """
        Test that CarPosePlugin inherits from PluginBase.
        """
        assert issubclass(CarPosePlugin, PluginBase)
    
    def test_initialization(self, car_pose_plugin, mock_car_pose):
        """
        Test that the plugin initializes correctly and sets up the required signals.
        """
        # Test that the plugin has the expected signals
        assert "car_pose(t)" in car_pose_plugin.signals
        assert "route" in car_pose_plugin.signals
        assert "timestamps" in car_pose_plugin.signals
        assert "car_poses" in car_pose_plugin.signals
        
        # Test that the signals have the correct type
        assert car_pose_plugin.signals["car_pose(t)"]["type"] == "spatial"
        assert car_pose_plugin.signals["route"]["type"] == "spatial"
        assert car_pose_plugin.signals["timestamps"]["type"] == "temporal"
        assert car_pose_plugin.signals["car_poses"]["type"] == "spatial"
        
        # Test that signal functions are callable
        assert callable(car_pose_plugin.signals["car_pose(t)"]["func"])
        assert callable(car_pose_plugin.signals["route"]["func"])
        assert callable(car_pose_plugin.signals["timestamps"]["func"])
        assert callable(car_pose_plugin.signals["car_poses"]["func"])
    
    def test_has_signal(self, car_pose_plugin):
        """
        Test the has_signal method.
        """
        assert car_pose_plugin.has_signal("car_pose(t)") is True
        assert car_pose_plugin.has_signal("route") is True
        assert car_pose_plugin.has_signal("nonexistent_signal") is False
    
    def test_get_data_for_timestamp(self, car_pose_plugin, mock_car_pose):
        """
        Test that get_data_for_timestamp returns correct data for different signals.
        """
        # Test car_pose(t) signal
        car_pose_data = car_pose_plugin.get_data_for_timestamp("car_pose(t)", 200)
        assert car_pose_data == {"x": 2.0, "y": 5.0, "theta": 20.0}
        mock_car_pose.get_car_pose_at_timestamp.assert_called_with(200)
        
        # Test route signal
        route_data = car_pose_plugin.get_data_for_timestamp("route", 0)  # Timestamp doesn't matter for route
        assert "x" in route_data
        assert "y" in route_data
        mock_car_pose.get_route.assert_called_once()
        
        # Test timestamps signal
        timestamps_data = car_pose_plugin.get_data_for_timestamp("timestamps", 0)  # Timestamp doesn't matter
        assert np.array_equal(timestamps_data, np.array([100, 200, 300]))
        
        # Test nonexistent signal
        assert car_pose_plugin.get_data_for_timestamp("nonexistent_signal", 200) is None
    
    def test_integration_with_plot_manager(self, car_pose_plugin):
        """
        Test that the plugin can be registered with PlotManager.
        """
        # Create a PlotManager and register the plugin
        with patch('core.plot_manager.TemporalPlotWidget_pg'), \
             patch('core.plot_manager.SpatialPlotWidget'):
            
            plot_manager = PlotManager()
            plot_manager.register_plugin("CarPosePlugin", car_pose_plugin)
            
            # Test that the plugin was registered correctly
            assert "CarPosePlugin" in plot_manager.plugins
            assert plot_manager.plugins["CarPosePlugin"] == car_pose_plugin
            
            # Test that the signals were registered
            for signal in car_pose_plugin.signals:
                assert signal in plot_manager.signal_plugins
                assert plot_manager.signal_plugins[signal]["plugin"] == "CarPosePlugin"


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
