import pyqtgraph as pg
from PySide6.QtCore import Qt

class PlotManager:
    def __init__(self, dock_area):
        self.dock_area = dock_area
        self.main_plot = None
        self.secondary_plot = None
        self.temporal_plot = None

    def initialize_plots(self, main_dock, secondary_dock, temporal_dock):
        """
        Initializes the plots and adds them to the corresponding docks.
        """
        self.main_plot = pg.PlotWidget(title="Main Plot")
        self.secondary_plot = pg.PlotWidget(title="Secondary Plot")
        self.temporal_plot = pg.PlotWidget(title="Temporal Signals")

        # Enable grid, zoom, and pan for the plots
        for plot in [self.main_plot, self.secondary_plot, self.temporal_plot]:
            plot.showGrid(x=True, y=True)
            plot.setMouseEnabled(x=True, y=True)  # Enable zoom and pan

        # Add custom crosshair tools
        self.crosshair = self._create_crosshair(self.main_plot)
        self.crosshair_secondary = self._create_crosshair(self.secondary_plot)
        
        # Connect hover event for tooltips
        self.main_plot.scene().sigMouseMoved.connect(self._display_tooltip)
        self.secondary_plot.scene().sigMouseMoved.connect(self._display_tooltip_secondary)

        main_dock.addWidget(self.main_plot)
        secondary_dock.addWidget(self.secondary_plot)
        temporal_dock.addWidget(self.temporal_plot)

    def _create_crosshair(self, plot):
        """
        Creates a crosshair tool for the given plot.
        """
        vline = pg.InfiniteLine(angle=90, movable=False)
        hline = pg.InfiniteLine(angle=0, movable=False)
        plot.addItem(vline, ignoreBounds=True)
        plot.addItem(hline, ignoreBounds=True)
        crosshair = {'vline': vline, 'hline': hline}
        return crosshair

    def _display_tooltip(self, pos):
        """
        Display tooltip with data details when hovering over the main plot.
        """
        # Retrieve the plot item under the mouse cursor
        vb = self.main_plot.getViewBox()
        mouse_point = vb.mapSceneToView(pos)
        x = mouse_point.x()
        y = mouse_point.y()

        # Check for nearby data points
        if hasattr(self, 'main_data') and not self.main_data.empty:
            closest_index = (self.main_data['x'] - x).abs().idxmin()
            data_x = self.main_data.iloc[closest_index]['x']
            data_y = self.main_data.iloc[closest_index]['y']
            if abs(data_x - x) < 0.1:  # Show tooltip only if close to data point
                tooltip_text = f"X: {data_x:.2f}, Y: {data_y:.2f}"
                self.main_plot.setToolTip(tooltip_text)
            else:
                self.main_plot.setToolTip("")

        # Update crosshair position
        self.crosshair['vline'].setPos(x)
        self.crosshair['hline'].setPos(y)

    def _display_tooltip_secondary(self, pos):
        """
        Display tooltip with data details when hovering over the secondary plot.
        """
        vb = self.secondary_plot.getViewBox()
        mouse_point = vb.mapSceneToView(pos)
        x = mouse_point.x()
        y = mouse_point.y()

        # Check for nearby data points
        if hasattr(self, 'secondary_data') and not self.secondary_data.empty:
            closest_index = (self.secondary_data['x'] - x).abs().idxmin()
            data_x = self.secondary_data.iloc[closest_index]['x']
            data_y = self.secondary_data.iloc[closest_index]['y']
            if abs(data_x - x) < 0.1:  # Show tooltip only if close to data point
                tooltip_text = f"X: {data_x:.2f}, Y: {data_y:.2f}"
                self.secondary_plot.setToolTip(tooltip_text)
            else:
                self.secondary_plot.setToolTip("")

        # Update crosshair position
        self.crosshair_secondary['vline'].setPos(x)
        self.crosshair_secondary['hline'].setPos(y)

    def update_data(self, main_data, secondary_data):
        """
        Updates the data used for plotting.
        """
        self.main_data = main_data
        self.secondary_data = secondary_data

    def update_plots(self):
        """
        Updates the main and secondary plots with the latest data.
        """
        if self.main_data is not None and self.secondary_data is not None:
            self.main_plot.clear()
            self.secondary_plot.clear()
            
            self.main_plot.plot(self.main_data['x'], self.main_data['y'], pen=pg.mkPen('b', width=2))
            self.secondary_plot.plot(self.secondary_data['x'], self.secondary_data['y'], pen=pg.mkPen('g', width=2))

    def update_temporal_plot(self, temporal_data):
        """
        Updates the temporal plot with selected signals.
        """
        self.temporal_plot.clear()
        if not temporal_data.empty:
            for column in temporal_data.columns:
                self.temporal_plot.plot(temporal_data.index, temporal_data[column], pen=pg.mkPen(width=2))

    def reset_plots(self):
        """
        Clears all the plots.
        """
        self.main_plot.clear()
        self.secondary_plot.clear()
        self.temporal_plot.clear()
