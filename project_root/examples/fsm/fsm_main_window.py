from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QVBoxLayout, QHBoxLayout,
                               QWidget, QSlider, QLabel, QTableWidget, QTableWidgetItem)
import sys
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import MaxNLocator, FuncFormatter
import numpy as np
from PySide6.QtGui import QFont


class MainWindow(QWidget):
    """Main application window"""

    def __init__(self, fsm_file_path=None, parent=None):
        super().__init__(parent)
        self.fsm = FSM(fsm_file_path)
        self.current_index = 0
        
        # Create components for each section of the layout
        self.table_widget = self.create_table_widget()  # Tabular data section
        self.view = GraphView(self.fsm)                 # FSM view section
        self.plot_widget = PlotWidget(self.fsm)         # Signal plot section

        # Assuming `self.table_widget` is your QTableWidget instance
        font = QFont()
        font.setPointSize(12)  # Set the desired font size
        self.table_widget.setFont(font)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Top row layout (tabular data and FSM view)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.table_widget, 1)  # Stretch factor 1 for table
        top_layout.addWidget(self.view, 2)          # Stretch factor 2 for FSM view


        # Bottom row layout (signals plot)
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.plot_widget)
        
        # Add layouts to the main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # Add FSM State Slider with label
        slider_layout = QHBoxLayout()  # Create a horizontal layout for the slider and its label
        slider_label = QLabel("FSM State Slider:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.fsm.dataframe) - 1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slider)

        bottom_layout.addLayout(slider_layout)  # Add slider layout to the bottom layout


        # Add Combo Box for selecting layout
        layout_combo_layout = QHBoxLayout()  # Horizontal layout for layout selection combo box
        layout_combo_label = QLabel("Select Layout:")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(self.view.get_layout_names())
        
        layout_combo_layout.addWidget(layout_combo_label)
        layout_combo_layout.addWidget(self.layout_combo)
        
        bottom_layout.addLayout(layout_combo_layout)  # Add layout combo box layout to the bottom layout


        # Add Combo Box for selecting the number of edges to highlight
        k_combo_layout = QHBoxLayout()  # Horizontal layout for edges combo box
        k_combo_label = QLabel("Highlight last k edges:")
        self.k_combo = QComboBox()
        self.k_combo.addItems([str(i) for i in range(1, 11)])  # k from 1 to 10
        self.k_combo.setCurrentIndex(2)  # Default k is 3
        
        k_combo_layout.addWidget(k_combo_label)
        k_combo_layout.addWidget(self.k_combo)
        
        bottom_layout.addLayout(k_combo_layout)  # Add edges combo box layout to the bottom layout


        # Connect signals for interactions
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        self.slider.valueChanged.connect(self.update_fsm_state)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))


        # Initialize FSM data
        self.state_sequence = []
        self.traversed_edges = []
        
        # Set up interactions and initial state
        # self.initialize_interactions()
        self.update_fsm_state(0)

        

    def create_table_widget(self):
        """Creates a table widget for displaying tabular data."""
        table = QTableWidget()
        table.setRowCount(10)  # Set to the number of rows you need
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Data Name", "Data Value"])
        table.verticalHeader().setVisible(False)
        return table
    
    def update_table_data(self, data):
        """Update the table with new data."""
        self.table_widget.setRowCount(len(data))
        for row, (name, value) in enumerate(data.items()):
            self.table_widget.setItem(row, 0, QTableWidgetItem(name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(value)))


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
            self.view.highlight_node(current_state)
            return  

        self.state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()
        self.traversed_edges = list(zip(self.state_sequence[:-1], self.state_sequence[1:]))

        row = self.fsm.dataframe.iloc[index]
        current_state = row["Current State"]

        self.view.highlight_node(current_state)

        d = len(self.traversed_edges)
        num_edges_to_highlight = min(self.view.k, d)
        self.traversed_edges = [edge for edge in self.traversed_edges if edge[0] != edge[1]]
        edges_to_highlight = self.traversed_edges[-num_edges_to_highlight:]
        self.view.highlight_last_k_edges(edges_to_highlight)

        # Update the timestamp marker in the PlotWidget
        self.update_timestamp_marker(index)
        data = self.fsm.get_signals_data_at_index(index)
        self.update_table_data(data)


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
                # Ensure that `signal` and "signal" key exist in `signals_data`
                if signal in self.fsm.signals_data and "signal" in self.fsm.signals_data[signal]:
                    # Retrieve signal values
                    signal_values = self.fsm.signals_data[signal]["signal"]
                    
                    # Ensure signal values are numeric and handle None or missing values
                    if isinstance(signal_values, (list, np.ndarray)):
                        # Optionally filter out None values if necessary
                        signal_values = [value if value is not None else 0 for value in signal_values]

                        # Plot the signal
                        line, = self.signal_ax.plot(timestamps, signal_values, label=signal)
                        lines.append(line)
                    else:
                        print(f"Warning: signal data for {signal} is not in a list or array format.")
                else:
                    print(f"Warning: Missing data for signal '{signal}' or missing 'signal' key in signals_data.")

        # Create the legend and position it at the top
        legend = self.signal_ax.legend(
            loc='upper center',  # Position at the top center
            bbox_to_anchor=(1.05, 1.05),  # Adjust position to place it outside the plot area
            ncol=1,  # Arrange legend entries in multiple columns
            fontsize='medium'  # Reduce font size for readability
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
                            # Only autoscale if visibility changes
                    if not visible:
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