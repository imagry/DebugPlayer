from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from fsm.fsm_data_interface import DataInterface
from fsm.fsm_data_objects import FSM
from fsm.fsm_graph_visualizer import Node, Edge, GraphVisualizer
import sys
from fsm.fsm_main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize and show the main window
    main_window = MainWindow()
    main_window.show()
    main_window.resize(800, 600)
    
    # Execute the application
    sys.exit(app.exec())

