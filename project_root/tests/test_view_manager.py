#!/usr/bin/env python3

"""
Tests for the ViewManager class.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.view_manager import ViewManager, ViewBase
from PySide6.QtWidgets import QWidget

class MockView(ViewBase):
    """Mock view implementation for testing."""
    
    def __init__(self, view_id, parent=None):
        super().__init__(view_id, parent)
        self.supported_signal_types = {"test"}
        self.widget = MagicMock(spec=QWidget)
        self.updated_signals = {}
        
    def update_data(self, signal_name, data):
        self.updated_signals[signal_name] = data
        return True
        
    def get_widget(self):
        return self.widget


class AnotherMockView(ViewBase):
    """Another mock view for testing."""
    
    def __init__(self, view_id, parent=None):
        super().__init__(view_id, parent)
        self.supported_signal_types = {"another"}
        self.widget = MagicMock(spec=QWidget)
        self.updated_signals = {}
        
    def update_data(self, signal_name, data):
        self.updated_signals[signal_name] = data
        return True
        
    def get_widget(self):
        return self.widget


class TestViewManager:
    """Test suite for the ViewManager."""
    
    @pytest.fixture
    def view_manager(self):
        """Create a ViewManager for testing."""
        manager = ViewManager()
        manager.register_view_class("mock", MockView)
        manager.register_view_class("another", AnotherMockView)
        return manager
    
    def test_register_view_class(self, view_manager):
        """Test registering a view class."""
        # Classes should already be registered by the fixture
        assert "mock" in view_manager.view_classes
        assert "another" in view_manager.view_classes
        assert view_manager.view_classes["mock"] is MockView
        assert view_manager.view_classes["another"] is AnotherMockView
    
    def test_create_view(self, view_manager):
        """Test creating a view instance."""
        view = view_manager.create_view("test_view", "mock")
        assert view is not None
        assert isinstance(view, MockView)
        assert view.view_id == "test_view"
        assert "test_view" in view_manager.views
        assert view_manager.views["test_view"] is view
        
        # Test with configuration
        config = {"key": "value"}
        view2 = view_manager.create_view("test_view2", "mock", config)
        assert view2 is not None
        assert "test_view2" in view_manager.views
        assert "test_view2" in view_manager.view_configs
        assert view_manager.view_configs["test_view2"] == config
        
        # Test with invalid view type
        with pytest.raises(ValueError):
            view_manager.create_view("invalid_view", "invalid_type")
            
        # Test with duplicate view ID
        with pytest.raises(ValueError):
            view_manager.create_view("test_view", "mock")
    
    def test_get_view(self, view_manager):
        """Test getting a view by ID."""
        view = view_manager.create_view("get_test", "mock")
        retrieved = view_manager.get_view("get_test")
        assert retrieved is view
        
        # Non-existent view should return None
        assert view_manager.get_view("nonexistent") is None
    
    def test_remove_view(self, view_manager):
        """Test removing a view."""
        # Create a view and connect signals
        view = view_manager.create_view("remove_test", "mock")
        view_manager.connect_signal_to_view("test_signal", "remove_test")
        
        # Remove the view
        result = view_manager.remove_view("remove_test")
        assert result is True
        assert "remove_test" not in view_manager.views
        assert "test_signal" not in view_manager.signal_views
        
        # Removing non-existent view should return False
        assert view_manager.remove_view("nonexistent") is False
    
    def test_connect_signal_to_view(self, view_manager):
        """Test connecting a signal to a view."""
        view_manager.create_view("connection_test", "mock")
        result = view_manager.connect_signal_to_view("test_signal", "connection_test")
        assert result is True
        assert "test_signal" in view_manager.signal_views
        assert "connection_test" in view_manager.signal_views["test_signal"]
        
        # Connecting to non-existent view should return False
        assert view_manager.connect_signal_to_view("test_signal", "nonexistent") is False
    
    def test_disconnect_signal_from_view(self, view_manager):
        """Test disconnecting a signal from a view."""
        view_manager.create_view("disconnect_test", "mock")
        view_manager.connect_signal_to_view("test_signal", "disconnect_test")
        
        # Disconnect the signal
        result = view_manager.disconnect_signal_from_view("test_signal", "disconnect_test")
        assert result is True
        assert "test_signal" not in view_manager.signal_views
        
        # Disconnecting non-existent signal should return False
        assert view_manager.disconnect_signal_from_view("nonexistent", "disconnect_test") is False
        
        # Disconnecting from non-existent view should return False
        view_manager.connect_signal_to_view("another_signal", "disconnect_test")
        assert view_manager.disconnect_signal_from_view("another_signal", "nonexistent") is False
    
    def test_update_signal_data(self, view_manager):
        """Test updating signal data in connected views."""
        # Create two views
        view1 = view_manager.create_view("update_test1", "mock")
        view2 = view_manager.create_view("update_test2", "mock")
        
        # Connect both views to the same signal
        view_manager.connect_signal_to_view("shared_signal", "update_test1")
        view_manager.connect_signal_to_view("shared_signal", "update_test2")
        
        # Connect only one view to another signal
        view_manager.connect_signal_to_view("unique_signal", "update_test1")
        
        # Update the shared signal
        test_data = {"value": 42}
        updated_count = view_manager.update_signal_data("shared_signal", test_data)
        assert updated_count == 2
        assert view1.updated_signals["shared_signal"] == test_data
        assert view2.updated_signals["shared_signal"] == test_data
        
        # Update the unique signal
        unique_data = {"value": "unique"}
        updated_count = view_manager.update_signal_data("unique_signal", unique_data)
        assert updated_count == 1
        assert view1.updated_signals["unique_signal"] == unique_data
        assert "unique_signal" not in view2.updated_signals
        
        # Update non-existent signal should return 0
        assert view_manager.update_signal_data("nonexistent", {}) == 0
    
    def test_get_views_for_signal(self, view_manager):
        """Test getting all views for a signal."""
        view1 = view_manager.create_view("views_test1", "mock")
        view2 = view_manager.create_view("views_test2", "mock")
        
        view_manager.connect_signal_to_view("shared_signal", "views_test1")
        view_manager.connect_signal_to_view("shared_signal", "views_test2")
        
        views = view_manager.get_views_for_signal("shared_signal")
        assert len(views) == 2
        assert view1 in views
        assert view2 in views
        
        # Non-existent signal should return empty list
        assert view_manager.get_views_for_signal("nonexistent") == []
    
    def test_register_template(self, view_manager):
        """Test registering a view template."""
        template_config = {
            "type": "mock",
            "config": {"key": "value"},
            "signals": ["test_signal"]
        }
        view_manager.register_template("test_template", template_config)
        assert "test_template" in view_manager.templates
        assert view_manager.templates["test_template"] == template_config
    
    def test_create_view_from_template(self, view_manager):
        """Test creating a view from a template."""
        # Register a template
        template_config = {
            "type": "mock",
            "config": {"key": "value"},
            "signals": ["test_signal"]
        }
        view_manager.register_template("test_template", template_config)
        
        # Create a view from the template
        view = view_manager.create_view_from_template("template_view", "test_template")
        assert view is not None
        assert isinstance(view, MockView)
        assert view.view_id == "template_view"
        assert "template_view" in view_manager.views
        assert "template_view" in view_manager.view_configs
        assert view_manager.view_configs["template_view"] == {"key": "value"}
        
        # The signal should be connected
        assert "test_signal" in view_manager.signal_views
        assert "template_view" in view_manager.signal_views["test_signal"]
        
        # Test with non-existent template
        assert view_manager.create_view_from_template("invalid", "nonexistent") is None
        
        # Test with invalid template (missing type)
        view_manager.register_template("invalid_template", {"config": {}})
        assert view_manager.create_view_from_template("invalid", "invalid_template") is None
    
    def test_save_and_load_layout(self, view_manager):
        """Test saving and loading a layout configuration."""
        # Create some views and connections
        view1 = view_manager.create_view("layout_test1", "mock", {"key1": "value1"})
        view2 = view_manager.create_view("layout_test2", "another", {"key2": "value2"})
        
        view_manager.connect_signal_to_view("signal1", "layout_test1")
        view_manager.connect_signal_to_view("signal2", "layout_test2")
        view_manager.connect_signal_to_view("signal3", "layout_test1")
        view_manager.connect_signal_to_view("signal3", "layout_test2")
        
        # Save the layout
        layout = view_manager.save_layout()
        
        # Clear the manager
        view_manager.views.clear()
        view_manager.signal_views.clear()
        view_manager.view_configs.clear()
        
        # Load the layout
        result = view_manager.load_layout(layout)
        assert result is True
        
        # Check that views and connections were restored
        assert "layout_test1" in view_manager.views
        assert "layout_test2" in view_manager.views
        assert isinstance(view_manager.views["layout_test1"], MockView)
        assert isinstance(view_manager.views["layout_test2"], AnotherMockView)
        
        assert "signal1" in view_manager.signal_views
        assert "signal2" in view_manager.signal_views
        assert "signal3" in view_manager.signal_views
        
        assert "layout_test1" in view_manager.signal_views["signal1"]
        assert "layout_test2" in view_manager.signal_views["signal2"]
        assert "layout_test1" in view_manager.signal_views["signal3"]
        assert "layout_test2" in view_manager.signal_views["signal3"]
        
        assert view_manager.view_configs["layout_test1"] == {"key1": "value1"}
        assert view_manager.view_configs["layout_test2"] == {"key2": "value2"}
