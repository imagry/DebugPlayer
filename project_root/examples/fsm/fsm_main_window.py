from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QVBoxLayout,
                               QWidget, QSlider, QLabel)
import sys
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import AutoLocator
from matplotlib.ticker import MaxNLocator, FuncFormatter



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
            # self.signal_label.setText("Signals: None")
            self.view.highlight_node(current_state)
            return  

        self.state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()
        self.traversed_edges = list(zip(self.state_sequence[:-1], self.state_sequence[1:]))

        row = self.fsm.dataframe.iloc[index]
        current_state = row["Current State"]
        self.state_label.setText(f"Current State: {current_state}")

        # signal_columns = self.fsm.dataframe.columns[2:-1]
        # signals = {col: row[col] for col in signal_columns}
        # signals_text = ", ".join(str(value) for value in signals.values())
        # TODO: plot only relevant signals, the ones that changed on this tranisiton compared to the previous meaningful transition
        # self.signal_label.setText(f"Signals: {signals_text}")

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

        # Create the figure and canvas
        self.canvas = FigureCanvas(Figure(figsize=(10, 4)))  # Single figure for signals plot only
        layout.addWidget(self.canvas)
        
        # Add the toolbar for interactive functionality
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)  # Add toolbar below the canvas
        
        # Create a single subplot for temporal signals
        self.signal_ax = self.canvas.figure.add_subplot(111)

        # Plot temporal signals
        self.plot_signals()

        # Initialize the vertical line for marking timestamp in the temporal signals plot
        self.vertical_bar = Line2D([], [], color='red', linewidth=2)
        self.signal_ax.add_line(self.vertical_bar)

    def plot_signals(self):
        """Plot the temporal signals on the single subplot."""
        # signal_columns = self.fsm.dataframe.columns[4:-1]
        signal_names = self.fsm.signals_list
        timestamps = self.fsm.dataframe["time_stamp"]  # Use "time_stamp" as x-axis data
        
        # Plot each signal and store its line object for toggling visibility
        lines = []
        for signal in signal_names:
            signal_values = self.fsm.signals_data[signal]["signal"]  # Access the signal values
            line, = self.signal_ax.plot(timestamps, signal_values, label=signal)    
            lines.append(line)


        # Create the legend and position it at the top
        legend = self.signal_ax.legend(
            loc='upper center',  # Position at the top center
            bbox_to_anchor=(1.05, 1.15),  # Adjust position to place it outside the plot area
            ncol=2,  # Arrange legend entries in multiple columns
            fontsize='small'  # Reduce font size for readability
        )
        legend.set_picker(True)  # Enable picking on the legend

        # Set y-axis tick density and formatting
        self.signal_ax.yaxis.set_major_locator(MaxNLocator(nbins=5))  # Limit to a maximum of 5 ticks
        self.signal_ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))  # Limit to 2 decimal places


        # Attach an event handler to each legend item for toggling visibility
        for legend_entry, line in zip(legend.get_lines(), lines):
            legend_entry.set_picker(True)  # Make legend item clickable
            legend_entry.set_pickradius(5)  # Set the area around the label that responds to clicks

            # Define a callback function for toggling visibility
            def on_pick(event, legend_entry=legend_entry, line=line):
                if event.artist == legend_entry:
                    visible = not line.get_visible()
                    line.set_visible(visible)
                    legend_entry.set_alpha(1.0 if visible else 0.2)  # Dim legend entry if hidden
                    self.signal_ax.figure.canvas.draw_idle()
                    
                    # auto rescale y-axis if any line is hidden
                    self.signal_ax.relim()
                    self.signal_ax.autoscale_view()                    
                    
            # Connect the callback to pick events
            self.canvas.mpl_connect("pick_event", on_pick)                    
            
        
        self.signal_ax.set_title("Temporal Signals")
        self.signal_ax.set_xlabel("Time")
        self.signal_ax.set_ylabel("Signal Value")
        
    def update_vertical_bar(self, timestamp):
        """Update the vertical bar position based on the current timestamp in the signals plot."""
        y_min, y_max = self.signal_ax.get_ylim()  # Get the y-axis limits for the line
        self.vertical_bar.set_data([timestamp, timestamp], [y_min, y_max])  # Set both x and y data
        self.signal_ax.figure.canvas.draw_idle()  # Redraw the canvas to update the position