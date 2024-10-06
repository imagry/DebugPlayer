import pyqtgraph as pg

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, signal_names):
        super().__init__()
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {}
        
        #         super().__init__()
        # self.signal_names = signal_names  # This plot can subscribe to multiple signals
        # self.layout = QVBoxLayout(self)
        # self.plot_widget = pg.PlotWidget()  # Using pyqtgraph.PlotWidget
        # self.layout.addWidget(self.plot_widget)
        # self.plot_widget.showGrid(x=True, y=True)Z
        # self.data = {}
        
    def update_data(self, signal_name, data):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            self.data[signal_name] = data
            self.plot_data()  # Re-plot with updated data        
            
            
    def plot_data(self):
        # TODO: can we have this as an interface and implement it in the plugin, at least partially.
        self.clear()
        for signal_name, data in self.data.items():
            if signal_name == 'car_pose(t)':
                # Handle car pose with orientation (SE2)
                self.plot([data['x']], [data['y']], symbol='o', pen=None, symbolBrush='m')
            elif signal_name == 'route':
                # Handle regular 2D path (route)
                self.plot(data['x'], data['y'], pen=pg.mkPen('r')) #, symbol='o', symbolBrush='r')
            elif signal_name == 'path_in_world_coordinates(t)':
                # Handle regular 2D path (route)
                self.plot(data[:,0],data[:,1], pen = pg.mkPen('g'), symbol='o', symbolBrush='g', symbolSize=5)
            elif signal_name == 'car_pose_at_path_timestamp(t)':
                # Handle car pose with orientation (SE2)
                self.plot([data[0,2]], [data[1,2]], symbol='p', pen=None, symbolBrush='g', symbolSize=10)