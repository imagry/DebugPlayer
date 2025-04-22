#!/usr/bin/env python3

"""
Test script to verify Qt dependencies installation.
This will help diagnose any missing Qt components.
"""

import sys
import importlib
from importlib import metadata


def test_import(module_name):
    """Test importing a module and report success or failure."""
    try:
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False


def get_package_version(package_name):
    """Get installed version of a package."""
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return "Not installed"


def main():
    """Main function to test Qt dependencies."""
    print("=== Testing Qt Dependencies ===")
    print(f"Python version: {sys.version}")
    
    # Test core PySide6 packages
    pyside_version = get_package_version("PySide6")
    print(f"PySide6 version: {pyside_version}")
    
    # Test imports
    modules_to_test = [
        "PySide6.QtCore",
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "PySide6.QtCharts",  # The problematic module
        "pyqtgraph"
    ]
    
    results = []
    for module in modules_to_test:
        results.append(test_import(module))
    
    # Summary
    print("\n=== Summary ===")
    success_count = results.count(True)
    print(f"Successful imports: {success_count}/{len(results)}")
    
    if not all(results):
        print("\n=== Recommendations ===")
        print("If QtCharts is missing, try the following:")
        print("1. Install the Qt Charts development package:")
        print("   sudo apt-get install libqt6charts6 libqt6charts6-dev")
        print("2. Ensure environment variables are set correctly:")
        print("   export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH")
        print("   export QT_PLUGIN_PATH=$CONDA_PREFIX/lib/Qt/plugins")


if __name__ == "__main__":
    main()
