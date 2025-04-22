import os
import sys
from PySide6.QtCore import Slot
import importlib.util
from gui.custom_plot_widget import TemporalPlotWidget_plt, SpatialPlotWidget, TemporalPlotWidget_pg   
from core.config import temporal_signal_axes

class PlotManager:
    """
    PlotManager is the central coordinator for the Debug Player system.
    
    This class manages the flow of data between plugins (data providers) and plot widgets
    (data visualizers). It handles plugin registration, signal management, and plot updates.
    It serves as the mediator between all components of the system.
    
    The PlotManager:
    1. Loads and manages plugins that provide data signals
    2. Registers plots that visualize these signals
    3. Coordinates data requests from the UI and routes them to the appropriate plugins
    4. Updates plots with data from plugins when timestamps change
    """
    
    def __init__(self):
        """
        Initialize the PlotManager with empty registries for plugins, signals, and plots.
        
        This constructor creates the basic data structures needed for the PlotManager to
        coordinate data flow between plugins and plot widgets.
        """
        # List of all plot widgets that can subscribe to signals
        self.plots = []  
        
        # Dictionary mapping signal names to lists of plot widgets that display them
        # Format: {signal_name: [plot_widget1, plot_widget2, ...]}
        self.signals = {}  
        
        # Dictionary of plugin instances registered with the system
        # Format: {plugin_name: plugin_instance}
        self.plugins = {}  
        
        # Dictionary mapping signals to their source plugin and metadata
        # Format: {signal_name: {"plugin": plugin_name, "func": callable, "type": signal_type, ...}}
        self.signal_plugins = {}  
        
        # Tracks signal types for type checking and validation
        self.signal_types = {}  
        
        # Central widget instances for each visualization type
        # Note: In future versions, these could be dynamically created based on need
        self.temporal_plot_widget = TemporalPlotWidget_pg()  # For time-based signals
        self.spatial_plot_widget = SpatialPlotWidget()      # For spatial data (2D/3D)


    def register_plugin(self, plugin_name, plugin_instance):
        """
        Register a plugin that provides data for signals.
        
        Args:
            plugin_name (str): The name of the plugin to register.
            plugin_instance (object): The instance of the plugin to register.
            
        Raises:
            ValueError: If the plugin name is empty or already registered.
        """
        # Input validation
        if not plugin_name or not isinstance(plugin_name, str):
            raise ValueError(f"Invalid plugin name: {plugin_name}")
            
        if plugin_name in self.plugins:
            print(f"\033[93mWarning: Plugin '{plugin_name}' is already registered. Overwriting previous instance.\033[0m")
        
        # Register the plugin instance
        self.plugins[plugin_name] = plugin_instance
        
        # Import signal validation after ensuring the plugin is valid
        # This avoids circular imports
        from core.signal_validation import validate_signal_definition, check_required_signal_fields, SignalValidationError
        
        # Count registered signals for summary
        registered_signals = []
        validation_warnings = []

        # Register each signal provided by the plugin
        for signal, signal_info in plugin_instance.signals.items():
            try:
                # Validate and normalize the signal definition
                normalized_signal = validate_signal_definition(signal, signal_info, plugin_name)
                
                # Check for missing required fields
                missing_fields = check_required_signal_fields(signal, signal_info, plugin_name)
                if missing_fields:
                    validation_warnings.append(
                        f"Signal '{signal}' is missing required fields: {', '.join(missing_fields)}"
                    )
                
                # Store the normalized signal in signal_plugins
                self.signal_plugins[signal] = normalized_signal
                registered_signals.append(signal)
                
            except SignalValidationError as e:
                print(f"\033[95mError: {str(e)}\033[0m")
                continue

        # Print summary of registered signals
        print(f"\033[92m Registered signals for plugin \033[0m'{plugin_name}': {registered_signals}")
        
        # Print any validation warnings
        for warning in validation_warnings:
            print(f"\033[93mWarning: {warning}\033[0m")

    
    def load_plugins_from_directory(self, directory_path, plugin_args=None):
        """
        Dynamically discover and load plugins from the given directory.

        Args:
            directory_path (str): The path to the directory containing plugin files.
            plugin_args (dict, optional): Additional arguments to pass to each plugin during loading. Defaults to None.

        Returns:
            None
        """
        for filename in os.listdir(directory_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]  # Strip off the '.py'
                module_path = os.path.join(directory_path, filename)
                self.load_plugin_from_file(module_name, module_path, plugin_args)
    
    
    def load_plugin_from_file(self, module_name, file_path, plugin_args=None):
        """
        Load a plugin from a specified Python file.
        This method dynamically loads a Python module from the given file path,
        expects the module to define a `plugin_class` variable, and instantiates
        the plugin class with the provided arguments. The instantiated plugin
        is then registered using the module name.
        Args:
            module_name (str): The name to assign to the loaded module.
            file_path (str): The file path to the Python file containing the plugin.
            plugin_args (dict, optional): A dictionary of arguments to pass to the
                          plugin class constructor. Defaults to None.
        Raises:
            AttributeError: If the module does not have a `plugin_class` attribute.
        Example:
            load_plugin_from_file('example_plugin', '/path/to/plugin.py', {'arg1': 'value1'})
        """
        if plugin_args is None:
            plugin_args = {}  # Ensure there's a default empty argument dict
            # TODO: Allow loading different arguments for different plugins
            
        ### Creating a Module Specification-  returns a ModuleSpec object,
        # which contains all the information needed to load the module, such as its name, location, and loader.
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        # Creating a Module from the Specification- sets up the module's attributes and prepares it for execution.
        module = importlib.util.module_from_spec(spec)
        # Executing the Module - runs the module's code and fully initializes it
        spec.loader.exec_module(module)

        # Expect an explicit plugin_class variable in the module
        if hasattr(module, 'plugin_class'):
            plugin_class = module.plugin_class
            
            # Pass arguments when instantiating the plugin
            plugin_instance = plugin_class(**plugin_args)
            
            self.register_plugin(module_name, plugin_instance)
        else:
            print(f"No 'Plugin' class found in {module_name}")
           
                    
    def register_plot(self, signal):
        """
        Register a signal and assign it to the appropriate plot widget based on its type.  
        
        Args:
            signal (str): The name of the signal to plot.
        """
        signal_info = self.signal_plugins.get(signal) # Get the plugin info for the signal: plugin, func, type
        if not signal_info:
            print(f"\033[95mError: Signal '{signal}' not found.\033[0m")
            return

        signal_type = signal_info["type"]
        
        # Create the appropriate plot widget based on signal type
        if signal_type == "temporal":
            # Get the specified axes for the signal, or default to ["ax1"] if not specified
            plots = temporal_signal_axes.get(signal, ["plot1"])  
            for plot_name in plots:
                self.temporal_plot_widget.register_signal(signal, plot_name)            
        elif signal_type == "spatial":
            self.spatial_plot_widget.register_signal(signal)
        else:
            print(f"\033[93mWarning: Signal type '{signal_type}' is unknown. Using TemporalPlotWidget by default.\033[0m")
    
        # Also track the signal in self.signals for PlotManager's use
        if signal not in self.signals:
            self.signals[signal] = []
            
        # Assuming here that self.temporal_plot_widget or self.spatial_plot_widget should be the "plot" references
        if signal_type == "temporal":
            self.signals[signal].append(self.temporal_plot_widget)
        elif signal_type == "spatial":
            self.signals[signal].append(self.spatial_plot_widget)


    def request_data(self, timestamp):
        """
        Request new data for all signals at the given timestamp.

        This method iterates over all registered signals and fetches the 
        corresponding data from the associated plugins. If a plugin provides 
        data for a signal, it retrieves the data for the specified timestamp 
        and updates the signal with the new data.

        Args:
            timestamp (int): The timestamp for which to request data.
        """
        print(f"Requesting data for timestamp {timestamp}")
        for signal, plot_list in self.signals.items(): # Iterate over all registered signals
            # Fetch data for each signal from all plugins that provide it
            signal_info = self.signal_plugins.get(signal) # Get the plugin info for the signal
            if not signal_info:
                        print(f"\033[93mWarning: No plugin found for signal '{signal}'\033[0m")
                        continue
                    
            # Fetch the plugin instance for the signal
            plugin_name = signal_info["plugin"]
            plugin = self.plugins.get(plugin_name) # Get the plugin instance
            if plugin and plugin.has_signal(signal):
                # Fetch data for this signal at the given timestamp
                data = plugin.get_data_for_timestamp(signal, timestamp)

                # Update the correct plot widget
                if signal_info["type"] == "temporal":
                    # Send data to TemporalPlotWidget
                    self.temporal_plot_widget.update_data(signal, data, timestamp)
                elif signal_info["type"] == "spatial":
                    # Send data to SpatialPlotWidget
                    self.spatial_plot_widget.update_data(signal, data)
            else:
                print(f"\033[95mError: Plugin '{plugin_name}' for signal '{signal}' not found.\033[0m")

                        
    def assign_signal_to_plot(self, plot_widget, signal):
        """Assign a specific signal to an existing plot widget."""
        if signal not in self.signals:
            self.signals[signal] = []
        if plot_widget not in self.signals[signal]:
            self.signals[signal].append(plot_widget)
        print(f"Assigned '{signal}' to plot {plot_widget}.")

        
    def update_signal(self, signal, data, current_timestamp):
        """Broadcast the updated data to all subscribed plots."""
        if signal in self.signals:
            # print(f"Updating data for signal '{signal}': {data}")
            for plot in self.signals[signal]:
                plot.update_data(signal, data, current_timestamp)
        else:
            print(f"\033[95mError: Signal '{signal}' not found in registered signals.\033[0m")
    

    def remove_signal_from_plot(self, plot_widget, signal):
        """Remove a specific signal from a plot."""
        if signal in self.signals:
            if plot_widget in self.signals[signal]:
                self.signals[signal].remove(plot_widget)
                # Remove data associated with the signal from the plot
                plot_widget.data.pop(signal, None)        
                
                
    def toggle_signal_visibility(self, plot_widget, signal, visible):
        """Show or hide the signal in the given plot."""
        if visible:
            self.request_data_for_signal(signal, plot_widget)
        else:
            # Remove the signal's data from the plot without removing the signal itself
            plot_widget.data.pop(signal, None)
            plot_widget.plot_data()                