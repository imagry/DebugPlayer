import pyqtgraph as pg
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QWidget, QMenu  # Import QCheckBox from PySide6
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QAction 

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, signal_names, default_visible_signals=[]):
        super().__init__(viewBox=CustomViewBox(self))  # Use CustomViewBox for mouse interactions
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {}  # Dictionary to store data for multiple signals
        self.plot_curves = {}  # Track plot curves (signal name -> PlotCurveItem)
        self.visibility_control = {signal: False for signal in signal_names}  # Visibility state for each signal
        self.legend = self.addLegend(offset=(10, 10))  # Add a legend to the plot with default position

        # Initialize default visible signals
        for signal in default_visible_signals:
            if signal in signal_names:
                self.visibility_control[signal] = True
                self.add_signal(signal)

    def update_data(self, signal_name, data):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            if data is not None and len(data) > 0:
                self.data[signal_name] = data
                if signal_name not in self.plot_curves:
                    self.add_signal(signal_name)  # Ensure the signal is added to the plot
                self.plot_data()  # Re-plot with updated data for all signals
            else:
                print(f"Warning: Received empty or None data for signal {signal_name}")

    def plot_data(self):
        """Plot data for all subscribed signals based on visibility control."""
        for signal_name, curve in self.plot_curves.items():
            if self.visibility_control.get(signal_name, False):
                data = self.data.get(signal_name)
                if data is not None and len(data) > 0:
                    try:
                        if signal_name == 'car_pose(t)':
                            # Handle car pose with orientation (SE2) as a single marker
                            # print(f"Plotting car_pose(t) with data: {data}")  # Debug output
                            curve.setData([data['x']], [data['y']], pen=None, symbol='o', symbolBrush='m', symbolSize=10)
                        elif signal_name == 'route':
                            # Handle regular 2D path (route) as a line
                            # print(f"Plotting route with data: {data}")  # Debug output
                            curve.setData(data['x'], data['y'], pen=pg.mkPen('r'))
                        elif signal_name == 'path_in_world_coordinates(t)':
                            # Handle path in world coordinates as scatter plot
                            # print(f"Plotting path_in_world_coordinates(t) with data: {data}")  # Debug output
                            if isinstance(data, (list, tuple)) and len(data) > 1 and isinstance(data[0], (list, tuple)):
                                data = pg.np.array(data)  # Ensure data is numpy array if needed
                            curve.setData(data[:, 0], data[:, 1], pen=None, symbol='o', symbolBrush='g', symbolSize=5)
                        elif signal_name == 'car_pose_at_path_timestamp(t)':
                            # Handle car pose at path timestamp as a single marker
                            # print(f"Plotting car_pose_at_path_timestamp(t) with data: {data}")  # Debug output
                            # curve.setData([data[0]], [data[1]], pen=None, symbol='p', symbolBrush='g', symbolSize=10)
                            pass
                    except Exception as e:
                        print(f"Error plotting {signal_name}: {e}")
            else:
                curve.clear()  # Clear the data if the signal is not visible

    def add_signal(self, signal_name):
        """Add a signal to the plot and the legend."""
        if signal_name in self.plot_curves:
            return  # Signal already exists

        curve = pg.PlotDataItem()  # Create a plot data item for the signal
        self.addItem(curve)  # Add the curve to the plot
        self.plot_curves[signal_name] = curve
        self.legend.addItem(curve, signal_name)  # Add the curve to the legend
        print(f"Added signal {signal_name} to plot and legend")  # Debug output

    def toggle_signal_visibility(self, signal_name, visible):
        """Toggle the visibility of the signal."""
        self.visibility_control[signal_name] = visible
        print(f"Toggled visibility for {signal_name} to {visible}")  # Debug output
        self.plot_data()  # Re-plot to update visibility

    def show_custom_context_menu(self, global_pos):
        """Show a custom context menu with signal visibility options."""
        menu = QMenu(self)
        signals_menu = QMenu("Signals", menu)

        for signal_name in self.signal_names:
            action = QAction(signal_name, signals_menu)
            action.setCheckable(True)
            action.setChecked(self.visibility_control.get(signal_name, False))
            action.triggered.connect(lambda checked, s=signal_name: self.toggle_signal_visibility(s, checked))
            signals_menu.addAction(action)

        menu.addMenu(signals_menu)
        menu.exec(global_pos)



class CustomViewBox(pg.ViewBox):
    def __init__(self, parent_plot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_plot = parent_plot
        self.setMenuEnabled(False)  # Disable default context menu


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            print("Setting PanMode with Middle Button")
            self.setMouseMode(pg.ViewBox.PanMode)
        elif event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.ControlModifier:
            print("Setting RectMode with Ctrl + Left Button")
            self.setMouseMode(pg.ViewBox.RectMode)
            self.setAspectLocked(True)
        super().mousePressEvent(event)  # Call the parent method to maintain default behaviors

    def contextMenuEvent(self, event):
        """Handle right-click event to show custom context menu."""
        event.accept()  # Accept the event to prevent default handling
        self.parent_plot.show_custom_context_menu(event.screenPos())
        
        
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