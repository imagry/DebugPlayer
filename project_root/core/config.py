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
    "current_steering": ["plot1", "plot3"],
    "target_steering_angle": ["plot1", "plot3"],
    "current_speed": ["plot2","plot3"],
    "target_speed": ["plot2", "plot3"],
    "driving_mode": ["plot3"]   
    # Add additional mappings as needed
}

