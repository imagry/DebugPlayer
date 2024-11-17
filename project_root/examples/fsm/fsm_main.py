import sys
from PySide6.QtWidgets import QApplication
from examples.fsm.fsm_main_window import MainWindow
import argparse

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Launch FSM Main Window with optional paths.")
    parser.add_argument("--trip_video_path", type=str, help="Path to the trip video file")
    parser.add_argument("--fsm_file_path", type=str, help="Path to the FSM conditions file")
    
    # Parse arguments
    args = parser.parse_args()
        # Use provided paths or default values
    trip_video_path = args.trip_video_path
    fsm_file_path = args.fsm_file_path
    
    window = MainWindow(fsm_file_path, trip_video_path)
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec())
