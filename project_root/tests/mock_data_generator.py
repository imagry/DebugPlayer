#!/usr/bin/env python3

"""
Mock data generator for Debug Player plugin testing.

This module provides functions to generate realistic mock data for testing
plugins without requiring actual data files. It supports the creation of
various signal types needed for different plugins.
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path


def create_mock_trip_structure(base_path):
    """
    Create a realistic mock trip directory structure.
    
    Args:
        base_path (str): Base directory for mock trip
    
    Returns:
        Path: Path to created mock trip
    """
    trip_path = Path(base_path)
    
    # Create necessary directories
    dirs = [
        trip_path,
        trip_path / "vehicle",
        trip_path / "environment",
        trip_path / "sensors"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    return trip_path


def generate_car_pose_data(trip_path, num_points=1000):
    """
    Generate mock car pose data and save to appropriate files.
    
    Args:
        trip_path (str or Path): Path to mock trip directory
        num_points (int): Number of data points to generate
    
    Returns:
        pd.DataFrame: Generated car pose data
    """
    trip_path = Path(trip_path)
    
    # Generate timestamps (100 ms intervals)
    timestamps = np.arange(0, num_points * 100, 100)  # in milliseconds
    
    # Generate position data (simulate car moving in a circular path)
    angles = np.linspace(0, 4 * np.pi, num_points)
    radius = 50  # meters
    x = radius * np.cos(angles) + np.random.normal(0, 0.5, num_points)
    y = radius * np.sin(angles) + np.random.normal(0, 0.5, num_points)
    
    # Calculate orientation (tangent to the circle)
    theta = angles + np.pi/2
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'x': x,
        'y': y,
        'theta': theta
    })
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Save to CSV
    output_file = trip_path / "vehicle" / "car_pose.csv"
    df.to_csv(output_file)
    
    return df


def generate_car_state_data(trip_path, num_points=1000):
    """
    Generate mock car state data (speed, steering, etc).
    
    Args:
        trip_path (str or Path): Path to mock trip directory
        num_points (int): Number of data points to generate
    
    Returns:
        pd.DataFrame: Generated car state data
    """
    trip_path = Path(trip_path)
    
    # Generate timestamps (100 ms intervals)
    timestamps = np.arange(0, num_points * 100, 100)  # in milliseconds
    
    # Generate speed data (varying between 0-30 m/s)
    speed = 15 + 10 * np.sin(np.linspace(0, 8 * np.pi, num_points)) + np.random.normal(0, 1, num_points)
    speed = np.clip(speed, 0, 30)  # ensure non-negative speeds
    
    # Generate steering angle (-30 to 30 degrees)
    steering = 20 * np.sin(np.linspace(0, 12 * np.pi, num_points)) + np.random.normal(0, 2, num_points)
    steering = np.clip(steering, -30, 30)
    
    # Generate acceleration
    accel = np.diff(speed, prepend=speed[0]) / 0.1  # 100 ms intervals
    accel = np.clip(accel, -5, 5)  # reasonable acceleration limits
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'speed': speed,
        'steering': steering,
        'acceleration': accel
    })
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Save to CSV
    output_file = trip_path / "vehicle" / "car_state.csv"
    df.to_csv(output_file)
    
    return df


def generate_path_data(trip_path, num_points=1000):
    """
    Generate mock path data.
    
    Args:
        trip_path (str or Path): Path to mock trip directory
        num_points (int): Number of data points to generate
    
    Returns:
        pd.DataFrame: Generated path data
    """
    trip_path = Path(trip_path)
    
    # Generate a more complex path (figure-8)
    t = np.linspace(0, 2 * np.pi, num_points)
    x = 100 * np.sin(t)
    y = 50 * np.sin(2 * t)
    
    # Calculate path properties
    path_length = np.cumsum(np.sqrt(np.diff(x, prepend=x[0])**2 + np.diff(y, prepend=y[0])**2))
    curvature = np.gradient(np.arctan2(np.gradient(y), np.gradient(x)))
    
    # Create DataFrame
    df = pd.DataFrame({
        'path_x': x,
        'path_y': y,
        'path_length': path_length,
        'path_curvature': curvature
    })
    
    # Save to CSV
    output_file = trip_path / "environment" / "path_data.csv"
    df.to_csv(output_file)
    
    return df


def generate_sensor_data(trip_path, num_points=1000):
    """
    Generate mock sensor data.
    
    Args:
        trip_path (str or Path): Path to mock trip directory
        num_points (int): Number of data points to generate
    
    Returns:
        pd.DataFrame: Generated sensor data
    """
    trip_path = Path(trip_path)
    
    # Generate timestamps (100 ms intervals)
    timestamps = np.arange(0, num_points * 100, 100)  # in milliseconds
    
    # Generate some sensor values
    lidar_distance = 50 + 30 * np.sin(np.linspace(0, 6 * np.pi, num_points)) + np.random.normal(0, 2, num_points)
    radar_speed = 20 + 15 * np.cos(np.linspace(0, 4 * np.pi, num_points)) + np.random.normal(0, 1, num_points)
    camera_detection = np.random.choice([0, 1], size=num_points, p=[0.7, 0.3])
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'lidar_distance': lidar_distance,
        'radar_speed': radar_speed,
        'camera_detection': camera_detection
    })
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Save to CSV
    output_file = trip_path / "sensors" / "sensor_data.csv"
    df.to_csv(output_file)
    
    return df


def generate_complete_mock_trip(base_path):
    """
    Generate a complete mock trip with all necessary data files.
    
    Args:
        base_path (str or Path): Base directory for mock trip
    
    Returns:
        Path: Path to created mock trip
    """
    trip_path = create_mock_trip_structure(base_path)
    
    # Generate various data types
    car_pose_df = generate_car_pose_data(trip_path)
    car_state_df = generate_car_state_data(trip_path)
    path_df = generate_path_data(trip_path)
    sensor_df = generate_sensor_data(trip_path)
    
    # Create a metadata file
    metadata = {
        'trip_id': 'mock_trip_001',
        'date': '2025-04-23',
        'duration_ms': 100000,
        'num_frames': 1000
    }
    
    import json
    with open(trip_path / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return trip_path


if __name__ == "__main__":
    # If run directly, generate a mock trip in the test_data directory
    test_data_dir = Path(__file__).parent / "test_data" / "mock_trip"
    trip_path = generate_complete_mock_trip(test_data_dir)
    print(f"Generated mock trip at: {trip_path}")
