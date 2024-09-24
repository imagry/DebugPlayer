import numpy as np
import subprocess
import sys
import pkg_resources
   
def is_padded_segment(path, start, threshold):
    """
    Checks if the segment starting at `start` is a padded segment.
    
    Parameters:
    path (np.ndarray): The path array.
    start (int): The start index for checking.
    threshold (int): The threshold for consecutive zeros.
    
    Returns:
    bool: True if the segment is padded, False otherwise.
    """
    zero_count = 0
    for i in range(start, min(start + threshold, len(path))):
        if np.array_equal(path[i], [0, 0]):
            zero_count += 1
        else:
            return False
    return zero_count >= threshold

def extract_valid_path(path, padding_threshold=5):
    """
    Extracts the valid part of a path padded with zeros using binary search.
    
    Parameters:
    path (np.ndarray): A numpy array of shape (300, 2) containing 2D waypoints.
    padding_threshold (int): Number of consecutive zeros to consider as the start of padding.
    
    Returns:
    np.ndarray: The valid part of the path without padding.
    """
    path = np.array(path)
    
    # Check if the last term is not (0,0)
    if not np.array_equal(path[-1], [0, 0]):
        return path
    
    # Binary search to find the start of the padding
    left, right = 0, len(path) - 1
    while left < right:
        mid = (left + right) // 2
        if is_padded_segment(path, mid, padding_threshold):
            right = mid
        else:
            left = mid + 1
    
    # Check if the left index is the start of padding
    if is_padded_segment(path, left, padding_threshold):
        return path[:left]
    
    return path