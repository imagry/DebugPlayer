import os
import sys
from PySide6.QtCore import Slot
import importlib.util
from gui.custom_plot_widget import TemporalPlotWidget, SpatialPlotWidget

class PlotManager:
    def __init__(self):
        self.plots = []  # List of all plots (subscribers)
        self.signals = {}  # Dictionary to manage signal subscriptions
        self.plugins = {}  # Plugin registry
        self.signal_plugins = {}  # To track which plugin provides which signal
        self.signal_types = {}  # To track the type of data for each signal

    def register_plugin(self, plugin_name, plugin_instance):
        """
        Register a plugin that provides data for signals.
        
        Args:
            plugin_name (str): The name of the plugin to register.
            plugin_instance (object): The instance of the plugin to register.
        """
        self.plugins[plugin_name] = plugin_instance

        for signal_name, signal_info in plugin_instance.signals.items():
            signal_func = signal_info.get("func")
            signal_type = signal_info.get("type", "temporal")  # Default to "temporal" if type is missing.

            if not callable(signal_func):
                print(f"Error: Signal '{signal_name}' in plugin '{plugin_name}' does not have a valid method.")
                continue

            if signal_type not in ["temporal", "spatial"]:
                print(f"Warning: Signal '{signal_name}' in plugin '{plugin_name}' has an unknown type '{signal_type}'. Defaulting to 'temporal'.")
                signal_type = "temporal"

            # Store the signal, its function, and type in self.signal_plugins.
            self.signal_plugins[signal_name] = {
                "plugin": plugin_name,
                "func": signal_func,
                "type": signal_type
            }

        print(f"Registered signals for plugin '{plugin_name}': {list(plugin_instance.signals.keys())}")

    
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
           
                    
    def register_plot(self, signal_name):
        """
        Register a plot widget for a given signal based on its type.
        
        Args:
            signal_name (str): The name of the signal to plot.
        """
        signal_info = self.signal_plugins.get(signal_name)
        if not signal_info:
            print(f"Error: Signal '{signal_name}' not found.")
            return

        signal_type = signal_info["type"]
        plugin_name = signal_info["plugin"]

        # Create the appropriate plot widget based on signal type
        if signal_type == "temporal":
            plot_widget = TemporalPlotWidget()
        elif signal_type == "spatial":
            plot_widget = SpatialPlotWidget(signal_names=[signal_name])
        else:
            print(f"Warning: Signal type '{signal_type}' is unknown. Using TemporalPlotWidget by default.")
            plot_widget = TemporalPlotWidget()

        # Register the signal with the appropriate widget and ensure it's added to self.signals
        self.assign_signal_to_plot(plot_widget, signal_name)
        self.plots.append(plot_widget)
        plot_widget.register_signal(signal_name)
        print(f"Registered '{signal_name}' (type: '{signal_type}') from plugin '{plugin_name}' to plot.")

    
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
        for signal_name, plot_list in self.signals.items():
            # Fetch data for each signal from all plugins that provide it
            signal_info = self.signal_plugins.get(signal_name)
            if not signal_info:
                        print(f"Warning: No plugin found for signal '{signal_name}'")
                        continue
                    
            plugin_name = signal_info["plugin"]
            plugin = self.plugins.get(plugin_name)
            if plugin and plugin.has_signal(signal_name):
                # Fetch data for this signal at the given timestamp
                data = plugin.get_data_for_timestamp(signal_name, timestamp)
                self.update_signal(signal_name, data, timestamp)
            else:
                print(f"Error: Plugin '{plugin_name}' for signal '{signal_name}' not found.")   
                
                        
    def assign_signal_to_plot(self, plot_widget, signal_name):
        """
        Assign a specific signal to a plot.

        Parameters:
        plot_widget (object): The plot widget to which the signal will be assigned.
        signal_name (str): The name of the signal to be assigned.
        """
        if signal_name not in self.signals:
            self.signals[signal_name] = []
        if plot_widget not in self.signals[signal_name]:
            self.signals[signal_name].append(plot_widget)
        print(f"Assigned '{signal_name}' to plot {plot_widget}.")
    
    
    def update_signal(self, signal_name, data, current_timestamp):
        """Broadcast the updated data to all subscribed plots."""
        if signal_name in self.signals:
            print(f"Updating data for signal '{signal_name}': {data}")
            for plot in self.signals[signal_name]:
                plot.update_data(signal_name, data, current_timestamp)
        else:
            print(f"Error: Signal '{signal_name}' not found in registered signals.")
    
    

    def remove_signal_from_plot(self, plot_widget, signal_name):
        """Remove a specific signal from a plot."""
        if signal_name in self.signals:
            if plot_widget in self.signals[signal_name]:
                self.signals[signal_name].remove(plot_widget)
                # Remove data associated with the signal from the plot
                plot_widget.data.pop(signal_name, None)        
                
    def toggle_signal_visibility(self, plot_widget, signal_name, visible):
        """Show or hide the signal in the given plot."""
        if visible:
            self.request_data_for_signal(signal_name, plot_widget)
        else:
            # Remove the signal's data from the plot without removing the signal itself
            plot_widget.data.pop(signal_name, None)
            plot_widget.plot_data()                