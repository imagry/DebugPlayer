import sys
import pandas as pd
import networkx as nx
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class FSMPlotWidget(QWidget):
    def __init__(self, data: pd.DataFrame, transitions: dict):
        super().__init__()
        self.data = data
        self.transitions = transitions
        self.current_timestamp = data['timestamp'].min()  # Initialize to the first timestamp

        # Initialize UI and networkx plot
        self.init_ui()
        self.create_fsm_networkx()

    def init_ui(self):
        """Initialize the UI layout and components."""
        main_layout = QVBoxLayout()
        
        # FSM layout: display the FSM networkx plot
        self.canvas = FigureCanvas(plt.Figure())
        main_layout.addWidget(self.canvas)

        # Set layout
        self.setLayout(main_layout)

    def create_fsm_networkx(self):
        """Create and render FSM layout using networkx."""
        G = nx.DiGraph()

        # Add nodes and edges based on transitions dictionary
        for state, edges in self.transitions.items():
            G.add_node(state)
            for target_state, label in edges.items():
                G.add_edge(state, target_state, label=label)

        # Draw the FSM using networkx and matplotlib
        ax = self.canvas.figure.subplots()
        ax.clear()

        pos = nx.spring_layout(G)  # Positioning of nodes
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, ax=ax)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", ax=ax)
        
        self.canvas.draw()

# Example transitions dictionary based on the provided image
transitions = {
    'ID': {'Approaching LI': 'Phi(D->LI)=1//SNLI=1'},
    'Approaching LI': {
        'Turning Right LI': 'Intent=R, ENLI=1',
        'Forward LI': 'Intent=F, ENLI=1',
        'Left LI': 'Intent=L, ENLI=1, CEWB=0'
    },
    'Turning Right LI': {},
    'Forward LI': {'Approaching Waiting Box': 'Intent=L, DWB=1, ENLI=1'},
    'Approaching Waiting Box': {'Waiting on the Waiting Box': 'RIF=0//ZVWB'},
    'Waiting on the Waiting Box': {'Left After WB LI': 'RWB=1, RIF=1//CZV'},
    'Left LI': {'Wait on Stop Line': 'Intent=L, DWB=1, CEWB=0//ZVSL'},
    'Wait on Stop Line': {'Exit Stop Line': 'ENLI=1'},
    'Exit Stop Line': {}
}

# Example usage
class MainWindow(QMainWindow):
    def __init__(self, fsm_widget):
        super().__init__()
        self.setWindowTitle("FSM Plot Widget")
        self.setCentralWidget(fsm_widget)

if __name__ == "__main__":
    # Example data for FSM (can be replaced with actual data)
    data = pd.DataFrame({
        'timestamp': range(10),
        'state': ['ID', 'Approaching LI', 'Forward LI', 'Approaching Waiting Box', 'Waiting on the Waiting Box',
                  'Left After WB LI', 'Left LI', 'Wait on Stop Line', 'Exit Stop Line', 'ID'],
        'signal1': [10, 20, 15, 25, 10, 30, 20, 15, 25, 10],
        'signal2': [5, 15, 10, 20, 5, 25, 10, 5, 20, 15]
    })

    # Initialize PySide6 application
    app = QApplication(sys.argv)
    fsm_widget = FSMPlotWidget(data, transitions)
    main_window = MainWindow(fsm_widget)
    main_window.show()
    sys.exit(app.exec())
