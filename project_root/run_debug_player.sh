#!/bin/bash

# Debug Player Startup Script
# This script ensures the application runs with the correct conda environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment
source ~/anaconda3/bin/activate DbgPkg

# Set environment variables for Qt
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export QT_PLUGIN_PATH=$CONDA_PREFIX/lib/Qt/plugins

# Check if trip path was provided
if [ $# -eq 0 ]; then
    echo "No trip path provided. Running with default settings."
    python "$SCRIPT_DIR/main.py"
else
    # Run the application with the provided trip path
    python "$SCRIPT_DIR/main.py" --trip "$1"
fi
