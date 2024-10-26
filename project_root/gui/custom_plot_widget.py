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

class SpatialPlotWidget(pg.PlotWidget):
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
        
    def update_data(self, signal_name, data):
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
        
    def update_data(self, signal_name, data):
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
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create a chart and set it up for time-series data
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(Qt.Antialiasing)
        
        # Layout for the chart
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
        
        # Store series for signals
        self.series_dict = {}  # Stores QLineSeries for each signal

    def register_signal(self, signal_name):
        """Register a new signal to be displayed on the temporal plot."""
        series = QLineSeries(name=signal_name)
        self.chart.addSeries(series)
        self.series_dict[signal_name] = series

    def update_data(self, signal_name, data):
        """Update the plot with new data for a signal."""
        if signal_name in self.series_dict:
            series = self.series_dict[signal_name]
            series.clear()
            
            timestamps = data.get('timestamps', [])
            values = data.get('values', [])

            for t, v in zip(timestamps, values):
                series.append(t, v)

            self.chart_view.chart().update()
            print(f"Updated plot for '{signal_name}' with {len(values)} points.")
        else:
            print(f"Error: Series for '{signal_name}' not found.")


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
        
    