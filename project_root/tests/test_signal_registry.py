#!/usr/bin/env python3

"""
Tests for the SignalRegistry class.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.signal_registry import SignalRegistry
from core.signal_validation import SignalValidationError

class TestSignalRegistry:
    """Test suite for the SignalRegistry class."""
    
    def test_init(self):
        """Test initialization of the SignalRegistry."""
        registry = SignalRegistry()
        assert registry.signals == {}
        assert registry.signal_providers == {}
        assert registry.signal_subscribers == {}
        
    def test_register_signal_valid(self):
        """Test registering a valid signal."""
        registry = SignalRegistry()
        
        # Create a mock signal
        signal_name = "test_signal"
        signal_func = lambda x: x
        signal_def = {
            "func": signal_func,
            "type": "temporal",
            "description": "A test signal"
        }
        plugin_name = "test_plugin"
        
        # Register the signal
        result = registry.register_signal(signal_name, signal_def, plugin_name)
        
        # Check that signal was registered
        assert signal_name in registry.signals
        assert registry.signal_providers[signal_name] == plugin_name
        assert signal_name in registry.signal_subscribers
        assert len(registry.signal_subscribers[signal_name]) == 0
        
        # Check the returned normalized signal
        assert result["plugin"] == plugin_name
        assert result["func"] == signal_func
        assert result["type"] == "temporal"
        assert result["description"] == "A test signal"
        
        # Check signal hierarchy
        assert plugin_name in registry.signal_hierarchy
        assert "temporal" in registry.signal_hierarchy[plugin_name]
        assert signal_name in registry.signal_hierarchy[plugin_name]["temporal"]
        
    def test_register_signal_invalid(self):
        """Test registering an invalid signal."""
        registry = SignalRegistry()
        
        # Create an invalid signal (missing func)
        signal_name = "invalid_signal"
        signal_def = {
            "type": "temporal",
            "description": "An invalid signal"
        }
        plugin_name = "test_plugin"
        
        # Registration should raise an exception
        with pytest.raises(SignalValidationError):
            registry.register_signal(signal_name, signal_def, plugin_name)
            
        # Signal should not be registered
        assert signal_name not in registry.signals
        assert signal_name not in registry.signal_providers
        assert signal_name not in registry.signal_subscribers
        
    def test_subscribe_to_signal(self):
        """Test subscribing to a signal."""
        registry = SignalRegistry()
        
        # Register a signal
        signal_name = "test_signal"
        signal_def = {
            "func": lambda x: x,
            "type": "temporal"
        }
        plugin_name = "test_plugin"
        registry.register_signal(signal_name, signal_def, plugin_name)
        
        # Create a mock subscriber
        subscriber = MagicMock()
        
        # Subscribe to the signal
        result = registry.subscribe_to_signal(signal_name, subscriber)
        assert result is True
        
        # Check that subscription was added
        assert subscriber in registry.signal_subscribers[signal_name]
        
        # Subscribing again should not add duplicates
        registry.subscribe_to_signal(signal_name, subscriber)
        assert len(registry.signal_subscribers[signal_name]) == 1
        
        # Subscribing to nonexistent signal should fail
        result = registry.subscribe_to_signal("nonexistent_signal", subscriber)
        assert result is False
        
    def test_unsubscribe_from_signal(self):
        """Test unsubscribing from a signal."""
        registry = SignalRegistry()
        
        # Register a signal
        signal_name = "test_signal"
        signal_def = {
            "func": lambda x: x,
            "type": "temporal"
        }
        plugin_name = "test_plugin"
        registry.register_signal(signal_name, signal_def, plugin_name)
        
        # Create and subscribe a mock subscriber
        subscriber = MagicMock()
        registry.subscribe_to_signal(signal_name, subscriber)
        
        # Unsubscribe
        result = registry.unsubscribe_from_signal(signal_name, subscriber)
        assert result is True
        
        # Check that subscription was removed
        assert subscriber not in registry.signal_subscribers[signal_name]
        
        # Unsubscribing again should return False
        result = registry.unsubscribe_from_signal(signal_name, subscriber)
        assert result is False
        
        # Unsubscribing from nonexistent signal should return False
        result = registry.unsubscribe_from_signal("nonexistent_signal", subscriber)
        assert result is False
        
    def test_get_signal_function(self):
        """Test getting signal function."""
        registry = SignalRegistry()
        
        # Register a signal
        signal_name = "test_signal"
        signal_func = lambda x: x
        signal_def = {
            "func": signal_func,
            "type": "temporal"
        }
        plugin_name = "test_plugin"
        registry.register_signal(signal_name, signal_def, plugin_name)
        
        # Get the function
        func = registry.get_signal_function(signal_name)
        assert func == signal_func
        
        # Getting nonexistent signal function should return None
        func = registry.get_signal_function("nonexistent_signal")
        assert func is None
        
    def test_get_signals_by_type(self):
        """Test getting signals by type."""
        registry = SignalRegistry()
        
        # Register signals of different types
        registry.register_signal("temporal_signal", {"func": lambda x: x, "type": "temporal"}, "test_plugin")
        registry.register_signal("spatial_signal", {"func": lambda x: x, "type": "spatial"}, "test_plugin")
        registry.register_signal("another_temporal", {"func": lambda x: x, "type": "temporal"}, "test_plugin")
        
        # Get signals by type
        temporal_signals = registry.get_signals_by_type("temporal")
        spatial_signals = registry.get_signals_by_type("spatial")
        unknown_signals = registry.get_signals_by_type("unknown")
        
        assert set(temporal_signals) == {"temporal_signal", "another_temporal"}
        assert set(spatial_signals) == {"spatial_signal"}
        assert unknown_signals == []
        
    def test_get_signals_by_plugin(self):
        """Test getting signals provided by a plugin."""
        registry = SignalRegistry()
        
        # Register signals from different plugins
        registry.register_signal("signal1", {"func": lambda x: x, "type": "temporal"}, "plugin1")
        registry.register_signal("signal2", {"func": lambda x: x, "type": "spatial"}, "plugin1")
        registry.register_signal("signal3", {"func": lambda x: x, "type": "temporal"}, "plugin2")
        
        # Get signals by plugin
        plugin1_signals = registry.get_signals_by_plugin("plugin1")
        plugin2_signals = registry.get_signals_by_plugin("plugin2")
        unknown_plugin_signals = registry.get_signals_by_plugin("unknown_plugin")
        
        assert set(plugin1_signals) == {"signal1", "signal2"}
        assert set(plugin2_signals) == {"signal3"}
        assert unknown_plugin_signals == []
        
    def test_get_signal_metadata(self):
        """Test getting signal metadata."""
        registry = SignalRegistry()
        
        # Register a signal with metadata
        signal_name = "test_signal"
        signal_func = lambda x: x
        signal_def = {
            "func": signal_func,
            "type": "temporal",
            "description": "A test signal",
            "units": "meters",
            "valid_range": [0, 100]
        }
        plugin_name = "test_plugin"
        registry.register_signal(signal_name, signal_def, plugin_name)
        
        # Get metadata
        metadata = registry.get_signal_metadata(signal_name)
        
        # Check that metadata was returned correctly
        assert "plugin" in metadata
        assert metadata["type"] == "temporal"
        assert metadata["description"] == "A test signal"
        assert metadata["units"] == "meters"
        assert metadata["valid_range"] == [0, 100]
        
        # Func should not be exposed in metadata
        assert "func" not in metadata
        
        # Getting metadata for nonexistent signal should return empty dict
        metadata = registry.get_signal_metadata("nonexistent_signal")
        assert metadata == {}
