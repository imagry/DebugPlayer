from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox,QVBoxLayout,
                               QWidget, QSlider, QLabel)
import sys
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView


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
