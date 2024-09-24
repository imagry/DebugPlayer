import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

app = pg.mkQApp("Path Regression Analysis")

win = pg.GraphicsLayoutWidget(show=True, title="2D Trajectory Plot")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: 2D Trajectory Plot')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p4 = win.addPlot(title="Parametric, grid enabled")



p4.plot(x, y)
p4.showGrid(x=True, y=True)

if __name__ == '__main__':
    pg.exec()