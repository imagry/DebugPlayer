import sys
from PySide6.QtWidgets import QApplication
from examples.fsm.fsm_main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trip_video_path = '/home/thh3/Downloads/ARIYA_TO_01__2024-11-15T10_41_48.mp4'
    # fsm_file_path = "/home/thh3/dev/DebugPlayer/project_root/examples/fsm/data/2024-11-15T10_51_52/li_conditions.csv"
    fsm_file_path = "/home/thh3/dev/DebugPlayer/project_root/examples/fsm/data/2024-11-15T10_41_51/li_conditions.csv"
    # "/home/thh3/dev/DebugPlayer/project_root/examples/fsm/data/fsm_3.csv"
    # fsm_file_path = None  
    window = MainWindow(fsm_file_path, trip_video_path)
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec())
