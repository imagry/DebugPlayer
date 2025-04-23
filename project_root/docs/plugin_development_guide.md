# Debug Player Plugin Development Guide

## Overview

The Debug Player's plugin system allows you to extend the application with custom data sources, visualizations, and processors. This guide explains how to create, test, and distribute plugins for the Debug Player.

## Plugin Types

The Debug Player supports several types of plugins:

- **Data Source Plugins**: Load and provide data from external files or sources
- **Visualization Plugins**: Provide custom visualization for specific data types
- **Processor Plugins**: Transform or analyze data from other plugins
- **Exporter Plugins**: Export data or visualizations to external formats

## Creating a New Plugin

### Plugin Structure

A plugin consists of at least one Python file with a class that:

1. Inherits from `PluginBase`
2. Implements all required methods
3. Provides metadata through the `METADATA` class attribute
4. Exposes data through signals defined in the `signals` dictionary
5. Is exported via the `plugin_class` variable

### Basic Example

Here's a minimal example of a valid plugin:

```python
from interfaces.PluginBase import PluginBase
from typing import Dict, Any, Optional

class MyPlugin(PluginBase):
    # Required plugin metadata
    METADATA = {
        "name": "My Plugin",
        "version": "1.0.0",
        "description": "A plugin that does something useful",
        "author": "Your Name",
        "type": "data_source"
    }
    
    def __init__(self, file_path: Optional[str] = None):
        super().__init__(file_path)
        # Initialize data structures
        self.data = {}
        
        # Define signals
        self.signals = {
            "my_signal": {
                "func": self.get_my_signal_data,
                "type": "temporal",
                "description": "My useful signal",
                "units": "meters/sec",
                "category": "measurements",
                "tags": ["velocity", "sensor"]
            }
        }
        
        # Load data if file_path is provided
        if file_path:
            self._load_data(file_path)
        else:
            self._generate_mock_data()
    
    def has_signal(self, signal: str) -> bool:
        return signal in self.signals
    
    def get_data_for_timestamp(self, signal: str, timestamp: float) -> Optional[Dict[str, Any]]:
        if not self.has_signal(signal):
            return None
            
        # Implement your data retrieval logic here
        # This is just an example
        if signal == "my_signal":
            return {"value": self.data.get(timestamp, 0.0)}
        
        return None
    
    def _load_data(self, file_path: str) -> None:
        # Implement loading data from the file
        pass
    
    def _generate_mock_data(self) -> None:
        # Generate sample data for testing
        for t in range(0, 1000, 10):
            self.data[t] = t * 0.1

# This line is required to export the plugin class
plugin_class = MyPlugin
```

### Plugin Metadata

The `METADATA` class attribute is required and must include these fields:

- `name`: The human-readable name of your plugin
- `version`: The version number in semantic versioning format (X.Y.Z)
- `description`: A brief description of what your plugin does
- `author`: Your name or organization

Optional metadata fields include:

- `type`: The plugin type ("data_source", "visualization", "processor", "exporter")
- `url`: A URL for more information about your plugin
- `dependencies`: A dictionary of other plugins your plugin depends on
- `license`: The license your plugin is distributed under

Example with all fields:

```python
METADATA = {
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "A plugin that does something useful",
    "author": "Your Name",
    "type": "data_source",
    "url": "https://github.com/yourusername/my-plugin",
    "dependencies": {
        "core_plugin": ">=0.5.0"
    },
    "license": "MIT"
}
```

### Signal Definitions

The `signals` dictionary defines what data your plugin provides. Each signal requires at least:

- `func`: A method in your class that returns data for this signal
- `type`: The signal type ("temporal", "spatial", "categorical", etc.)

Recommended additional signal metadata:

- `description`: A description of what the signal represents
- `units`: The units of measurement (if applicable)
- `category`: A category for organizing signals
- `tags`: A list of tags for filtering
- `valid_range`: The valid range of values (min/max)
- `precision`: Display precision for numeric values
- `critical_values`: Important threshold values
- `color`: Default display color

Example with rich metadata:

```python
self.signals = {
    "vehicle_speed": {
        "func": self.get_vehicle_speed,
        "type": "temporal",
        "description": "Vehicle speed from odometry",
        "units": "m/s",
        "category": "vehicle_state",
        "tags": ["speed", "odometry"],
        "valid_range": {"min": 0.0, "max": 40.0},
        "precision": 2,
        "critical_values": {"max_legal": 13.8},  # 50 km/h in m/s
        "color": "#ff0000"  # Red
    }
}
```

## Signal Types

The Debug Player supports different signal types, each with its own data format:

### Temporal Signals

Time-series data shown in plots against time.

```python
# Return format:
{"value": 42.0}  # Single value
# or
{"values": [41.0, 42.0, 43.0]}  # Multiple values
```

### Spatial Signals

Geometric data shown in 2D or 3D plots.

```python
# Return format:
{"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]}  # 2D points
# or with orientation
{"x": [1.0], "y": [2.0], "theta": [0.5]}  # Vehicle pose
```

### Categorical Signals

Discrete categorized data.

```python
# Return format:
{"value": "category_name"}
# or
{"values": ["cat1", "cat2"], "counts": [5, 10]}
```

### Text Signals

Text-based data like logs or messages.

```python
# Return format:
{"value": "Log message text"}
# or
{"values": ["Log line 1", "Log line 2", "Log line 3"]}
```

### Statistical Signals

Data representing statistics or metrics.

```python
# Return format:
{"mean": 10.5, "std": 2.3, "min": 5.0, "max": 15.0}
# or any dictionary of metric names to values
```

## Testing Your Plugin

### Using Mock Data

When your plugin is initialized with `file_path=None`, it should generate mock data for testing. This allows your plugin to work in demo mode without real data files.

### Writing Unit Tests

Create unit tests to verify your plugin works as expected:

```python
def test_plugin_initialization():
    plugin = MyPlugin(None)  # Use mock data
    assert plugin.has_signal("my_signal")
    
def test_signal_data():
    plugin = MyPlugin(None)
    data = plugin.get_data_for_timestamp("my_signal", 100.0)
    assert data is not None
    assert "value" in data
    assert isinstance(data["value"], float)
```

## Packaging and Distribution

### Plugin File Location

Place your plugin file in one of these locations:

1. The main `plugins/` directory for bundled plugins
2. The `plugins/user_plugins/` directory for user-installed plugins

### Dependencies

If your plugin requires external Python packages, list them in a `requirements.txt` file next to your plugin.

### Distribution

Package your plugin for distribution as a ZIP file containing:

- Your plugin Python file(s)
- A `requirements.txt` file (if needed)
- A README.md with installation and usage instructions

## Plugin Integration Tips

### Signal Registry Integration

Signals are registered with the `SignalRegistry` when your plugin is loaded. Make sure your signal names are unique and descriptive.

### View Compatibility

Ensure your signals specify the correct `type` to be compatible with the appropriate views:

- `temporal` signals work with `TemporalView` and `TableView`
- `spatial` signals work with `SpatialView`
- `text` signals work with `TextView`
- All signal types work with `MetricsView`

### Best Practices

1. **Error Handling**: Handle exceptions gracefully in your plugin
2. **Performance**: Optimize data loading and processing for large datasets
3. **Versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)
4. **Documentation**: Include clear documentation in your plugin's docstring
5. **Configuration**: Allow customization through constructor parameters

## Advanced Features

### Plugin Events

Implement optional event handler methods in your plugin:

```python
def on_load(self):
    """Called when the plugin is fully loaded"""
    pass
    
def on_unload(self):
    """Called before the plugin is unloaded"""
    pass
    
def on_timestamp_changed(self, timestamp: float):
    """Called when the global timestamp changes"""
    pass
```

### Custom UI Components

Plugins can provide custom UI components:

```python
def get_custom_widget(self) -> Optional[QWidget]:
    """Return a custom widget for the plugin"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel(f"Plugin: {self.METADATA['name']}"))
    return widget
```

## Example Plugins

Refer to these example plugins as starting points:

- `plugins/car_state_plugin.py`: Basic temporal data plugin
- `plugins/CarPosePlugin.py`: Spatial data plugin
- `plugins/path_view_plugin.py`: Complex spatial visualization
- `plugins/user_plugins/example_plugin.py`: User plugin template

## Troubleshooting

### Common Issues

1. **Plugin not loading**: Check your `plugin_class` assignment
2. **Missing signals**: Verify signal registration in `__init__`
3. **Data not showing**: Check the format of your returned data
4. **Errors during loading**: Look for missing dependencies

### Debugging Plugins

Enable debug logging to see detailed information about plugin loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The Debug Player plugin system allows for powerful extensions to the application's capabilities. By following this guide, you should be able to create your own plugins that seamlessly integrate with the Debug Player ecosystem.
