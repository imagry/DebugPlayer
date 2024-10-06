class PlotManager:
    def __init__(self):
        self.plots = []  # List of all plots (subscribers)
        self.signals = {}  # Dictionary to manage signal subscriptions
        self.plugins = {}  # Plugin registry
        self.signal_plugins = {}  # To track which plugin provides which signal


    def register_plugin(self, plugin_name, plugin_instance):
        """Register a plugin that provides data for signals."""
        self.plugins[plugin_name] = plugin_instance
        # Track which plugin provides which signals
        for signal in plugin_instance.signals.keys():
            if signal not in self.signal_plugins:
                self.signal_plugins[signal] = []
            self.signal_plugins[signal].append(plugin_name)
        
    def register_plot(self, plot_widget):
        """Register a plot widget, auto-fetching the signals it subscribes to."""
        self.plots.append(plot_widget)
        for signal in plot_widget.signal_names:
            if signal not in self.signals:
                self.signals[signal] = []
            self.signals[signal].append(plot_widget)  # Subscribe the plot to this signal

    def update_signal(self, signal_name, data):
        """Broadcast the updated data to all subscribed plots."""
        # print(f"Broadcasting data for signal {signal_name}: x={data['x']}, y={data['y']}")
        if signal_name in self.signals:
            for plot in self.signals[signal_name]:
                plot.update_data(signal_name, data)
                
    def request_data(self, timestamp):
        """Request new data for all signals at the given timestamp."""
        print(f"Requesting data for timestamp {timestamp}")
        for signal, plot_list in self.signals.items():
            # Fetch data for each signal from all plugins that provide it
            for plugin_name in self.signal_plugins.get(signal, []):
                plugin = self.plugins[plugin_name]
                if plugin.has_signal(signal):
                    # Fetch data for this signal at the given timestamp
                    data = plugin.get_data_for_timestamp(signal, timestamp)
                    self.update_signal(signal, data)             