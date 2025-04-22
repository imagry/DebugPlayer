#!/usr/bin/env python3

"""
Test the PluginBase abstract class implementation.

These tests verify that plugins correctly implement the required interface.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interfaces.PluginBase import PluginBase


class TestPluginBase:
    """
    Test cases for the PluginBase abstract class.
    
    These tests verify that plugins must implement the required methods.
    """
    
    def test_abstract_methods(self):
        """
        Test that PluginBase cannot be instantiated directly
        since it has abstract methods.
        """
        # Attempt to instantiate PluginBase directly should fail
        with pytest.raises(TypeError):
            PluginBase("/path/to/test")
    
    def test_plugin_inheritance(self):
        """
        Test that a concrete plugin class must implement all required methods.
        """
        # Create a class that inherits from PluginBase but doesn't implement all methods
        class IncompletePlugin(PluginBase):
            def __init__(self, file_path):
                super().__init__(file_path)
                
            # Missing has_signal and get_data_for_timestamp implementations
        
        # Attempt to instantiate the incomplete plugin should fail
        with pytest.raises(TypeError):
            IncompletePlugin("/path/to/test")
            
    def test_complete_plugin_implementation(self):
        """
        Test that a complete plugin implementation can be instantiated.
        """
        # Create a class that implements all required methods
        class CompletePlugin(PluginBase):
            def __init__(self, file_path):
                self.file_path = file_path
                self.signals = {}
                
            def has_signal(self, signal):
                return signal in self.signals
                
            def get_data_for_timestamp(self, signal, timestamp):
                if signal in self.signals:
                    return {"value": 42}
                return None
        
        # This should work without errors
        plugin = CompletePlugin("/path/to/test")
        assert plugin.file_path == "/path/to/test"
        assert plugin.has_signal("test_signal") is False
        
        # Add a signal and test again
        plugin.signals["test_signal"] = {"func": lambda: None}
        assert plugin.has_signal("test_signal") is True
        
        # Test data retrieval
        data = plugin.get_data_for_timestamp("test_signal", 0)
        assert data == {"value": 42}


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
