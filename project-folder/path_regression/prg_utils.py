# utils.py
import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import pyqtgraph as pg


# Some general helper functions
def get_color_list(n_colors):
    # Generate n_colors distinct colors
    import matplotlib.pyplot as plt
    cmap = plt.get_cmap('hsv')
    return [pg.mkColor(cmap(i / n_colors)) for i in range(n_colors)]
