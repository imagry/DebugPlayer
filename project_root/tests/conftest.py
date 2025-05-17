#!/usr/bin/env python3

"""
Test configuration and fixtures for the Debug Player.

This module provides common fixtures and configuration for all tests,
particularly focused on Qt-related testing support.
"""

import os
import sys
import tempfile
import time
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure Qt for testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Mock data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"

# Test data generation parameters
TEST_TIMESTAMPS = np.linspace(0, 10, 100)  # 10 seconds of data at 10Hz

@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path (module scoped)."""
    if not TEST_DATA_DIR.exists():
        TEST_DATA_DIR.mkdir(parents=True)
    return TEST_DATA_DIR

@pytest.fixture
def mock_trip_path(test_data_dir):
    """Fixture to provide a mock trip path for testing."""
    return str(test_data_dir / "mock_trip")

@pytest.fixture(scope='session')
def qapp():
    """Fixture to provide a QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        # Create QApplication if it doesn't exist
        app = QApplication([])
    
    return app

@pytest.fixture
def qtbot(qapp, request):
    """
    Fixture to provide QtBot for Qt widget testing.
    
    This is a wrapper around the pytest-qt qtbot fixture that provides
    additional functionality specific to Debug Player testing.
    """
    try:
        from pytestqt.qtbot import QtBot
        return QtBot(request)
    except ImportError:
        pytest.skip("pytest-qt not installed")

@pytest.fixture
def mock_plot_manager():
    """Fixture to provide a mock PlotManager instance."""
    pm = MagicMock()
    pm.signals = {}
    pm.plots = []
    pm.plugins = {}
    pm.signal_plugins = {}
    return pm

@pytest.fixture
def timeline_controller(mock_plot_manager):
    """Fixture to provide a TimelineController instance for testing."""
    from core.timeline import TimelineController
    return TimelineController(plot_manager=mock_plot_manager, update_interval=10)

@pytest.fixture
def mock_temporal_plot():
    """Fixture to provide a mock temporal plot widget."""
    plot = MagicMock()
    plot.signal_names = []
    plot.update_time_range = MagicMock()
    return plot

@pytest.fixture
def mock_spatial_plot():
    """Fixture to provide a mock spatial plot widget."""
    plot = MagicMock()
    plot.signal_names = []
    plot.update_time_range = MagicMock()
    return plot

@pytest.fixture
def test_signal_data():
    """Generate test signal data for testing."""
    return {
        'timestamps': TEST_TIMESTAMPS,
        'values': np.sin(TEST_TIMESTAMPS),
        'metadata': {
            'name': 'test_signal',
            'unit': 'm/s',
            'description': 'Test signal data'
        }
    }

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def test_csv_file(temp_dir):
    """Create a test CSV file with signal data."""
    df = pd.DataFrame({
        'timestamp': TEST_TIMESTAMPS,
        'value': np.sin(TEST_TIMESTAMPS)
    })
    
    csv_path = temp_dir / "test_signal.csv"
    df.to_csv(csv_path, index=False)
    return csv_path

@pytest.fixture
def test_pickle_file(temp_dir, test_signal_data):
    """Create a test pickle file with signal data."""
    import pickle
    
    pkl_path = temp_dir / "test_signal.pkl"
    with open(pkl_path, 'wb') as f:
        pickle.dump(test_signal_data, f)
    return pkl_path
