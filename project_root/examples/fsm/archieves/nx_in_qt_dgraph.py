from PySide6.QtCore import (QEasingCurve, QLineF, QParallelAnimationGroup, QPointF,
                            QPropertyAnimation, QRectF, Qt)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsItem, QGraphicsObject,
                               QGraphicsScene, QGraphicsView, QStyleOptionGraphicsItem,
                               QVBoxLayout, QWidget, QSlider, QLabel)
import pandas as pd
import random
from datetime import datetime, timedelta
import math
import sys
import networkx as nx


class Node(QGraphicsObject):
    """A QGraphicsItem representing node in a graph"""

    def __init__(self, name: str, parent=None):
        """Node constructor

        Args:
            name (str): Node label
        """
        super().__init__(parent)
        self._name = name
        self._edges = []
        self._color = "#5AD469"
        self._radius = 30
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return self._rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """Override from QGraphicsItem

        Draw node

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            QPen(
                QColor(self._color).darker(),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(QBrush(QColor(self._color)))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(QPen(QColor("white")))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self._name)

    def add_edge(self, edge):
        """Add an edge to this node

        Args:
            edge (Edge)
        """
        self._edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override from QGraphicsItem

        Args:
            change (QGraphicsItem.GraphicsItemChange)
            value (Any)

        Returns:
            Any
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self._edges:
                edge.adjust()

        return super().itemChange(change, value)

    def highlight(self, highlight: bool):
        """Highlight or unhighlight the node

        Args:
            highlight (bool): True to highlight, False to unhighlight
        """
        self._color = "#FFD700" if highlight else "#5AD469"
        self.update()


class Edge(QGraphicsItem):
    def __init__(self, source: Node, dest: Node, parent: QGraphicsItem = None):
        """Edge constructor

        Args:
            source (Node): source node
            dest (Node): destination node
        """
        super().__init__(parent)
        self._source = source
        self._dest = dest

        self._tickness = 2
        self._color = "#2BB53C"
        self._highlight_color = "#FFD700"
        self._arrow_size = 20
        self._name = f"e{source._name}{dest._name}"

        self._source.add_edge(self)
        self._dest.add_edge(self)

        self._line = QLineF()
        self.setZValue(-1)
        self.adjust()

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return (
            QRectF(self._line.p1(), self._line.p2())
            .normalized()
            .adjusted(
                -self._tickness - self._arrow_size,
                -self._tickness - self._arrow_size,
                self._tickness + self._arrow_size,
                self._tickness + self._arrow_size,
            )
        )

    def adjust(self):
        """
        Update edge position from source and destination node.
        This method is called from Node::itemChange
        """
        self.prepareGeometryChange()
        self._line = QLineF(
            self._source.pos() + self._source.boundingRect().center(),
            self._dest.pos() + self._dest.boundingRect().center(),
        )

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        """Draw arrow from start point to end point.

        Args:
            painter (QPainter)
            start (QPointF): start position
            end (QPointF): end position
        """
        painter.setBrush(QBrush(self._color))

        line = QLineF(end, start)

        angle = math.atan2(-line.dy(), line.dx())
        arrow_p1 = line.p1() + QPointF(
            math.sin(angle + math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi / 3) * self._arrow_size,
        )
        arrow_p2 = line.p1() + QPointF(
            math.sin(angle + math.pi - math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi - math.pi / 3) * self._arrow_size,
        )

        arrow_head = QPolygonF()
        arrow_head.clear()
        arrow_head.append(line.p1())
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.drawLine(line)
        painter.drawPolygon(arrow_head)

    def _arrow_target(self) -> QPointF:
        """Calculate the position of the arrow taking into account the size of the destination node

        Returns:
            QPointF
        """
        target = self._line.p1()
        center = self._line.p2()
        radius = self._dest._radius
        vector = target - center
        length = math.sqrt(vector.x() ** 2 + vector.y() ** 2)
        if length == 0:
            return target
        normal = vector / length
        target = QPointF(center.x() + (normal.x() * radius), center.y() + (normal.y() * radius))

        return target

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Override from QGraphicsItem

        Draw Edge. This method is called from Edge.adjust()

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """

        if self._source and self._dest:
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)

            painter.setPen(
                QPen(
                    QColor(self._color),
                    self._tickness,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            )
            painter.drawLine(self._line)
            self._draw_arrow(painter, self._line.p1(), self._arrow_target())
            self._arrow_target()

            # Draw the edge name
            mid_point = (self._line.p1() + self._line.p2()) / 2
            painter.setPen(QPen(QColor("black")))
            painter.drawText(mid_point, self._name)

    def highlight(self, highlight: bool):
        """Highlight or unhighlight the edge

        Args:
            highlight (bool): True to highlight, False to unhighlight
        """
        self._color = self._highlight_color if highlight else "#2BB53C"
        self.update()

    def set_signals(self, signal1, signal2, signal3):
        """Set the signals for the edge

        Args:
            signal1 (str): First signal
            signal2 (str): Second signal
            signal3 (str): Third signal
        """
        self._name = f"{self._name}\n{signal1}, {signal2}, {signal3}"
        self.update()


class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, parent=None):
        """GraphView constructor

        This widget can display a directed graph

        Args:
            graph (nx.DiGraph): a networkx directed graph
        """
        super().__init__()
        self._graph = graph
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Used to add space between nodes
        self._graph_scale = 200

        # Map node name to Node object {str=>Node}
        self._nodes_map = {}

        # Map edge name to Edge object {str=>Edge}
        self._edges_map = {}

        # List of networkx layout function
        self._nx_layout = {
            "circular": nx.circular_layout,
            "planar": nx.planar_layout,
            "random": nx.random_layout,
            "shell_layout": nx.shell_layout,
            "kamada_kawai_layout": nx.kamada_kawai_layout,
            "spring_layout": nx.spring_layout,
            "spiral_layout": nx.spiral_layout,
        }

        self._load_graph()
        self.set_nx_layout("circular")

        # List to keep track of the last k edges traversed
        self._last_k_edges = []
        self._k = 3  # Default value for k

    def get_nx_layouts(self) -> list:
        """Return all layout names

        Returns:
            list: layout name (str)
        """
        return self._nx_layout.keys()

    def set_nx_layout(self, name: str):
        """Set networkx layout and start animation

        Args:
            name (str): Layout name
        """
        if name in self._nx_layout:
            self._nx_layout_function = self._nx_layout[name]

            # Compute node position from layout function
            positions = self._nx_layout_function(self._graph)

            # Change position of all nodes using an animation
            self.animations = QParallelAnimationGroup()
            for node, pos in positions.items():
                x, y = pos
                x *= self._graph_scale
                y *= self._graph_scale
                item = self._nodes_map[node]

                animation = QPropertyAnimation(item, b"pos")
                animation.setDuration(1000)
                animation.setEndValue(QPointF(x, y))
                animation.setEasingCurve(QEasingCurve.OutExpo)
                self.animations.addAnimation(animation)

            self.animations.start()

    def _load_graph(self):
        """Load graph into QGraphicsScene using Node class and Edge class"""

        self.scene().clear()
        self._nodes_map.clear()
        self._edges_map.clear()

        # Add nodes
        for node in self._graph:
            item = Node(node)
            self.scene().addItem(item)
            self._nodes_map[node] = item

        # Add edges
        for a, b in self._graph.edges:
            source = self._nodes_map[a]
            dest = self._nodes_map[b]
            edge = Edge(source, dest)
            self.scene().addItem(edge)
            self._edges_map[f"e{a}{b}"] = edge

    def highlight_node(self, node_id: str):
        """Highlight the selected node

        Args:
            node_id (str): Node ID to highlight
        """
        for node in self._nodes_map.values():
            node.highlight(False)
        if node_id in self._nodes_map:
            self._nodes_map[node_id].highlight(True)

    def highlight_last_k_edges(self, edge_list: list):
        """Highlight the last k edges traversed

        Args:
            edge_list (list): List of edges to highlight
        """
        # Unhighlight all edges
        for edge in self._scene.items():
            if isinstance(edge, Edge):
                edge.highlight(False)

        # Highlight the last k edges
        self._last_k_edges = edge_list[-self._k:]
        for edge in self._last_k_edges:
            edge.highlight(True)

    def set_k(self, k: int):
        """Set the value of k

        Args:
            k (int): Number of edges to highlight
        """
        self._k = k

    def highlight_edge(self, edge_name: str):
        """Highlight the selected edge

        Args:
            edge_name (str): Edge name to highlight
        """
        for edge in self._edges_map.values():
            edge.highlight(False)
        if edge_name in self._edges_map:
            self._edges_map[edge_name].highlight(True)

    def set_edge_signals(self, edge_name: str, signal1: str, signal2: str, signal3: str):
        """Set the signals for the selected edge

        Args:
            edge_name (str): Edge name
            signal1 (str): First signal
            signal2 (str): Second signal
            signal3 (str): Third signal
        """
        if edge_name in self._edges_map:
            self._edges_map[edge_name].set_signals(signal1, signal2, signal3)


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.previous_state = None  # Add this line to keep track of the previous state

        self.graph = nx.DiGraph()
        self.graph.add_edges_from(
            [
                ("1", "2"),
                ("2", "3"),
                ("3", "4"),
                ("4", "1"),
                ("1", "3"),
                ("2", "4"),
            ]
        )

        self.view = GraphView(self.graph)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(self.view.get_nx_layouts())
        self.node_combo = QComboBox()
        self.node_combo.addItems(self.graph.nodes)
        self.k_combo = QComboBox()
        self.k_combo.addItems([str(i) for i in range(1, 11)])  # Allow k to be set from 1 to 10
        self.k_combo.setCurrentIndex(2)  # Default value for k is 3
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(9)  # Assuming we have 10 rows of data
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.signal_label = QLabel("")

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.layout_combo)
        v_layout.addWidget(self.node_combo)
        v_layout.addWidget(self.k_combo)
        v_layout.addWidget(self.slider)
        v_layout.addWidget(self.signal_label)
        v_layout.addWidget(self.view)

        self.layout_combo.currentTextChanged.connect(self.view.set_nx_layout)
        self.node_combo.currentTextChanged.connect(self.view.highlight_node)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))
        self.slider.valueChanged.connect(self.update_fsm_state)

        # Generate mock data
        self.generate_mock_data()

    def generate_mock_data(self):
        states = ["S1", "S2", "S3", "S4"]
        signals = ["Signal1", "Signal2", "Signal3"]

        # Generate mock data
        data = []
        start_time = datetime.now()

        for i in range(10):  # Generate 10 rows of data
            timestamp = start_time + timedelta(seconds=i * 10)  # Increment timestamp by 10 seconds
            state = random.choice(states)
            signal1 = random.choice(signals)
            signal2 = random.choice(signals)
            signal3 = random.choice(signals)
            next_state = random.choice(states)
            data.append([timestamp, state, signal1, signal2, signal3, next_state])

        # Create DataFrame
        self.df = pd.DataFrame(data, columns=["Timestamp", "State", "Signal1", "Signal2", "Signal3", "Next State"])

    def update_fsm_state(self, value):
        """Update the FSM state based on the slider value

        Args:
            value (int): Slider value
        """
        row = self.df.iloc[value]
        state = row["State"]
        next_state = row["Next State"]
        signal1 = row["Signal1"]
        signal2 = row["Signal2"]
        signal3 = row["Signal3"]
        print(f"Current State: {state}, Next State: {next_state}, Signals: {signal1}, {signal2}, {signal3}")

        # Update the dropdown menu to match the current state
        index = self.node_combo.findText(state)
        if index != -1:
            self.node_combo.setCurrentIndex(index)
        
        # Highlight the current state
        self.view.highlight_node(state)

        # Highlight the signal
        self.signal_label.setText(f"Signals: {signal1}, {signal2}, {signal3}")

        # Set the signals on the edge
        edge_name = f"e{state}{next_state}"
        self.view.set_edge_signals(edge_name, signal1, signal2, signal3)

        # Highlight the edge
        self.view.highlight_edge(edge_name)
        
        # Highlight the previous state and the edge from the previous state to the current state
        if self.previous_state:
            prev_edge_name = f"e{self.previous_state}{state}"
            self.view.highlight_edge(prev_edge_name)

        # Update the previous state
        self.previous_state = state  # Update to the current state
def generate_mock_data(self):
    states = ["1", "2", "3", "4"]  # Ensure these match the node names in the graph
    signals = ["Signal1", "Signal2", "Signal3"]

    # Generate mock data
    data = []
    start_time = datetime.now()

    for i in range(10):  # Generate 10 rows of data
        timestamp = start_time + timedelta(seconds=i * 10)  # Increment timestamp by 10 seconds
        state = random.choice(states)
        signal1 = random.choice(signals)
        signal2 = random.choice(signals)
        signal3 = random.choice(signals)
        next_state = random.choice(states)
        data.append([timestamp, state, signal1, signal2, signal3, next_state])

    # Create DataFrame
    self.df = pd.DataFrame(data, columns=["Timestamp", "State", "Signal1", "Signal2", "Signal3", "Next State"])
    
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a networkx graph
    widget = MainWindow()
    widget.show()
    widget.resize(800, 600)
    sys.exit(app.exec())