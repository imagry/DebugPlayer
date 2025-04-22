#!/usr/bin/env python3

"""
Test configuration and fixtures for the Debug Player.

This module provides common fixtures and configuration for all tests,
particularly focused on Qt-related testing support.
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure Qt for testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Mock data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"

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

@pytest.fixture
def qtbot(request):
    """
    Fixture to provide QtBot for Qt widget testing.
    
    This is a wrapper around the pytest-qt qtbot fixture that provides
    additional functionality specific to Debug Player testing.
    """
    pytest_qt = pytest.importorskip("pytest_qt")
    result = pytest_qt.plugin.QtBot(request)
    return result
