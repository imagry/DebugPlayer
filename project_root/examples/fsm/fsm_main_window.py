from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QVBoxLayout,
                               QWidget, QSlider, QLabel)
import sys
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class MainWindow(QWidget):
    """Main application window"""

    def __init__(self, fsm_file_path=None, parent=None):
        super().__init__(parent)
        self.fsm = FSM(fsm_file_path)
        self.current_index = 0

        # Initialize FSM View
        self.view = GraphView(self.fsm)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(self.view.get_layout_names())
        self.state_label = QLabel("Current State:")
        self.signal_label = QLabel("Signals:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.fsm.dataframe) - 1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)

        # Combo for k edges
        self.k_combo = QComboBox()
        self.k_combo.addItems([str(i) for i in range(1, 11)])  # k from 1 to 10
        self.k_combo.setCurrentIndex(2)  # Default k is 3

        # Setup layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select Layout:"))
        layout.addWidget(self.layout_combo)
        layout.addWidget(self.state_label)
        layout.addWidget(self.signal_label)
        layout.addWidget(QLabel("Highlight last k edges:"))
        layout.addWidget(self.k_combo)
        layout.addWidget(QLabel("FSM State Slider:"))
        layout.addWidget(self.slider)
        layout.addWidget(self.view)

        # Initialize the plot widget and add it directly to the main layout
        self.plot_widget = PlotWidget(self.fsm)
        layout.addWidget(self.plot_widget)

        # Connect signals
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        self.slider.valueChanged.connect(self.update_fsm_state)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))

        # Initialize
        self.state_sequence = []
        self.traversed_edges = []
        self.update_fsm_state(0)

    def update_timestamp_marker(self, index):
        """Pass the timestamp of the current index to the PlotWidget to update the vertical bar."""
        timestamp = self.fsm.dataframe["time_stamp"].iloc[index]  # Assuming "time_stamp" column exists
        self.plot_widget.update_vertical_bar(timestamp)

    def update_fsm_state(self, index):
        """Update the FSM state based on the slider value with support for configurable signals."""
        
        if index == 0:
            self.state_sequence = []
            self.traversed_edges = []
            current_state = self.fsm.dataframe["Current State"].iloc[index]
            self.state_label.setText(f"Current State: {current_state}")
            self.signal_label.setText("Signals: None")
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

        self.view.highlight_node(current_state)

        d = len(self.traversed_edges)
        num_edges_to_highlight = min(self.view.k, d)
        self.traversed_edges = [edge for edge in self.traversed_edges if edge[0] != edge[1]]
        edges_to_highlight = self.traversed_edges[-num_edges_to_highlight:]
        self.view.highlight_last_k_edges(edges_to_highlight)

        # Update the timestamp marker in the PlotWidget
        self.update_timestamp_marker(index)


class PlotWidget(QWidget):
    """Widget to display only the temporal signals with a vertical line for the current timestamp."""

    def __init__(self, fsm, parent=None):
        super().__init__(parent)
        self.fsm = fsm
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure(figsize=(10, 4)))  # Single figure for signals plot only
        layout.addWidget(self.canvas)
        
        # Create a single subplot for temporal signals
        self.signal_ax = self.canvas.figure.add_subplot(111)

        # Plot temporal signals
        self.plot_signals()

        # Initialize the vertical line for marking timestamp in the temporal signals plot
        self.vertical_bar = Line2D([], [], color='red', linewidth=2)
        self.signal_ax.add_line(self.vertical_bar)

    def plot_signals(self):
        """Plot the temporal signals on the single subplot."""
        signal_columns = self.fsm.dataframe.columns[2:-1]
        timestamps = self.fsm.dataframe["time_stamp"]  # Use "time_stamp" as x-axis data
        for signal in signal_columns:
            self.signal_ax.plot(timestamps, self.fsm.dataframe[signal], label=signal)
        self.signal_ax.legend()
        self.signal_ax.set_title("Temporal Signals")
        self.signal_ax.set_xlabel("Time")
        self.signal_ax.set_ylabel("Signal Value")

    def update_vertical_bar(self, timestamp):
        """Update the vertical bar position based on the current timestamp in the signals plot."""
        y_min, y_max = self.signal_ax.get_ylim()  # Get the y-axis limits for the line
        self.vertical_bar.set_data([timestamp, timestamp], [y_min, y_max])  # Set both x and y data
        self.signal_ax.figure.canvas.draw_idle()  # Redraw the canvas to update the position