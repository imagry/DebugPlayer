import pyqtgraph as pg

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, signal_names):
        super().__init__()
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {}
        
    def update_data(self, signal_name, data):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            self.data[signal_name] = data
            self.plot_data()  # Re-plot with updated data        
            
            
    def plot_data(self):
        # TODO: can we have this as an interface and implement it in the plugin, at least partially.
        self.clear()
        for signal_name, data in self.data.items():
            if 'theta' in data and data['theta'] is not None:
                # Handle car pose with orientation (SE2)
                self.plot([data['x']], [data['y']], symbol='o', pen=None)
            else:
                # Handle regular 2D path (route)
                self.plot(data['x'], data['y'], pen=pg.mkPen('r'))  # Red line for route