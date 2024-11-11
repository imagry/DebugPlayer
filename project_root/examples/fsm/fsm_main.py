import sys
from PySide6.QtWidgets import QApplication
from examples.fsm.fsm_main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fsm_file_path = "examples/fsm/data/fsm_data.csv"  
    fsm_file_path = None  
    window = MainWindow(fsm_file_path)
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec())
