from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        
        # Create Matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Create an axis for plotting
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)
    
    def update_plot(self, data):
        """
        Updates the plot with new data.
        """
        self.ax.clear()
        self.ax.plot(data)
        self.ax.set_title(self.title)
        self.canvas.draw()
