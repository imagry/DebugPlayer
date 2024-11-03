import os
import sys

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.plot_manager import PlotManager
from unittest.mock import MagicMock

def test_register_plugin():
    plot_manager = PlotManager()
    mock_plugin = MagicMock()
    mock_plugin.signals = {"speed": {"func": lambda: 0, "type": "temporal"}}
    plot_manager.register_plugin("MockPlugin", mock_plugin)
    assert "MockPlugin" in plot_manager.plugins

def test_request_data():
    plot_manager = PlotManager()
    mock_plugin = MagicMock()
    mock_plugin.get_data_for_timestamp.return_value = {"value": 30}
    plot_manager.plugins["MockPlugin"] = mock_plugin
    plot_manager.signal_plugins["speed"] = {"plugin": "MockPlugin"}
    plot_manager.request_data(123456)
    mock_plugin.get_data_for_timestamp.assert_called_with("speed", 123456)
