#!/usr/bin/env python3

"""
Test suite for the data_loader module.

These tests verify that the data loading process correctly validates
trip paths and handles errors appropriately.
"""

import os
import sys
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add project root to Python path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from core.data_loader import validate_trip_path, DataLoadError, get_available_signals, parse_arguments


class TestDataLoader:
    """
    Test suite for the data_loader module functions.
    """
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_validate_trip_path_with_valid_directory(self, temp_dir):
        """
        Test that validate_trip_path accepts a valid directory.
        """
        # Create a test directory
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        result = validate_trip_path(str(test_dir))
        assert result == str(test_dir)
    
    def test_validate_trip_path_with_valid_file(self, temp_dir):
        """
        Test that validate_trip_path accepts a valid file.
        """
        # Create a test file
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test data")
        
        result = validate_trip_path(str(test_file))
        assert result == str(test_file)
    
    def test_validate_trip_path_with_nonexistent_path(self):
        """
        Test that validate_trip_path rejects a nonexistent path.
        """
        with pytest.raises(DataLoadError) as excinfo:
            validate_trip_path("/nonexistent/path/that/does/not/exist")
        
        assert "does not exist" in str(excinfo.value)
    
    def test_validate_trip_path_with_unreadable_file(self, temp_dir):
        """
        Test that validate_trip_path rejects an unreadable file.
        """
        if os.name == 'nt':
            pytest.skip("File permissions work differently on Windows")
            
        # Create a file and make it unreadable
        test_file = temp_dir / "unreadable.txt"
        test_file.write_text("test data")
        test_file.chmod(0o000)  # No permissions
        
        try:
            with pytest.raises(DataLoadError) as excinfo:
                validate_trip_path(str(test_file))
            assert "not readable" in str(excinfo.value)
        finally:
            # Clean up permissions so temp dir can be removed
            test_file.chmod(0o644)
    
    def test_validate_trip_path_with_empty_path(self):
        """
        Test that validate_trip_path rejects an empty path.
        """
        with pytest.raises(DataLoadError) as excinfo:
            validate_trip_path("")
        
        assert "cannot be empty" in str(excinfo.value)
    
    def test_parse_arguments_single_trip(self, temp_dir):
        """Test parsing command line arguments with a single trip."""
        test_dir = temp_dir / "trip1"
        test_dir.mkdir()
        
        with patch('sys.argv', ['script.py', '--trip1', str(test_dir)]):
            result = parse_arguments()
            assert result == str(test_dir)
    
    def test_parse_arguments_two_trips(self, temp_dir):
        """Test parsing command line arguments with two trips."""
        trip1 = temp_dir / "trip1"
        trip2 = temp_dir / "trip2"
        trip1.mkdir()
        trip2.mkdir()
        
        with patch('sys.argv', ['script.py', '--trip1', str(trip1), '--trip2', str(trip2)]):
            result = parse_arguments()
            assert result == (str(trip1), str(trip2))
    
    def test_parse_arguments_missing_trip(self, capsys):
        """Test error handling when no trip is provided."""
        with patch('sys.argv', ['script.py']), \
             pytest.raises(SystemExit):
            parse_arguments()
        
        captured = capsys.readouterr()
        assert "No trip path provided" in captured.err
    
    def test_parse_arguments_invalid_trip(self, capsys, temp_dir):
        """Test error handling with invalid trip path."""
        invalid_path = str(temp_dir / "nonexistent")
        
        with patch('sys.argv', ['script.py', '--trip1', invalid_path]), \
             pytest.raises(SystemExit):
            parse_arguments()
        
        captured = capsys.readouterr()
        assert "does not exist" in captured.err
    
    def test_get_available_signals_with_csv_files(self, temp_dir):
        """Test that get_available_signals finds CSV files in a directory."""
        # Create test CSV files
        signals_dir = temp_dir / "signals"
        signals_dir.mkdir()
        
        # Create a CSV file with some data
        df1 = pd.DataFrame({
            'timestamp': [0, 1, 2],
            'value': [1.0, 2.0, 3.0]
        })
        df1.to_csv(signals_dir / "signal1.csv", index=False)
        
        # Create another CSV file
        df2 = pd.DataFrame({
            'time': [0, 1, 2],
            'velocity': [10.0, 11.0, 12.0]
        })
        df2.to_csv(signals_dir / "signal2.csv", index=False)
        
        # Test getting available signals
        signals = get_available_signals(str(signals_dir))
        
        # Verify the signals were found
        assert "signal1" in signals
        assert signals["signal1"]["type"] == "temporal"
        assert "signal2" in signals
        assert signals["signal2"]["type"] == "temporal"
    
    def test_get_available_signals_with_pickle_file(self, temp_dir):
        """Test that get_available_signals can handle pickle files."""
        import pickle
        
        # Create test data
        test_data = {
            'timestamps': [0, 1, 2],
            'values': [1.0, 2.0, 3.0]
        }
        
        # Save as pickle
        pickle_file = temp_dir / "test_data.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(test_data, f)
        
        # Test getting available signals
        signals = get_available_signals(str(pickle_file))
        
        # Verify the signal was found
        assert "test_data" in signals
        assert signals["test_data"]["type"] == "generic"
    
    def test_get_available_signals_empty_directory(self, temp_dir):
        """Test get_available_signals with an empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        signals = get_available_signals(str(empty_dir))
        assert signals == {}
    
    def test_get_available_signals_invalid_path(self):
        """Test get_available_signals with invalid path."""
        with pytest.raises(DataLoadError):
            get_available_signals("/invalid/path/that/does/not/exist")


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
