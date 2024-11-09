from PySide6.QtWidgets import   QGraphicsScene, QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtCore import QPointF

from fsm.fsm_data_objects import FSM

import networkx as nx

from fsm.fsm_data_objects import Node, Edge

class GraphVisualizer(QGraphicsView):
    """Handles visualization of FSM states and transitions using Nodes and Edges."""

    def __init__(self, fsm: FSM, parent=None):
        super().__init__(parent)
        self.fsm = fsm
        # print("GraphVisualizer Transitions (received):", self.fsm.transitions)  # Debug

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.nodes = {}  # Mapping of state names to Node objects
        self.edges = {}  # Mapping of (source, dest) to Edge objects

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
        """Load FSM data into nodes and edges with fixed positions."""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()

        # Define fixed positions for testing
        fixed_positions = {
            "S1": QPointF(-50, -50),
            "S2": QPointF(50, -50),
            "S3": QPointF(-50, 50),
            "S4": QPointF(50, 50)
        }

        # Create nodes with fixed positions
        for state in self.fsm.get_states():
            node = Node(state)
            self.scene.addItem(node)
            self.nodes[state] = node
            node.setPos(fixed_positions.get(state, QPointF(0, 0)))

        # Skip edges for now to simplify the visualization
        self.scene.setSceneRect(-100, -100, 200, 200)  # Set a manageable scene area
        
            
    def load_graph_(self):
        """Load FSM data into nodes and edges within the scene."""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()

        # Create nodes
        for state in self.fsm.get_states():
            node = Node(state)
            self.scene.addItem(node)
            self.nodes[state] = node

        # Create edges with signal data
        for (source_state, dest_state), signals in self.fsm.transitions:
            source_node = self.nodes.get(source_state)
            dest_node = self.nodes.get(dest_state)

            # Ensure both nodes exist before creating an edge
            if source_node is None or dest_node is None:
                print(f"Error: Missing node for transition ({source_state} -> {dest_state})")
                continue

            # Create the edge and add it to the scene and edges dictionary
            edge = Edge(source_node, dest_node, signals)
            self.scene.addItem(edge)
            self.edges[(source_state, dest_state)] = edge

        # Set scene boundaries and fit the view
        self.scene.setSceneRect(self.scene.itemsBoundingRect())  # Set bounds to include all items
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)



    def get_layout_names(self):
        return list(self.nx_layout_functions.keys())


    def apply_layout(self, layout_name: str):
        if layout_name in self.nx_layout_functions:
            nx_graph = nx.DiGraph()
            state_pairs = [(source_state, dest_state) for (source_state, dest_state), _ in self.fsm.get_transitions()]
            nx_graph.add_edges_from(state_pairs)

            # Compute positions using the selected layout
            positions = self.nx_layout_functions[layout_name](nx_graph)

            # Apply positions with moderate scaling
            for state, pos in positions.items():
                x, y = pos
                x *= 150  # Moderate scaling factor to spread nodes
                y *= 150
                node = self.nodes[state]
                node.setPos(QPointF(x, y))

            # Set the scene rectangle to ensure all nodes are within view
            self.scene.setSceneRect(-200, -200, 400, 400)
             
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

            

    def highlight_last_k_edges(self, edge_list: list):
        """Highlight the last k edges traversed with a glow effect."""
        for edge in self.edges.values():
            edge.set_highlight(False)

        for source_state, dest_state in edge_list:
            key = (source_state, dest_state)
            if key in self.edges:
                self.edges[key].set_highlight(True)

        self.scene.update()


    def set_k(self, k: int):
        self.k = k