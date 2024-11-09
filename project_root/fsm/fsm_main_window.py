from PySide6.QtWidgets import QComboBox, QVBoxLayout, QWidget
from PySide6.QtWidgets import QLabel, QSlider
from PySide6.QtCore import Qt
from fsm.fsm_data_interface import DataInterface
from fsm.fsm_data_objects import FSM
from fsm.fsm_graph_visualizer import Node, Edge, GraphVisualizer

class MainWindow(QWidget):
       
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize data interface, FSM, and visualization
        data_interface = DataInterface()
        data_interface.load_mock_data()
        self.fsm = FSM(data_interface)
        self.view = GraphVisualizer(self.fsm)

        # Set up layout for MainWindow
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        # Add UI components for layout selection and other controls
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(self.view.nx_layout_functions.keys())
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        layout.addWidget(QLabel("Select Layout:"))
        layout.addWidget(self.layout_combo)

        # Slider to simulate state traversal and highlight transitions
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.fsm.get_dataframe()) - 1)  # Based on number of transitions
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.update_fsm_state)
        layout.addWidget(QLabel("FSM State Slider:"))
        layout.addWidget(self.slider)
        
        
        # Attach the graph visualizer view to the layout
        layout.addWidget(self.view)
        self.setLayout(layout)
        
        
    def update_fsm_state(self, index):
        """Update the FSM state based on the slider value with support for configurable signals."""
        
        # Check if it's the first state
        if index == 0:
            current_state = self.fsm.dataframe["Current State"].iloc[index]
            self.view.highlight_last_k_edges([])  # No edges to highlight
            self.view.highlight_node(current_state)
            return

        # Generate the list of traversed edges based on the slider index
        state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()
        traversed_edges = list(zip(state_sequence[:-1], state_sequence[1:]))

        # Update highlights for last 'k' edges
        num_edges_to_highlight = min(self.view.k, len(traversed_edges))
        edges_to_highlight = traversed_edges[-num_edges_to_highlight:]
        self.view.highlight_last_k_edges(edges_to_highlight)
