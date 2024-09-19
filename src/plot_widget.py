# plot_widget.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class PlotWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        
        # Simple layout with a label for now
        layout = QVBoxLayout(self)
        self.label = QLabel(title)
        layout.addWidget(self.label)
