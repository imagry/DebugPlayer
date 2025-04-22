#!/usr/bin/env python3

"""
Test suite for the signal_validation module.

These tests verify that signal definitions are correctly validated and normalized.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

# Add project root to Python path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.signal_validation import (
    validate_signal_definition, 
    check_required_signal_fields, 
    get_signal_metadata,
    SignalValidationError,
    SIGNAL_TYPES
)


class TestSignalValidation:
    """
    Test suite for the signal_validation module.
    """
    
    def test_validate_signal_definition_valid(self):
        """
        Test that a valid signal definition is properly normalized.
        """
        signal_name = "test_signal"
        signal_info = {
            "func": lambda: None,
            "type": "temporal",
            "description": "A test signal"
        }
        plugin_name = "test_plugin"
        
        result = validate_signal_definition(signal_name, signal_info, plugin_name)
        
        # Check that the normalized signal has all required fields
        assert result["plugin"] == plugin_name
        assert result["func"] == signal_info["func"]
        assert result["type"] == signal_info["type"]
        assert result["description"] == signal_info["description"]
    
    def test_validate_signal_definition_invalid_not_dict(self):
        """
        Test that a non-dictionary signal definition raises a validation error.
        """
        with pytest.raises(SignalValidationError) as excinfo:
            validate_signal_definition(
                "test_signal", "not_a_dict", "test_plugin"
            )
        
        assert "not a dictionary" in str(excinfo.value)
    
    def test_validate_signal_definition_invalid_func(self):
        """
        Test that a signal definition with a non-callable function raises a validation error.
        """
        with pytest.raises(SignalValidationError) as excinfo:
            validate_signal_definition(
                "test_signal", {"func": "not_callable", "type": "temporal"}, "test_plugin"
            )
        
        assert "not have a valid callable function" in str(excinfo.value)
    
    def test_validate_signal_definition_unknown_type(self):
        """
        Test that a signal definition with an unknown type is defaulted to 'temporal'.
        """
        signal_name = "test_signal"
        signal_info = {
            "func": lambda: None,
            "type": "unknown_type"
        }
        plugin_name = "test_plugin"
        
        result = validate_signal_definition(signal_name, signal_info, plugin_name)
        
        # The type should be defaulted to 'temporal'
        assert result["type"] == "temporal"
    
    def test_check_required_signal_fields_complete(self):
        """
        Test that a signal definition with all required fields returns an empty list.
        """
        signal_name = "test_signal"
        signal_info = {
            "func": lambda: None,
            "type": "temporal"
        }
        plugin_name = "test_plugin"
        
        result = check_required_signal_fields(signal_name, signal_info, plugin_name)
        
        assert result == []
    
    def test_check_required_signal_fields_missing(self):
        """
        Test that a signal definition missing required fields returns those fields.
        """
        signal_name = "test_signal"
        signal_info = {
            # Missing "func"
            "type": "categorical",
            # Missing "categories"
        }
        plugin_name = "test_plugin"
        
        result = check_required_signal_fields(signal_name, signal_info, plugin_name)
        
        assert "func" in result
        assert "categories" in result
    
    def test_get_signal_metadata_known_type(self):
        """
        Test that get_signal_metadata returns the correct metadata for a known type.
        """
        for signal_type in SIGNAL_TYPES:
            result = get_signal_metadata(signal_type)
            
            assert "description" in result
            assert "required_fields" in result
            assert "optional_fields" in result
    
    def test_get_signal_metadata_unknown_type(self):
        """
        Test that get_signal_metadata returns an empty dict for an unknown type.
        """
        result = get_signal_metadata("unknown_type")
        
        assert result == {}


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
