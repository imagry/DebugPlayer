# core/config.py

# Spatial signals: represent 2D map-based data like routes, poses, etc.
spatial_signals = [
    "car_pose(t)", "route", "path_in_world_coordinates(t)"
]

# Temporal signals: represent time-series data like speed, steering, etc.
temporal_signals = [
    "current_speed", "current_steering", "driving_mode", 
    "target_speed", "target_steering_angle"
]


# Updated mapping: signals assigned to one or more axes
temporal_signal_axes = {
    "current_steering": ["ax1", "ax3"],
    "target_steering_angle": ["ax1", "ax3"],
    "current_speed": ["ax2","ax3"],
    "target_speed": ["ax2", "ax3"],
    "driving_mode": ["ax3", "ax3"]   
    # Add additional mappings as needed
}

