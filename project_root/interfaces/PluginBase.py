from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

class PluginBase(ABC):
    """
    Abstract base class for all Debug Player plugins.
    
    This class defines the required interface that all plugins must implement.
    Plugins are responsible for loading and providing access to data from various
    sources, and exposing that data through signals that can be visualized by the UI.
    
    The plugin system follows these key principles:
    1. Each plugin handles a specific type of data source
    2. Plugins expose signals that provide data for visualization
    3. Plugins are dynamically discovered and loaded by the PlotManager
    4. All plugins must implement the methods defined in this interface
    
    To create a custom plugin:
    1. Create a new class that inherits from PluginBase
    2. Implement all abstract methods
    3. Define signals in the self.signals dictionary
    4. Export the plugin class via the plugin_class variable
    
    Example implementation:
    ```python
    class MyPlugin(PluginBase):
        def __init__(self, file_path):
            super().__init__(file_path)
            # Initialize your data sources here
            # Define your signals dictionary
            self.signals = {
                "my_signal": {
                    "func": self.get_my_data,
                    "type": "temporal"
                }
            }
            
        def has_signal(self, signal):
            return signal in self.signals
            
        def get_data_for_timestamp(self, signal, timestamp):
            # Return data for the specific signal and timestamp
            pass
        
    # Export the plugin class (REQUIRED)
    plugin_class = MyPlugin
    ```
    """
    
    @abstractmethod
    def __init__(self, file_path: Optional[str] = None) -> None:
        """
        Initialize the plugin with the given file path.

        This method should set up any data structures needed for the plugin,
        load data from the file path if applicable, and define the signals
        that this plugin provides.

        Parameters:
        -----------
        file_path : Optional[str]
            The path to the data file or directory containing the data.
            This is passed to the plugin by the PlotManager during loading.
            If None, the plugin should use mock data for development/testing.
        """
        self.file_path = file_path
        # Flag to indicate if we're using mock data
        self.use_mock_data = (file_path is None)
        
        # The signals dictionary is a key component of every plugin.
        # It maps signal names to dictionaries containing metadata about each signal.
        # Each signal definition must include at minimum:
        # - func: A callable that returns data for this signal
        # - type: The signal type (e.g., "temporal", "spatial")
        # 
        # Example:
        # self.signals = {
        #     "car_pose": {
        #         "func": self.get_car_pose,
        #         "type": "spatial",
        #         "description": "Vehicle position and orientation"
        #     }
        # }
        self.signals: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    def has_signal(self, signal: str) -> bool:
        """
        Check if this plugin provides the requested signal.

        This method is called by the PlotManager to determine if this plugin
        can provide data for a specific signal.

        Parameters:
        -----------
        signal : str
            The name of the signal to check for.

        Returns:
        --------
        bool
            True if this plugin provides the signal, False otherwise.
        """
        pass

    @abstractmethod
    def get_data_for_timestamp(self, signal: str, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a specific signal and timestamp.

        This method is called by the PlotManager when it needs to update
        the plot widgets with new data, typically in response to a timestamp
        change from the UI.

        Parameters:
        -----------
        signal : str
            The name of the signal to fetch data for.
            This should be a key in the self.signals dictionary.
            
        timestamp : float
            The timestamp to fetch data for, in milliseconds.
            This allows the plugin to provide time-specific data.

        Returns:
        --------
        Optional[Dict[str, Any]]
            A dictionary containing the data for the signal at the specified timestamp.
            The format of this dictionary depends on the signal type:
            - For temporal signals: {"value": value} or {"values": [v1, v2, ...]}
            - For spatial signals: {"x": x_values, "y": y_values, (optional) "theta": orientation}
            - Return None if the signal is not found or data is not available
        """
        pass