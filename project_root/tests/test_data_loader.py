#!/usr/bin/env python3

"""
Test suite for the data_loader module.

These tests verify that the data loading process correctly validates
trip paths and handles errors appropriately.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to Python path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.data_loader import validate_trip_path, DataLoadError, get_available_signals


class TestDataLoader:
    """
    Test suite for the data_loader module functions.
    """
    
    def test_validate_trip_path_with_valid_directory(self):
        """
        Test that validate_trip_path accepts a valid directory.
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True):
            
            path = "/valid/trip/path"
            result = validate_trip_path(path)
            assert result == path
    
    def test_validate_trip_path_with_valid_file(self):
        """
        Test that validate_trip_path accepts a valid file.
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=False), \
             patch('os.path.isfile', return_value=True), \
             patch('os.access', return_value=True):
            
            path = "/valid/trip/file.txt"
            result = validate_trip_path(path)
            assert result == path
    
    def test_validate_trip_path_with_nonexistent_path(self):
        """
        Test that validate_trip_path rejects a nonexistent path.
        """
        with patch('os.path.exists', return_value=False):
            with pytest.raises(DataLoadError) as excinfo:
                validate_trip_path("/nonexistent/path")
            
            assert "does not exist" in str(excinfo.value)
    
    def test_validate_trip_path_with_invalid_path_type(self):
        """
        Test that validate_trip_path rejects a path that is neither a file nor a directory.
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=False), \
             patch('os.path.isfile', return_value=False):
            
            with pytest.raises(DataLoadError) as excinfo:
                validate_trip_path("/invalid/path/type")
            
            assert "neither a file nor a directory" in str(excinfo.value)
    
    def test_validate_trip_path_with_unreadable_file(self):
        """
        Test that validate_trip_path rejects an unreadable file.
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=False), \
             patch('os.path.isfile', return_value=True), \
             patch('os.access', return_value=False):
            
            with pytest.raises(DataLoadError) as excinfo:
                validate_trip_path("/unreadable/file.txt")
            
            assert "not readable" in str(excinfo.value)
    
    def test_validate_trip_path_with_empty_path(self):
        """
        Test that validate_trip_path rejects an empty path.
        """
        with pytest.raises(DataLoadError) as excinfo:
            validate_trip_path("")
        
        assert "cannot be empty" in str(excinfo.value)
    
    def test_get_available_signals(self):
        """
        Test that get_available_signals returns a dictionary.
        """
        result = get_available_signals("/valid/trip/path")
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
