from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsObject, QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, QPointF
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from matplotlib.ticker import MaxNLocator, FuncFormatter
from matplotlib.lines import Line2D


import networkx as nx
from examples.fsm.fsm_core import Node, Edge, FSM

class GraphView(QGraphicsView):
    """A QGraphicsView to display the FSM graph"""

    def __init__(self, fsm: FSM, parent=None):
        super().__init__(parent)
        self.fsm = fsm
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Map node names to Node objects
        self.nodes = {}
        # Map edge keys to Edge objects
        self.edges = {}

        self.graph_scale = 250
        self.k = 3  # Default number of edges to highlight

        self.nx_layout_functions = {
            "Circular": nx.circular_layout,
            "Planar": nx.planar_layout,
            "Random": nx.random_layout,
            "Shell": nx.shell_layout,
            "Kamada-Kawai": nx.kamada_kawai_layout,
            "Spring": nx.spring_layout,
            "Spiral": nx.spiral_layout,
        }

        self.load_graph()
        self.apply_layout("Circular")

    def load_graph(self):
        """Load FSM data into the scene"""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()

        # Create nodes
        for state in self.fsm.get_states():
            node = Node(state)
            self.scene.addItem(node)
            self.nodes[state] = node

        # Create edges
        for (source_state, dest_state), signals in self.fsm.transitions.items():
            source_node = self.nodes[source_state]
            dest_node = self.nodes[dest_state]
            edge = Edge(source_node, dest_node, signals)
            self.scene.addItem(edge)
            self.edges[(source_state, dest_state)] = edge

    def get_layout_names(self):
        return list(self.nx_layout_functions.keys())

    def apply_layout(self, layout_name: str):
        """Apply a NetworkX layout to the graph"""
        if layout_name in self.nx_layout_functions:
            nx_graph = nx.DiGraph()
            nx_graph.add_edges_from(self.fsm.get_transitions())
            positions = self.nx_layout_functions[layout_name](nx_graph)

            # Set initial positions
            for state, pos in positions.items():
                x, y = pos
                x *= self.graph_scale
                y *= self.graph_scale
                node = self.nodes[state]
                node.setPos(QPointF(x, y))

    def highlight_node(self, state: str):
        """Highlight a node"""
        for node in self.nodes.values():
            node.set_highlight(False)
        if state in self.nodes:
            self.nodes[state].set_highlight(True)

    def highlight_edge(self, source_state: str, dest_state: str):
        """Highlight the specified edge from source_state to dest_state."""
        # Unhighlight all edges first
        for edge in self.edges.values():
            edge.set_highlight(False)

        # Highlight the specified edge if it exists
        key = (source_state, dest_state)
        if key in self.edges:
            self.edges[key].set_highlight(True)
            
    def highlight_last_k_edges(self, edge_list: list):
        """Highlight the last k edges traversed with a glow effect."""
        
        # Unhighlight all edges initially
        for edge in self.edges.values():
            edge.set_highlight(False)

        # Highlight each edge in the list
        level_count = 0
        for source_state, dest_state in edge_list:
            key = (source_state, dest_state)
            if key in self.edges:
                level_count += 1
                self.edges[key].set_highlight(True, glow_level = level_count/self.k)

        # Force a full scene update to apply changes immediately
        # self.scene().update()


    def set_k(self, k: int):
        self.k = k


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
        
          # Limit the zoom to horizontal only
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        self.canvas.mpl_connect('scroll_event', self.on_scroll)        
        
        # Create a single subplot for temporal signals
        self.signal_ax = self.canvas.figure.add_subplot(111)

        # Plot temporal signals
        self.plot_signals()

        # Initialize the vertical line for marking timestamp in the temporal signals plot
        self.vertical_bar = Line2D([], [], color='red', linewidth=2)
        self.signal_ax.add_line(self.vertical_bar)


    def on_scroll(self, event):
        """Handle scroll events to limit zoom to horizontal axis."""
        ax = self.signal_ax
        x_min, x_max = ax.get_xlim()
        x_range = x_max - x_min

        if event.button == 'up':
            scale_factor = 1 / 1.1
        elif event.button == 'down':
            scale_factor = 1.1
        else:
            return

        xdata = event.xdata
        new_width = x_range * scale_factor
        ax.set_xlim([xdata - new_width / 2, xdata + new_width / 2])
        ax.figure.canvas.draw_idle()
        
        
    def plot_signals(self):
        """Plot the temporal signals on the single subplot."""
        # signal_columns = self.fsm.dataframe.columns[4:-1]
        signal_names = self.fsm.signals_list
        timestamps = self.fsm.dataframe["time_stamp"]  # Use "time_stamp" as x-axis data
        
        # Plot each signal and store its line object for toggling visibility
        lines = []
        for signal in signal_names:
                # Ensure that `signal` and "signal" key exist in `signals_data`
                if signal in self.fsm.signals_dict and "signal" in self.fsm.signals_and_data_dict[signal]:
                    # Retrieve signal values
                    signal_values = self.fsm.signals_dict[signal]
                    
                    # Ensure signal values are numeric and handle None or missing values
                    if isinstance(signal_values, (list, np.ndarray)):
                        # Optionally filter out None values if necessary
                        signal_values = [value if value is not None else 0 for value in signal_values]

                        # Plot the signal
                        line, = self.signal_ax.plot(timestamps, signal_values, label=signal, marker='o', markersize=3, linestyle='--')
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