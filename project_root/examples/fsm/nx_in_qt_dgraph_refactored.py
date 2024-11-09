from PySide6.QtCore import (
    QEasingCurve, QLineF, QParallelAnimationGroup, QPointF,
    QPropertyAnimation, QRectF, Qt
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication, QComboBox, QGraphicsItem, QGraphicsObject,
    QGraphicsScene, QGraphicsView, QStyleOptionGraphicsItem,
    QVBoxLayout, QWidget, QSlider, QLabel
)
import pandas as pd
import random
from datetime import datetime, timedelta
import math
import sys
import networkx as nx


class FSM:
    """Finite State Machine Data Class"""

    def __init__(self):
        self.states = set()
        self.transitions = {}
        self.dataframe = None
        self.load_mock_data(k=8, m=3, n=20, self_loops=False)


    def load_mock_data(self, k=4, m=3, n=10, self_loops=False):
        """Generate mock FSM data with continuous transitions.

        Args:
            k (int): Number of unique states.
            m (int): Number of unique signals.
            n (int): Number of rows (transitions).
            self_loops (bool): Allow or disallow self-loops.
        """
        # Generate states and signals
        states = [f"S{i+1}" for i in range(k)]
        signals = [f"Signal{j+1}" for j in range(m)]
        data = []
        start_time = datetime.now()

        # Initialize the first state randomly
        current_state = random.choice(states)

        for i in range(n):
            # Choose a next state
            next_state = random.choice(states)
            # Ensure no self-loops if they are not allowed
            if not self_loops:
                while next_state == current_state:
                    next_state = random.choice(states)

            # Randomly select 'm' signals for this transition
            selected_signals = {f"signal{j+1}": random.choice(signals) for j in range(m)}

            # Record the transition with timestamp, state, and signals
            timestamp = start_time + timedelta(seconds=i * 10)
            data.append([timestamp, current_state, next_state, *selected_signals.values()])

            # Update transitions dictionary for each transition
            self.transitions[(current_state, next_state)] = selected_signals
            
            # Move to the next state
            current_state = next_state

        # Track all unique states
        self.states.update(states)

        # Define column names dynamically for the DataFrame
        column_names = ["Timestamp", "Current State", "Next State"] + [f"Signal{j+1}" for j in range(m)]

        # Create DataFrame from the generated data
        self.dataframe = pd.DataFrame(data, columns=column_names)

        print(self.dataframe)
        
    def get_states(self):
        return list(self.states)

    def get_transitions(self):
        return list(self.transitions.keys())


class Node(QGraphicsObject):
    """A QGraphicsItem representing a node in the graph"""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.edges = []
        self.default_color = QColor("#5AD469")
        self.highlight_color = QColor("#FFD700")
        self.color = self.default_color
        self.radius = 30
        self.rect = QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.color.darker(), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(QPen(QColor("white")))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.name)

    def add_edge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.adjust()
        return super().itemChange(change, value)

    def set_highlight(self, highlight: bool):
        self.color = self.highlight_color if highlight else self.default_color
        self.update()


class Edge(QGraphicsItem):
    """A QGraphicsItem representing an edge in the graph"""

    def __init__(self, source: Node, dest: Node, signals: dict, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.source = source
        self.dest = dest
        self.signals = signals

        # Edge properties
        self.line_width = 2
        self.default_color = QColor("#2BB53C")  # Default color for the edge
        self.highlight_color = QColor("red")    # Color to use when highlighted
        self.color = self.default_color         # Initial color
        
        # New attribute for glow effect
        self.glow = False
        
        
        # Arrow size and line for edge
        self.arrow_size = 10
        self.line = QLineF()
        self.setZValue(-1)
        self.adjust()
                  
        self.source.add_edge(self)
        self.dest.add_edge(self)


    def boundingRect(self) -> QRectF:
        extra = self.line_width + self.arrow_size
        return QRectF(self.line.p1(), self.line.p2()).normalized().adjusted(-extra, -extra, extra, extra)

    def adjust(self):
        self.prepareGeometryChange()
        self.line = QLineF(
            self.source.pos(),
            self.dest.pos(),
        )

    def _draw_arrow(self, painter: QPainter):
        painter.setBrush(QBrush(self.color))
        line = self.line
        angle = math.atan2(-line.dy(), line.dx())

        arrow_p1 = line.p2() - QPointF(
            math.sin(angle + math.pi / 3) * self.arrow_size,
            math.cos(angle + math.pi / 3) * self.arrow_size,
        )
        arrow_p2 = line.p2() - QPointF(
            math.sin(angle - math.pi / 3) * self.arrow_size,
            math.cos(angle - math.pi / 3) * self.arrow_size,
        )
        arrow_head = QPolygonF([line.p2(), arrow_p1, arrow_p2])
        painter.drawPolygon(arrow_head)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Draw the edge with optional glow effect when highlighted."""
        if self.source and self.dest:
            # Set up the painter for antialiasing
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)
            
            # Draw the glow effect if the edge is highlighted
            if self.glow:
                glow_pen = QPen(QColor(255, 215, 0, 100))  # A semi-transparent yellow glow
                glow_pen.setWidth(self.line_width + 10)  # Make the glow thicker than the edge
                painter.setPen(glow_pen)
                painter.drawLine(self.line)

            # Draw the main line with the current color
            main_pen = QPen(self.color, self.line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(main_pen)
            painter.drawLine(self.line)

            # Draw the arrow with the main color
            painter.setBrush(QBrush(self.color))
            self._draw_arrow(painter)

            # Draw the signals or other information if needed
            mid_point = (self.line.p1() + self.line.p2()) / 2
            painter.setPen(QPen(QColor("black")))
            signals_text = ", ".join([v for v in self.signals.values()])
            painter.drawText(mid_point, signals_text)
            

    def set_highlight(self, highlight: bool):
        """Toggle the highlight effect by setting the glow flag and updating the item."""
        self.glow = highlight  # Set a flag to indicate whether the glow should be drawn
        self.update()  # Force a repaint to reflect the glow effect



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

        self.graph_scale = 200
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
        for source_state, dest_state in edge_list:
            key = (source_state, dest_state)
            if key in self.edges:
                self.edges[key].set_highlight(True)

        # Force a full scene update to apply changes immediately
        # self.scene().update()


    def set_k(self, k: int):
        self.k = k


class MainWindow(QWidget):
    """Main application window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fsm = FSM()
        self.current_index = 0

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

        self.k_combo = QComboBox()
        self.k_combo.addItems([str(i) for i in range(1, 11)])  # k from 1 to 10
        self.k_combo.setCurrentIndex(2)  # Default k is 3

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

        # Connect signals
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        self.slider.valueChanged.connect(self.update_fsm_state)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))

        # Initialize
        self.state_sequence = []
        self.traversed_edges = []
        self.update_fsm_state(0)
        
            
    def update_fsm_state(self, index):
        """Update the FSM state based on the slider value with support for configurable signals."""
        
        # Handle the first state case where there are no traversed edges
        if index == 0:
            # Reset the state sequence and traversed edges
            self.state_sequence = []
            self.traversed_edges = []
            current_state = self.fsm.dataframe["Current State"].iloc[index]
            
            # Highlight only the current state without any edges
            self.state_label.setText(f"Current State: {current_state}")
            self.signal_label.setText("Signals: None")
            self.view.highlight_node(current_state)
            return  # Exit early since there are no edges to process

        # 1. Reconstruct the state sequence up to the current index
        self.state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()

        # 2. Build the list of traversed edges based on the state sequence
        self.traversed_edges = list(zip(self.state_sequence[:-1], self.state_sequence[1:]))

        # 3. Get the current state and signals from the current row
        row = self.fsm.dataframe.iloc[index]
        current_state = row["Current State"]

        # Dynamically retrieve all signal columns (assumes all columns between "Current State" and "Next State" are signals)
        signal_columns = self.fsm.dataframe.columns[2:-1]  # Select columns after "Current State" and before "Next State"
        signals = {col: row[col] for col in signal_columns}

        # 4. Update labels with the current state and dynamically generated signals
        self.state_label.setText(f"Current State: {current_state}")
        signals_text = ", ".join(signals.values())
        self.signal_label.setText(f"Signals: {signals_text}")

        # 5. Highlight the current node
        self.view.highlight_node(current_state)

        # 6. Calculate the number of edges to highlight
        d = len(self.traversed_edges)  # Total number of traversed edges
        num_edges_to_highlight = min(self.view.k, d)

        # 7. Get the last 'num_edges_to_highlight' edges
        edges_to_highlight = self.traversed_edges[-num_edges_to_highlight:]

        # 8. Highlight the edges
        self.view.highlight_last_k_edges(edges_to_highlight)

        print(f"Traversed Edges: {self.traversed_edges}")
        print(f"Edges to Highlight: {edges_to_highlight}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec())
