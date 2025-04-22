# Set the base path
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

import pytest
from plugins.CarPosePlugin import CarPosePlugin
from tests.mock_data_generator import generate_complete_mock_trip

@pytest.fixture(scope="module")
def mock_trip_data(test_data_dir):
    """Generate mock trip data for tests in this module."""
    mock_trip_path = test_data_dir / "mock_car_pose_test"
    return generate_complete_mock_trip(mock_trip_path)

@pytest.fixture
def mock_car_pose_plugin(mock_trip_data):
    """Create a CarPosePlugin instance with mock data."""
    return CarPosePlugin(str(mock_trip_data))

def test_car_pose_signal_registration(mock_car_pose_plugin):
    """Test that the car pose plugin registers expected signals."""
    plugin = mock_car_pose_plugin
    
    # Check that expected signals are registered
    assert "car_pose" in plugin.signals
    assert "car_route" in plugin.signals
    
    # Check that has_signal method works correctly
    assert plugin.has_signal("car_pose")
    assert plugin.has_signal("car_route")
    assert not plugin.has_signal("nonexistent_signal")

def test_get_data_for_timestamp(mock_car_pose_plugin):
    """Test fetching data for specific timestamps."""
    plugin = mock_car_pose_plugin
    
    # Test with a timestamp that should exist in our mock data (100ms)
    result = plugin.get_data_for_timestamp("car_pose", 100)
    assert result is not None
    assert "x" in result
    assert "y" in result
    assert "theta" in result
    
    # Test with car_route signal
    route_result = plugin.get_data_for_timestamp("car_route", 100)
    assert route_result is not None
    assert "x" in route_result
    assert "y" in route_result
    
    # Test a nonexistent signal
    none_result = plugin.get_data_for_timestamp("nonexistent_signal", 100)
    assert none_result is None

def test_signal_types():
    """Test that signals have the correct type definitions."""
    with patch('plugins.CarPosePlugin.CarPose') as MockCarPose:
        instance = MockCarPose.return_value
        instance.timestamps = [0, 100, 200]
        
        plugin = CarPosePlugin("/mock/path")
        
        assert plugin.signals["car_pose"]["type"] == "spatial"
        assert plugin.signals["car_route"]["type"] == "spatial"

def test_out_of_range_timestamp(mock_car_pose_plugin):
    """Test behavior with timestamps outside the available range."""
    plugin = mock_car_pose_plugin
    
    # Very high timestamp (beyond our data)
    high_result = plugin.get_data_for_timestamp("car_pose", 999999)
    # Should return the last available data point
    assert high_result is not None
