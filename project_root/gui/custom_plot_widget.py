import pyqtgraph as pg
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QWidget  # Import QCheckBox from PySide6


class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, signal_names):
        super().__init__()
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {} # Dictionary to store data for multiple signals
        self.legend_items = {}  # Track legend items (signal name -> checkbox)
        self.legend = self.addLegend(offset=(10, 10))  # Add a legend to the plot with default position
        self.visibility_control = {}  # Dictionary to control the visibility of signals

               
    def update_data(self, signal_name, data):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            self.data[signal_name] = data
            if signal_name not in self.legend_items:
                self.add_signal_to_legend(signal_name)  # Ensure legend item exists
            self.plot_data()  # Re-plot with updated data for all signals            
            
            
    def plot_data(self):
        """Plot data for all subscribed signals."""
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


    def add_signal_to_legend(self, signal_name):
        """Add the signal to the legend with the actual plot curve."""
        if signal_name in self.legend_items:
            return  # Signal already in the legend

        # Create a plot curve for the signal (it will be updated later in plot_data)
        curve = pg.PlotCurveItem()  # Placeholder item until data is plotted
        self.addItem(curve)  # Add the curve to the plot (for later updates)
        self.legend.addItem(curve, signal_name)  # Add the curve to the legend
        self.legend_items[signal_name] = curve
        self.visibility_control[signal_name] = True  # Set default visibility to True

    def toggle_signal_visibility(self, signal_name, visible):
        """Toggle the visibility of the signal based on checkbox control."""
        self.visibility_control[signal_name] = visible
        self.plot_data()  # Re-plot to update visibility
        
        
        # # Create a custom checkbox for the legend
        # checkbox = QCheckBox(signal_name)
        # checkbox.setChecked(True)  # Signal visible by default

        # # # Add the checkbox to the legend (assuming self.legend_layout exists)
        # self.legend_layout.addWidget(checkbox)
        # self.legend_items[signal_name] = checkbox
        
        #  # Add the checkbox to the legend
        # legend_item_widget = QWidget()
        # layout = QHBoxLayout()
        # layout.addWidget(checkbox)
        # legend_item_widget.setLayout(layout)

        # # Add the checkbox to the plot's legend
        # self.legend.addItem(None, legend_item_widget)
        # self.legend_items[signal_name] = checkbox
        
        
        # Connect checkbox state change to re-plotting the data
        # checkbox.stateChanged.connect(self.plot_data)
                    
    # TODO: Import some how the plotting data instriuctions from the plugin and/or from the user / plot manager
    # so we don't have to have all these custom plotting instructions here.
    # This is a very simple example of how to plot different signals. 
    # A more complex version would be to have a dictionary of functions that plot each signal type.
    # Then we could define a function that maps each signal to its plotting function.
    # This way, we could have a generic plot function that just calls the appropriate plotting function for each signal.
    # The plotting functions would be defined in the plugin for each signal type.
    # This would make the plot widget more generic and easier to extend.
    # This is a good example of the open/closed principle in action.
    # We can easily add new signal types by just adding new plotting functions to the dictionary.
    # This way, we don't have to modify the plot widget class every time we add a new signal type.
    # We can just define a new plotting function in the plugin and add it to the dictionary.
    # This makes the plot widget class more reusable and easier to maintain.
    # We could also define a generic plotting function in the plugin that takes a signal name and data as arguments.
    # This function would call the appropriate plotting function based on the signal name.
    # This would further simplify the plot widget class and make it easier to extend.
    # This is a good example of the single responsibility principle in action.
    # Each class should have a single responsibility, and the plotting logic should be encapsulated in the plugin.
    # This way, the plot widget class can focus on managing the plot and handling user interactions,
    # while the plugin class can focus on fetching and processing data for each signal type.
    # This separation of concerns makes the code easier to understand, test, and maintain.
    # We could also define a base class for all plugins that provides common functionality for fetching and processing data.
    # This base class could define abstract methods for fetching data for each signal type,
    # which would be implemented by concrete plugin classes.
    # This would further simplify the plugin classes and make it easier to add new signal types.
    # This is a good example of the interface segregation principle in action.
    # Each class should define an interface that contains only the methods it needs to implement,
    # rather than a single monolithic interface that contains all possible methods.
    # This makes the code more modular and flexible, as each class can implement only the methods it needs to.
    # We could also define a separate class