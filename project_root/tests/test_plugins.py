# Set the base path
import sys
import os

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

import pytest
from plugins.CarPosePlugin import CarPosePlugin


def test_car_pose_signal_registration():
    plugin = CarPosePlugin("/path/to/test/data")
    assert "car_pose(t)" in plugin.signals
    assert "route" in plugin.signals

def test_get_data_for_timestamp():
    plugin = CarPosePlugin("/path/to/test/data")
    data = plugin.get_data_for_timestamp("car_pose(t)", timestamp=123456)
    assert data is not None
    assert isinstance(data, dict)
