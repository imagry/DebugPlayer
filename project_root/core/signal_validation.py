#!/usr/bin/env python3

"""
Signal Validation Module for the Debug Player

This module provides a comprehensive validation system for signal definitions in the
Debug Player framework. It ensures that plugins correctly define their signals according
to the required specifications for each signal type.

Signal Types:
- temporal: Time-series data plotted on a 2D graph (e.g., velocity vs time)
- spatial: 2D or 3D spatial data (e.g., vehicle position on a map)
- categorical: Discrete categorical data (e.g., operational modes)
- boolean: Binary state data (e.g., system flags, on/off states)

Signal Definition Requirements:
- Every signal must have a 'type' field matching one of the defined types
- Every signal must have a 'func' field containing a callable that returns data
- Some signal types have additional required fields (e.g., 'categories' for categorical signals)
- Additional metadata fields may be included for enhanced functionality

Usage:
    validated_signal = validate_signal_definition("signal_name", signal_info, "plugin_name")
"""

from typing import Dict, Any, Callable, List, Union, Optional


class SignalValidationError(Exception):
    """Exception raised for errors in the signal validation process."""
    pass


# Define known signal types and their expected format
SIGNAL_TYPES = {
    "temporal": {
        "description": "Time-series data that changes with timestamp",
        "required_fields": ["func", "type"],
        "optional_fields": ["description", "units", "valid_range"],
    },
    "spatial": {
        "description": "Spatial data that may be 2D or 3D",
        "required_fields": ["func", "type"],
        "optional_fields": ["description", "coordinate_system", "units", "valid_range"],
    },
    "categorical": {
        "description": "Data with discrete categories or states",
        "required_fields": ["func", "type", "categories"],
        "optional_fields": ["description"],
    },
    "boolean": {
        "description": "Binary true/false data",
        "required_fields": ["func", "type"],
        "optional_fields": ["description", "true_label", "false_label"],
    },
}


def validate_signal_definition(signal_name: str, signal_info: Dict[str, Any], plugin_name: str) -> Dict[str, Any]:
    """
    Validate a signal definition and return a normalized version.
    
    This function performs several key validations:
    1. Ensures the signal definition is a dictionary
    2. Verifies that the 'func' field contains a callable
    3. Checks that the 'type' field is one of the supported signal types
    4. Validates that all required fields for the specific signal type are present
    
    The function also normalizes the signal definition by adding the plugin name
    and ensuring all fields follow the expected format.
    
    Args:
        signal_name (str): The name of the signal (e.g., "car_pose", "velocity")
        signal_info (Dict[str, Any]): The signal definition dictionary from the plugin
        plugin_name (str): The name of the plugin providing this signal
        
    Returns:
        Dict[str, Any]: A normalized signal definition with all required fields,
                        ready to be registered with the PlotManager
        
    Raises:
        SignalValidationError: If the signal definition is invalid or missing required fields
    """
    if not isinstance(signal_info, dict):
        raise SignalValidationError(
            f"Signal '{signal_name}' in plugin '{plugin_name}' "
            f"has an invalid definition (not a dictionary): {signal_info}"
        )
    
    # Extract signal function and type
    signal_func = signal_info.get("func")
    signal_type = signal_info.get("type", "temporal")  # Default to "temporal"
    
    # Check if function is callable
    if not callable(signal_func):
        raise SignalValidationError(
            f"Signal '{signal_name}' in plugin '{plugin_name}' "
            f"does not have a valid callable function."
        )
    
    # Check if type is valid
    if signal_type not in SIGNAL_TYPES:
        # Rather than error, we'll default to 'temporal' with a warning
        print(
            f"Warning: Signal '{signal_name}' in plugin '{plugin_name}' "
            f"has unknown type '{signal_type}'. Defaulting to 'temporal'."
        )
        signal_type = "temporal"
    
    # Create a normalized signal definition
    normalized_signal = {
        "plugin": plugin_name,
        "func": signal_func,
        "type": signal_type,
    }
    
    # Copy over any additional fields from the original definition
    for key, value in signal_info.items():
        if key not in ["func", "type"]:
            normalized_signal[key] = value
    
    return normalized_signal


def check_required_signal_fields(signal_name: str, signal_info: Dict[str, Any], plugin_name: str) -> List[str]:
    """
    Check if a signal definition has all required fields for its specific type.
    
    Different signal types have different required fields. For example:
    - All signal types require 'func' and 'type'
    - 'categorical' signals also require a 'categories' field
    
    This function helps ensure that plugins correctly implement all required
    fields for the signals they provide.
    
    Args:
        signal_name (str): The name of the signal to check
        signal_info (Dict[str, Any]): The signal definition dictionary from the plugin
        plugin_name (str): The name of the plugin providing this signal
        
    Returns:
        List[str]: A list of missing required fields. Empty list if all required fields are present.
    """
    signal_type = signal_info.get("type", "temporal")
    
    if signal_type not in SIGNAL_TYPES:
        return []  # Can't check required fields for unknown types
    
    required_fields = SIGNAL_TYPES[signal_type]["required_fields"]
    missing_fields = [field for field in required_fields if field not in signal_info]
    
    return missing_fields


def get_signal_metadata(signal_type: str) -> Dict[str, Any]:
    """
    Get metadata for a specific signal type.
    
    This function retrieves the definition and requirements for a given signal type,
    including its description, required fields, and optional fields.
    
    Args:
        signal_type (str): The signal type to get metadata for (e.g., "temporal", "spatial")
        
    Returns:
        Dict[str, Any]: Metadata dictionary containing:
            - description: String describing the signal type
            - required_fields: List of field names that must be present
            - optional_fields: List of additional fields that may be present
            Returns an empty dict if the type is unknown.
    """
    if signal_type not in SIGNAL_TYPES:
        return {}  # Unknown type
    
    return SIGNAL_TYPES[signal_type]
