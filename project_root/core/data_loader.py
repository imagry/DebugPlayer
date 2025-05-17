import argparse
import os
import sys
from typing import Union, Tuple, Optional


class DataLoadError(Exception):
    """Exception raised for errors in the data loading process."""
    pass


def validate_trip_path(path: str) -> str:
    """
    Validate if a trip path exists and is accessible.
    
    Args:
        path (str): The path to validate.
        
    Returns:
        str: The validated path.
        
    Raises:
        DataLoadError: If the path doesn't exist or isn't accessible.
    """
    if not path:
        raise DataLoadError("Trip path cannot be empty.")
        
    # Expand user directory if present (e.g., ~/)
    expanded_path = os.path.expanduser(path)
    
    # Check if the path exists
    if not os.path.exists(expanded_path):
        raise DataLoadError(f"Trip path does not exist: {expanded_path}")
    
    # Check if it's a directory (most trip data is stored in directories)
    if not os.path.isdir(expanded_path):
        # If it's a file, check if it's readable
        if not os.path.isfile(expanded_path):
            raise DataLoadError(f"Trip path is neither a file nor a directory: {expanded_path}")
        elif not os.access(expanded_path, os.R_OK):
            raise DataLoadError(f"Trip file exists but is not readable: {expanded_path}")
    
    return expanded_path


def parse_arguments() -> Union[str, Tuple[str, str]]:
    """
    Parse command-line arguments and validate trip paths.
    
    Returns:
        Union[str, Tuple[str, str]]: The validated trip path(s).
        
    Raises:
        DataLoadError: If no valid trip paths are provided.
    """
    # Create an argument parser with more descriptive help
    parser = argparse.ArgumentParser(
        description="Debug Player: A tool for visualizing and analyzing trip data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )  
    
    # Add the trip arguments with better descriptions
    parser.add_argument(
        '--trip1', 
        type=str, 
        help='Path to the first trip data directory or file (required)'
    )
    parser.add_argument(
        '--trip2', 
        type=str, 
        default=None, 
        help='Path to the second trip data directory or file (optional for comparison)'
    )
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    try:
        # Check if at least one trip path is provided
        if not args.trip1:
            raise DataLoadError(
                "No trip path provided. Please specify at least one trip path using --trip1."
            )
        
        # Validate the primary trip path
        trip1_path = validate_trip_path(args.trip1)
        
        # If second trip is provided, validate it too
        if args.trip2:
            trip2_path = validate_trip_path(args.trip2)
            return trip1_path, trip2_path
        
        # If only one trip is provided, return just that path
        return trip1_path
        
    except DataLoadError as e:
        # Print the error message in red for better visibility
        print(f"\033[91mError: {str(e)}\033[0m", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


def get_available_signals(trip_path: str) -> dict:
    """
    Scan trip data and return available signals.
    
    This function scans the specified directory for data files (CSV, pickle) and
    extracts information about available signals.
    
    Args:
        trip_path (str): Path to trip data directory or file.
        
    Returns:
        dict: Dictionary where keys are signal names and values are dictionaries
              containing signal metadata (type, description, etc.).
              
    Raises:
        DataLoadError: If the trip path is invalid or inaccessible.
    """
    import os
    import pandas as pd
    import pickle
    from pathlib import Path
    
    # Check if path exists
    if not os.path.exists(trip_path):
        raise DataLoadError(f"Trip path does not exist: {trip_path}")
    
    signals = {}
    path = Path(trip_path)
    
    # If it's a file, handle it directly
    if path.is_file():
        if path.suffix.lower() == '.pkl':
            # Handle pickle file
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                signals[path.stem] = {
                    'type': 'generic',
                    'description': f'Data from {path.name}',
                    'source': str(path)
                }
            except (pickle.PickleError, EOFError) as e:
                raise DataLoadError(f"Error reading pickle file {path}: {str(e)}")
        elif path.suffix.lower() == '.csv':
            # Handle CSV file
            signals[path.stem] = {
                'type': 'temporal',
                'description': f'Time series data from {path.name}',
                'source': str(path)
            }
        return signals
    
    # If it's a directory, scan for data files
    if not path.is_dir():
        raise DataLoadError(f"Path is neither a file nor a directory: {trip_path}")
    
    # Scan for CSV files
    for csv_file in path.glob('**/*.csv'):
        try:
            # Just read the header to check if it's a valid CSV
            with open(csv_file, 'r') as f:
                # Read just the first line to get headers
                header = f.readline().strip().split(',')
                if len(header) >= 2:  # At least one data column + timestamp
                    signals[csv_file.stem] = {
                        'type': 'temporal',
                        'description': f'Time series data from {csv_file.name}',
                        'source': str(csv_file),
                        'columns': header
                    }
        except Exception as e:
            # Skip files that can't be read
            continue
    
    # Scan for pickle files
    for pkl_file in path.glob('**/*.pkl'):
        try:
            with open(pkl_file, 'rb') as f:
                # Just try to load it to verify it's a valid pickle
                data = pickle.load(f)
                signals[pkl_file.stem] = {
                    'type': 'generic',
                    'description': f'Data from {pkl_file.name}',
                    'source': str(pkl_file)
                }
        except (pickle.PickleError, EOFError):
            # Skip invalid pickle files
            continue
    
    return signals
