from PySide6.QtWidgets import QApplication
from gui.main_window import create_main_window
from plugins.carpose_plugin import CarPosePlugin
from core.data_loader import parse_arguments

def main():
    # Initialize QApplication
    app = QApplication([])

    # Initialize and register plugins with the PlotManager
    trip_path = parse_arguments()
    car_pose_plugin = CarPosePlugin(trip_path)
    
    # Create the main window, and pass the loaded plugins and timestamps to it
    win, plot_manager = create_main_window(car_pose_plugin=car_pose_plugin)
    win.show()
    

    # Assuming we're loading data from a dummy path or a real trip
    plot_manager.request_data(0)  # Start with an initial timestamp (e.g., 0)

    # Start the event loop
    app.exec()

if __name__ == '__main__':
    main()
