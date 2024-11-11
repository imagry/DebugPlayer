from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsObject
from PySide6.QtGui import QColor, QPen, QBrush, QLinearGradient, QGradient, QPolygonF, QPolygon
from PySide6.QtCore import Qt, QPointF, QRectF, QRect

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

