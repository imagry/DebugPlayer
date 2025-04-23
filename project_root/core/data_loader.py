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


def parse_arguments() -> Optional[Union[str, Tuple[str, str]]]:
    """
    Parse command-line arguments and validate trip paths.
    
    Returns:
        Optional[Union[str, Tuple[str, str]]]: The validated trip path(s) or None if using mock data.
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
        default=None,
        help='Path to the first trip data directory or file (optional)'
    )
    parser.add_argument(
        '--trip2', 
        type=str, 
        default=None, 
        help='Path to the second trip data directory or file (optional for comparison)'
    )
    parser.add_argument(
        '--mock', 
        action='store_true',
        help='Use mock data instead of loading from files (for development)'
    )
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    try:
        # If mock flag is set, return None to indicate using mock data
        if args.mock:
            print("Using mock data for development.")
            return None
        
        # Check if trip paths are provided
        if not args.trip1:
            print("No trip path provided. Using mock data for development.")
            return None
        
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
    
    Args:
        trip_path (str): Path to trip data.
        
    Returns:
        dict: Dictionary of available signals and their types.
    """
    # This is a placeholder for future implementation
    # In the future, this could scan the trip directory structure
    # and find available signals based on file patterns or metadata
    
    # For now, return an empty dict to indicate no automatic detection
    return {}
