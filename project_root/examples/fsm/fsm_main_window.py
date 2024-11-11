from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox,QVBoxLayout,
                               QWidget, QSlider, QLabel)
from PySide6.QtWidgets import QPushButton
import sys
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QWidget):
    """Main application window"""

    def __init__(self, fsm_file_path = None, parent=None):
        super().__init__(parent)
        self.fsm = FSM(fsm_file_path)
        self.current_index = 0

        self.view = GraphView(self.fsm)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(self.view.get_layout_names())
        self.state_label = QLabel("Current State:")
        self.signal_label = QLabel("Signals:")
        self.time_label = QLabel("Time Stamp:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.fsm.dataframe) - 1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        
        # Add a button to open the signal plot window
        self.plot_button = QPushButton("Plot Signals")
        
         # Layout for MainWindow
        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_button)
        layout.addWidget(QLabel("Select Layout:"))
        layout.addWidget(self.layout_combo)
        layout.addWidget(self.state_label)
        layout.addWidget(self.signal_label)
        layout.addWidget(self.time_label)
        layout.addWidget(QLabel("Highlight last k edges:"))
        
        # Combo for k edges
        self.k_combo = QComboBox()
        self.k_combo.addItems([str(i) for i in range(1, 11)])  # k from 1 to 10
        self.k_combo.setCurrentIndex(2)  # Default k is 3
        layout.addWidget(self.k_combo)
        layout.addWidget(QLabel("FSM State Slider:"))
        layout.addWidget(self.slider)
        layout.addWidget(self.view)
        
        self.plot_button.clicked.connect(self.open_signal_plot_window)


        # Connect signals
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        self.slider.valueChanged.connect(self.update_fsm_state)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))


        # Initialize
        self.state_sequence = []
        self.traversed_edges = []
        self.update_fsm_state(0)
        
        
        
    def open_signal_plot_window(self):    
        """Open a new window to plot temporal signals."""
        self.plot_window = SignalPlotWindow(self.fsm)
        self.plot_window.show()
    
    
    def update_fsm_state(self, index):
        """Update the FSM state based on the slider value with support for configurable signals."""
        
        if index == 0:
            self.state_sequence = []
            self.traversed_edges = []
            current_state = self.fsm.dataframe["Current State"].iloc[index]
            self.state_label.setText(f"Current State: {current_state}")
            self.signal_label.setText("Signals: None")
            self.time_label.setText("Time Stamp: None")
            self.view.highlight_node(current_state)
            return  

        self.state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()
        self.traversed_edges = list(zip(self.state_sequence[:-1], self.state_sequence[1:]))

        row = self.fsm.dataframe.iloc[index]
        current_state = row["Current State"]
        self.state_label.setText(f"Current State: {current_state}")

        signal_columns = self.fsm.dataframe.columns[2:-1]
        signals = {col: row[col] for col in signal_columns}
        signals_text = ", ".join(str(value) for value in signals.values())
        self.signal_label.setText(f"Signals: {signals_text}")
        self.time_label.setText(f"Time Stamp: {row['Timestamp']}")
        self.view.highlight_node(current_state)

        d = len(self.traversed_edges)
        num_edges_to_highlight = min(self.view.k, d)
        self.traversed_edges = [edge for edge in self.traversed_edges if edge[0] != edge[1]]
        edges_to_highlight = self.traversed_edges[-num_edges_to_highlight:]
        self.view.highlight_last_k_edges(edges_to_highlight)

class SignalPlotWindow(QWidget):
    """Window to plot temporal signals."""

    def __init__(self, fsm, parent=None):
        super().__init__(parent)
        self.fsm = fsm
        self.setWindowTitle("Signal Plot")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout(self)
        self.plot_widget = PlotWidget(self.fsm)
        self.layout.addWidget(self.plot_widget)


class PlotWidget(QWidget):
    """Widget to display the signal plot."""

    def __init__(self, fsm, parent=None):
        super().__init__(parent)
        self.fsm = fsm
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)
        self.plot_signals()

    def plot_signals(self):
        """Plot the temporal signals from the FSM dataframe."""
        signal_columns = self.fsm.dataframe.columns[2:-1]
        for signal in signal_columns:
            self.ax.plot(self.fsm.dataframe[signal], label=signal)
        self.ax.legend()
        self.ax.set_title("Temporal Signals")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Signal Value")
        # self.canvas.draw()
                                            
