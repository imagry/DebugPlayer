import numpy as np
import math
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QMenu, QCheckBox, QHBoxLayout, QVBoxLayout  # Import QCheckBox from PySide6
from PySide6.QtCore import Qt, QObject, QEvent, QPointF
from PySide6.QtGui import QAction, QPolygonF, QBrush, QColor
from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsItem
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries
from gui.vehicle_object import VehicleObject
from gui.vehicle_config import VehicleConfigBase
from gui.vehicle_config import niro_ev2
from PySide6.QtGui import QPainter, QPen
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QObject, QEvent, QPointF


class TemporalPlotWidget_pg(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create three PlotWidgets
        self.plot1 = pg.PlotWidget()
        self.plot2 = pg.PlotWidget()
        self.plot3 = pg.PlotWidget()

        # Add the plots to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.plot1)
        layout.addWidget(self.plot2)
        layout.addWidget(self.plot3)
        self.setLayout(layout)

        # Initialize data store for each plot
        self.data_store = {
            "plot1": {},
            "plot2": {},
            "plot3": {},
        }

        # List to store registered signals
        self.signals = []

        # Dictionary to store plot lines per signal per plot
        # Now supports multiple plots per signal
        self.plot_lines = {}  # { signal_name: { plot_name: PlotDataItem } }


        # Current timestamp indicator
        self.timestamp_line = {
            "plot1": None,
            "plot2": None,
            "plot3": None,
        }

        # Add legends to plots
        self.legend_items = {
            "plot1": self.plot1.addLegend(),
            "plot2": self.plot2.addLegend(),
            "plot3": self.plot3.addLegend(),
        }
        
        # Initialize a color cycle
        self.color_cycle = self.get_color_cycle()

    def get_color_cycle(self):
        """Returns a generator that cycles through a list of colors."""
        colors = [
            'r', 'g', 'b', 'c', 'm', 'y', 'k',  # Basic colors
            '#e6194b', '#3cb44b', '#ffe119', '#4363d8',  # More colors
            '#f58231', '#911eb4', '#46f0f0', '#f032e6',
            '#bcf60c', '#fabebe', '#008080', '#e6beff',
            '#9a6324', '#fffac8', '#800000', '#aaffc3',
            '#808000', '#ffd8b1', '#000075', '#808080'
        ]
        while True:
            for color in colors:
                yield color
                
    def register_signal(self, signal, plot_name="plot1", color = None):
        """
        Register a signal to be displayed on one or more plots based on the mapping.
        """
        
        
        if plot_name in self.data_store:
            # Initialize data storage for the signal in the specified plot
            self.data_store[plot_name][signal] = {
                "timestamps": [],
                "values": []
            }
            
            # Add signal to signals list if not already present
            if signal not in self.signals:
                self.signals.append(signal)
        
            # Assign a color if not specified
            if color is None:
                color = next(self.color_cycle)  
        
            # Create a pen with the specified color
            pen = pg.mkPen(color=color, width=2)
            
            # Initialize plot lines for this signal if not already
            if signal not in self.plot_lines:
                self.plot_lines[signal] = {}
    
    
            # Plot the signal on the specified plot and store the line for future updates
            plot_widget = getattr(self, plot_name)
            line = plot_widget.plot([], [], name=signal, pen=pen)
            self.plot_lines[signal][plot_name] = line  # Store line under signal and plot

            # Debug message
            print(f"\033[38;5;214mAdded signal\033[0m '{signal}' to \033[93m data_store \033[0m in plot '{plot_name}'")
        else:
            print(f"Error(register_signal): Plot '{plot_name}' not found in data_store.")

    def update_data(self, signal, data, current_timestamp):
        """
        Update data for a specific signal and timestamp.
        """
        # Ensure data is in a compatible format
        data_value = data.to_numpy().item() if hasattr(data, 'to_numpy') else data

        if data_value is not None:
        # Update data in each plot where the signal is registered
            for plot_name in self.plot_lines.get(signal, {}):
                # Get the data store for this signal and plot
                plot_data = self.data_store[plot_name][signal] 

                # Append the current timestamp and data value to this signal's list
                plot_data["timestamps"].append(current_timestamp)
                plot_data["values"].append(data_value)

                # Update the line data for the signal
                line = self.plot_lines[signal][plot_name]
                line.setData(plot_data["timestamps"], plot_data["values"])

                # Update or create the timestamp line
                if self.timestamp_line[plot_name] is None:
                    self.timestamp_line[plot_name] = pg.InfiniteLine(pos=current_timestamp, angle=90, pen=pg.mkPen('r', style=Qt.DashLine))
                    getattr(self, plot_name).addItem(self.timestamp_line[plot_name])
                else:
                    self.timestamp_line[plot_name].setValue(current_timestamp)

                # Auto-update zoom if desired
                self.auto_update_zoom()
                
            else:
                print(f"Warning: Received empty or None data for signal {signal}")

    def auto_update_zoom(self):
        """Auto-update zoom to fit the data."""
        for plot in [self.plot1, self.plot2, self.plot3]:
            plot.enableAutoRange()
            
class SpatialPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up plot widget for displaying spatial data
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        # Dictionaries to store data and plot elements for each signal
        self.data_store = {}
        self.plot_elements = {}
        self.signals = []  # Track registered signals

        # Initialize vehicle representation
        self.vehicle = VehicleObject(config=niro_ev2)
        self.plot_widget.addItem(self.vehicle)  # Add vehicle to plot                                      


    def register_signal(self, signal):               
        """
        Register spatial signals, initializing plot elements.
        """
        
        
                # Append signal to self.signals if not already present
        
        # Append signal to self.signals if not already present
        if signal not in self.signals: 
            self.signals.append(signal)
            
        # Initialize an empty dictionary for this signal's data
        self.data_store[signal] = {"x": [], "y": [], "theta": None}  # Adjust as needed
        
        # Create plot elements based on signal type
        if signal == "route":
            self.plot_elements[signal] = self.plot_widget.plot(pen=pg.mkPen('r', width=2))
        elif signal == "car_pose(t)":
            self.plot_elements[signal] = pg.ScatterPlotItem()
            self.plot_widget.addItem(self.plot_elements[signal])
        elif signal == "path_in_world_coordinates(t)":
            self.plot_elements[signal] = pg.PlotDataItem(pen=None, symbol='o', symbolBrush='g', symbolSize=5)
            self.plot_widget.addItem(self.plot_elements[signal])
            
        print(f"\033[94mRegistered spatial signal\033[0m: {signal}")

        
    def update_data(self, signal, data):
        """Update data for spatial signals."""
        if signal not in self.data_store:
            print(f"Error(update_data): Signal '{signal}' not registered.")
            return
        
        # Update data store
        # Handle data as either dictionary or ndarray
        if isinstance(data, dict):
            self.data_store[signal]["x"] = data.get("x", [])
            self.data_store[signal]["y"] = data.get("y", [])
            self.data_store[signal]["theta"] = data.get("theta")  # Only for 'car_pose(t)', if applicable
        elif isinstance(data, np.ndarray):
             # Assuming ndarray format: [[x1, y1], [x2, y2], ...]
            if data.shape[1] >= 2:  # Check to ensure we have at least two columns
                self.data_store[signal]["x"] = data[:, 0]
                self.data_store[signal]["y"] = data[:, 1]
                # Optional: Set theta if provided as a third column in ndarray
                if data.shape[1] > 2:
                    self.data_store[signal]["theta"] = data[:, 2]

        # Update plot elements
        if signal in self.plot_elements:
            if signal == "route" or signal == "path_in_world_coordinates(t)":
                self.plot_elements[signal].setData(self.data_store[signal]["x"], self.data_store[signal]["y"])
            elif signal == "car_pose(t)":
                # Update the vehicle position and orientation
                self.vehicle.set_pose_at_front_axle(
                    self.data_store[signal]["x"], 
                    self.data_store[signal]["y"], 
                    math.radians(self.data_store[signal]["theta"])
                )
            
        self.plot_widget.repaint()
        
        
    def plot_data(self):
        """Plot data for all registered signals based on current data."""
        for signal in self.plot_elements.keys():
            if signal in self.data_store:
                self.update_data(signal, self.data_store[signal])
  
    
    def toggle_signal_visibility(self, signal, visible):
        """
        Allows toggling visibility for each signal.        
        """
        if signal in self.plot_elements:
            self.plot_elements[signal].setVisible(visible)
            print(f"Toggled visibility for {signal} to {visible}")


    def show_custom_context_menu(self, global_pos):
        """Show a custom context menu with signal visibility options."""
        menu = QMenu(self)
        signals_menu = QMenu("Signals", menu)

        for signal in self.data_store.keys():
            action = QAction(signal, self)
            action.setCheckable(True)
            action.setChecked(self.plot_elements[signal].isVisible())
            action.triggered.connect(lambda checked, s=signal: self.toggle_signal_visibility(s, checked))
            signals_menu.addAction(action)

        menu.addMenu(signals_menu)
        menu.exec(global_pos)


class TemporalPlotWidget_plt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize Matplotlib figure and canvas
        self.figure , (self.ax1, self.ax2, self.ax3) = plt.subplots(3,1,figsize = (8,6))
        self.canvas = FigureCanvas(self.figure)
        
        # Layout setup for embedding the Matplotlib canvas
        layout = QVBoxLayout() # Vertical layout
        layout.addWidget(self.canvas) # Add the Matplotlib canvas to the layout
        self.setLayout(layout) # Set the layout for the widget
        
        # Dictionary to store data for each subplot        
        # self.data_store = {
        #         "ax1": {"timestamps": [], "values": {}},
        #         "ax2": {"timestamps": [], "values": {}},
        #         "ax3": {"timestamps": [], "values": {}},
        
        # }   
        self.data_store = {
            "ax1": {},
            "ax2": {},
            "ax3": {},
        }
        # Initialize list to store registered signal names
        self.signals = []
        
        # current timestamp indicator
        self.timestamp_line = {
            "ax1": None,
            "ax2": None,
            "ax3": None,
        }
        
        # Legend visibility control
        self.legend_lines = {}
                                                            
            
    def register_signal(self, signal, ax_name="ax1"):
        """
        Register a signal to be displayed on a specific subplot (ax1, ax2, or ax3).
        """
        
        if ax_name in self.data_store: # Check if the subplot exists

            # Initialize timestamps and values for this signal in the specified axis
            self.data_store[ax_name][signal] = {
                "timestamps": [],
                "values": []
            }
                                            
            # add signal to signals if not already present
            if signal not in self.signals:
                self.signals.append(signal)
                                    
            # Plot the signal on the specified axis and store the line for toggling visibility
            line, = getattr(self, ax_name).plot([], [], label=signal)
            self.legend_lines[signal] = line
            
            # update legened for subplot
            getattr(self, ax_name).legend(loc="upper right", fancybox=True, shadow=True) # Add the legend to the subplot
            self.canvas.draw() # Redraw the canvas

            # Debug message
            print(f"\033[38;5;214mAdded signal\033[0m '{signal}' to \033[94m data_store in subplot \033[0m '{ax_name}'") # Debug output
        else:
            print(f"\033[95mError(register_signal): Subplot '{ax_name}' not found in data_store.\033[0m")
        
                      
    def update_data(self, signal, data, current_timestamp):
        """
        Update data for a specific signal and timestamp:
        # Iterate over all subplots: ax1, ax2, ax3 and their data. For 
        # each subplot, we have a dictionary with timestamps and values. 
        # Then we iterate over the dictionary items to get the subplot 
        # name and data so we can append the current timestamp and data for the signal.
        """
                   
        # Ensure data is in a compatible format
        data_value = data.to_numpy().item() if hasattr(data, 'to_numpy') else data

                
        for ax_name, ax_data in self.data_store.items(): # Iterate over all subplots
             # Initialize 'timestamps' and 'values' if not present
            if "timestamps" not in ax_data:
                ax_data["timestamps"] = []
            if "values" not in ax_data:
                ax_data["values"] = {}
            
            
            if signal in ax_data:# Check if the signal is registered for this subplot
                if data_value is not None: 
                    # Append the current timestamp and data value to this signal's list
                    ax_data[signal]["timestamps"].append(current_timestamp)
                    ax_data[signal]["values"].append(data_value)                                
                    
                    # Update the line data for the signal
                    line = self.legend_lines[signal]
                    line.set_xdata(ax_data[signal]["timestamps"])
                    line.set_ydata(ax_data[signal]["values"])
                    
                    # Set reasonable axis limits to avoid singular matrix issues
                    # self.ensure_axis_limits(ax_name)
                    
                    # Update or create the timestamp line
                    # if self.timestamp_line[ax_name] is None:
                    #     self.timestamp_line[ax_name] = getattr(self, ax_name).axvline(current_timestamp, color="red", linestyle="--")
                    # else:
                    #     self.timestamp_line[ax_name].set_xdata([current_timestamp, current_timestamp])
                        
                    # Update the figure
                    self.canvas.draw()
                    self.auto_update_zoom()  # Auto-update zoom


                else:
                    print(f"\033[93mWarning: Received empty or None data for signal {signal}\033[0m")            

    def auto_update_zoom(self):
        """Auto-update zoom to fit the data."""
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw()
        
    def ensure_axis_limits(self, ax_name):
        """
        Adjust the y-axis limits for a given subplot based on the values of the signals
        plotted on that axis, with safeguards against singular matrix errors.
        """
        if ax_name not in self.data_store or "values" not in self.data_store[ax_name]:
            print(f"Error: Axis '{ax_name}' not found or 'values' key missing in data_store.")
            return

        all_values = []
        for signal, signal_data in self.data_store[ax_name]["values"].items():
            if signal_data:  # Only include non-empty data
                all_values.extend(signal_data)

        if all_values:
            min_val, max_val = min(all_values), max(all_values)
            
            # Apply buffer to avoid singular matrix
            if max_val - min_val < 1e-3:
                buffer = 0.1 if min_val == 0 else 0.05 * abs(min_val)
                min_val -= buffer
                max_val += buffer
            else:
                buffer = 0.05 * (max_val - min_val)
                min_val -= buffer
                max_val += buffer

            getattr(self, ax_name).set_ylim(min_val, max_val)
            self.canvas.draw()
        else:
            print(f"Warning: No data available for setting axis limits on '{ax_name}'.")


    def toggle_signal_visibility(self, signal, visible):
        """
        Toggle the visibility of a signal.
        """
        if signal in self.legend_lines:
            self.legend_lines[signal].set_visible(visible)
            self.canvas.draw()
            
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
        
    
class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
            
class BasePlotWidget(pg.PlotWidget):
    def __init__(self, signals, default_visible_signals=[], parent = None):
        super().__init__(parent)
        self.signals = signals
        self.default_visible_signals = default_visible_signals
        self.data_store = {signal: {'timestamps':[], 'values':[] }for signal in self.signals} 
        self.visibility_control = {signal: False for signal in signals}
        self.plot_widget = pg.PlotWidget()
        self.curves = {signal: self.plot_widget.plot(pen = pg.mkPen(color))
                       for signal , color in zip(self.signals, ["r", "g", "b", "y", "c"])}
        self.legend = self.plot_widget.addLegend(offset = (10,10))
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        
        for signal in default_visible_signals:
            if signal in signals:
                self.visibility_control[signal] = True
                self.register_signal(signal)
            else:
                print(f"Error: Signal '{signal}' not found in signals.")
                
    def register_signal(self, signal):
        if signal in self.curves:
            return
        curve = pg.PlotDataItem()
        set.plot_widget.addItem(curve)
        self.curves[signal] = curve
        self.legned.addItem(curve, signal)
        print(f"\033[38;5;214mAdded signal\033[0m {signal} to plot and legend")
        
    def update_data(self, signal, data, current_timestamp):
        if signal in self.signals:
            if data is not None:
                self.data_store[signal]['timestamps'].append(current_timestamp)
                self.data_store[signal]['values'].append(data)
                self.plot_data()
            else:
                print(f"Warning: Received empty or None data for signal {signal}")
        else:   
            print(f"Error: Signal '{signal}' not found in signals.")
            
            
            
    def plot_data(self):
        for signal, curve in self.curves.items():
            data = self.data_store.get(signal)
            if data and len(data['timestamps']) > 0:
                timestamps = np.array(data['timestamps']).flatten()
                values = np.array(data['values']).flatten()
                curve.setData(timestamps, values)
            else:
                curve.clear()
                
    def toggle_signal_visibility(self, signal, visible):
        if signal in self.curves:
            self.curves[signal].setVisible(visible)
            print(f"Toggled visibility for {signal} to {visible}")
        else:
            print(f"Error: Signal '{signal}' not found in curves.")
            
    def show_custom_context_menu(self, global_pos):
        menu = QMenu(self)
        signals_menu = QMenu("Signals", menu)
        
        for signal in self.signals:
            action = QAction(signal, signals_menu)
            action.setCheckable(True)
            action.setChecked(self.visibility_control.get(signal, False))
            action.triggered.connect(lambda checked, s=signal: self.toggle_signal_visibility(s, checked))
            signals_menu.addAction(action)
            
        menu.addMenu(signals_menu)
        menu.exec(global_pos)
