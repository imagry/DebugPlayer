from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QVBoxLayout, QHBoxLayout,
                               QWidget, QSlider, QLabel, QTableWidget, QTableWidgetItem)
from PySide6.QtGui import QFont
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView, PlotWidget

class MainWindow(QWidget):
    """Main application window"""

    def __init__(self, fsm_file_path=None, parent=None):
        super().__init__(parent)
        self.fsm = FSM(fsm_file_path)
        self.current_index = 0
        
        # Create components for each section of the layout
        k = min(len(self.fsm.signals_dict), len(self.fsm.signals_data_dict))
        self.table_widget = self.create_table_widget(k+2)  # Tabular data section
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

        

    def create_table_widget(self, k = 10):
        """Creates a table widget for displaying tabular data."""
        table = QTableWidget()
        table.setRowCount(k)  # Set to the number of rows you need
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Data Name", "Data Value", "Signal Name", "Signal Value"])
        table.verticalHeader().setVisible(False)
        table.setColumnWidth(0, 400)
        table.setColumnWidth(2, 150)
        return table
    
    def update_table_data(self, data):
        """Update the table with new data."""
        self.table_widget.setRowCount(len(data))
        for row, (name, value) in enumerate(data.items()):
            self.table_widget.setItem(row, 0, QTableWidgetItem(name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(value)))

    def update_table_signals(self, signals):
        """Update the table with new signals."""
        self.table_widget.setRowCount(len(signals))
        for row, (name, value) in enumerate(signals.items()):
            self.table_widget.setItem(row, 2, QTableWidgetItem(name))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(value)))

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
        signal_data_values = self.fsm.get_signals_data_at_index(index)
        self.update_table_data(signal_data_values)
        
        signals_values = self.fsm.get_signals_value_at_index(index)
        self.update_table_signals(signals_values)
        


