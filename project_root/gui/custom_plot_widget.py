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
from PySide6.QtGui import QPainter
import pandas as pd
import polars as pl

class SpatialPlotWidget(QWidget):
    def __init__(self, signal_names, default_visible_signals=[], parent=None):
        super().__init__(parent)  # Use CustomViewBox for mouse interactions
        
        # Create a plot widget and set it up for spatial data
        self.plot_widget = pg.PlotWidget(viewBox=CustomViewBox(self))  # Use CustomViewBox for mouse interactions
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {}  # Dictionary to store data for multiple signals
        self.plot_curves = {}  # Track plot curves (signal name -> PlotCurveItem)
        self.visibility_control = {signal: False for signal in signal_names}  # Visibility state for each signal
        self.legend = self.plot_widget.addLegend(offset=(10, 10))  # Add a legend to the plot with default position
        self.rect_items = {}  # Track custom polygon items for car_pose(t)
        self.vehicle = VehicleObject(config=niro_ev2)


        # Layout for the plot widget
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
                                
        # Initialize default visible signals
        for signal in default_visible_signals:
            if signal in signal_names:
                self.visibility_control[signal] = True
                self.register_signal(signal)
            else:
                print(f"Error: Signal '{signal}' not found in signal_names.")

   
    def register_signal(self, signal_name):
        """Register a new signal to be displayed on the spatial plot."""
        
        if signal_name in self.plot_curves:
            return  # Signal already exists
        
        curve = pg.PlotDataItem()  # Create a plot data item for the signal
        self.plot_widget.addItem(curve)  # Add the curve to the plot
        self.plot_curves[signal_name] = curve
        self.legend.addItem(curve, signal_name)  # Add the curve to the legend
        print(f"Added signal {signal_name} to plot and legend")  # Debug output

        
    def update_data(self, signal_name, data, current_timestamp):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            # if data is not None and len(data) > 0:
            if data is not None:
                self.data[signal_name] = data
                if signal_name not in self.plot_curves:
                    self.register_signal(signal_name)  # Ensure the signal is added to the plot
                self.plot_data()  # Re-plot with updated data for all signals
            else:
                print(f"Warning: Received empty or None data for signal {signal_name}")
        else:
            print(f"Error: Signal '{signal_name}' not found in signal_names.")

        
    def plot_data(self):
        """Plot data for all subscribed signals based on visibility control."""
        for signal_name, curve in self.plot_curves.items():
            if self.visibility_control.get(signal_name, False):
                data = self.data.get(signal_name)
                if data is not None:
                    try:
                        if signal_name == 'car_pose(t)':
                            if signal_name in self.rect_items:
                                rect_item = self.rect_items[signal_name]
                                self.vehicle.set_pose_at_front_axle(data['x'], data['y'], math.radians(data['theta']))
                            else:
                                rect_item = self.vehicle
                                self.plot_widget.getViewBox().addItem(rect_item)
                                self.rect_items[signal_name] = rect_item
                        elif signal_name == 'route':
                            curve.setData(data['x'], data['y'], pen=pg.mkPen('r'))
                        elif signal_name == 'path_in_world_coordinates(t)':
                            data = np.array(data)  # Ensure it's a numpy array
                            curve.setData(data[:, 0], data[:, 1], pen=None, symbol='o', symbolBrush='g', symbolSize=5)
                        elif signal_name == 'car_pose_at_path_timestamp(t)':
                            x, y = data['x'], data['y']
                            curve.setData([x], [y], pen=None, symbol='p', symbolBrush='b', symbolSize=10)
                    except Exception as e:
                        print(f"Error plotting {signal_name}: {e}")
            else:
                curve.clear()  # Clear the data if the signal is not visible


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

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, signal_names, default_visible_signals=[]):
        super().__init__(viewBox=CustomViewBox(self))  # Use CustomViewBox for mouse interactions
        self.signal_names = signal_names  # This plot can subscribe to multiple signals
        self.data = {}  # Dictionary to store data for multiple signals
        self.plot_curves = {}  # Track plot curves (signal name -> PlotCurveItem)
        self.visibility_control = {signal: False for signal in signal_names}  # Visibility state for each signal
        self.legend = self.addLegend(offset=(10, 10))  # Add a legend to the plot with default position
        self.rect_items = {}  # Track custom polygon items for car_pose(t)
        self.vehicle = VehicleObject(config=niro_ev2)
                                
        # Initialize default visible signals
        for signal in default_visible_signals:
            if signal in signal_names:
                self.visibility_control[signal] = True
                self.add_signal(signal)
        
        print(f"Initializing TemporalPlotWidget with signals: {self.signal_names}")
        print(f"Data store initialized: {self.data_store}")

    def update_data(self, signal_name, data, current_timestamp):
        """Update the plot with new data for a specific signal."""
        if signal_name in self.signal_names:
            # if data is not None and len(data) > 0:
            if data is not None:
                self.data[signal_name] = data
                if signal_name not in self.plot_curves:
                    self.add_signal(signal_name)  # Ensure the signal is added to the plot
                self.plot_data()  # Re-plot with updated data for all signals
            else:
                print(f"Warning: Received empty or None data for signal {signal_name}")

    def register_signal(self, signal_name):
        """Register a new signal to be displayed on the temporal plot."""
        series = QLineSeries(name=signal_name)
        self.chart.addSeries(series)
        self.series_dict[signal_name] = series
        
    def plot_data(self):
        """Plot data for all subscribed signals based on visibility control."""
        # Clear existing QGraphicsPolygonItem objects
        # for item in self.rect_items.values():
        #     self.getViewBox().removeItem(item)
        # self.rect_items.clear()
        
        for signal_name, curve in self.plot_curves.items():
            if self.visibility_control.get(signal_name, False):
                data = self.data.get(signal_name)
                if data is not None: # and len(data) > 0:
                    try:
                        if signal_name == 'car_pose(t)':
                            # Update existing rectangle instead of clearing and re-adding
                            if signal_name in self.rect_items:
                                rect_item = self.rect_items[signal_name]
                                # Update the vehicle's pose
                                self.vehicle.set_pose_at_front_axle(data['x'], data['y'], math.radians(data['theta']))
                            else:
                                rect_item = self.vehicle
                                self.getViewBox().addItem(rect_item)
                                self.rect_items[signal_name] = rect_item   
                                # add the rect_item to the legend
                                # self.legend.addItem(rect_item, signal_name)
                                
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


class TemporalPlotWidget(QWidget):
    def __init__(self, signal_names=None, default_visible_signals=None, parent=None):
        super().__init__(parent)
        self.signal_names = signal_names or []
        self.default_visible_signals = default_visible_signals or []
        
        # Store the time series data for each signal
        self.data_store = {
            signal_name: {'timestamps': [], 'values': []} 
            for signal_name in self.signal_names
        }
               
        # Create a chart and set it up for time-series data
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Layout for the chart
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
        
        # Store series for signals
        self.series_dict = {}  # Stores QLineSeries for each signal

        # Initialize visible signals
        for signal_name in self.default_visible_signals:
            self.register_signal(signal_name)
            
            
    def register_signal(self, signal_name):
        """Register a new signal to be displayed on the temporal plot."""
        if signal_name not in self.series_dict:
            series = QLineSeries(name=signal_name)
            self.chart.addSeries(series)
            self.series_dict[signal_name] = series

            # Ensure that the signal has an entry in the data store
            if signal_name not in self.data_store:
                self.data_store[signal_name] = {'timestamps': [], 'values': []}

    def update_data(self, signal_name, data, current_timestamp):
        if signal_name in self.series_dict:
            series = self.series_dict[signal_name]
            series.clear()
    
            if isinstance(data, pd.DataFrame):
                value = data['values'].values if 'values' in data else []
            elif isinstance(data, pl.DataFrame):
                value = data["values"].to_list() if "values" in data.columns else []
            else:
                # Store the scalar value in the data store
                value = float(data)  # Ensure value is a float
        
            
            self.data_store[signal_name]['timestamps'].append(current_timestamp)
            self.data_store[signal_name]['values'].append(value)

            # Update the plot with accumulated data
            timestamps = self.data_store[signal_name]['timestamps']
            values = self.data_store[signal_name]['values']
            try:
                for t, v in zip(timestamps, values):
                    series.append(float(t), v)
            except Exception as e:
                print(f"Error updating series for {signal_name}: {e}")

            self.chart_view.chart().update()
            print(f"Updated plot for '{signal_name}' with {len(values)} points.")
        else:
            print(f"Error: Series for '{signal_name}' not found.")
            
        #     if isinstance(data, pd.DataFrame):
        #         timestamps = data['timestamps'].values if 'timestamps' in data else []
        #         values = data['values'].values if 'values' in data else []
        #     elif isinstance(data, pl.DataFrame):
        #         timestamps = data["timestamps"].to_list() if "timestamps" in data.columns else []
        #         values = data["values"].to_list() if "values" in data.columns else []
        #     else:
        #         timestamps = data.get('timestamps', [])
        #         values = data.get('values', [])

        #     for t, v in zip(timestamps, values):
        #         series.append(t, v)

        #     self.chart_view.chart().update()
        #     print(f"Updated plot for '{signal_name}' with {len(values)} points.")
        # else:
        #     print(f"Error: Series for '{signal_name}' not found.")


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
        
    