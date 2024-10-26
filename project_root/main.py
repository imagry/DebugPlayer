from PySide6.QtWidgets import QApplication
from gui.main_window import create_main_window
from core.data_loader import parse_arguments
from core.plot_manager import PlotManager
import os

def main():
    # Initialize QApplication
    app = QApplication([])
   
    # Initialize the PlotManager
    plot_manager = PlotManager()
    
    # Load plugins dynamically from the 'plugins/' directory
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')

    # Pass file path arguments as needed to the plugins
    trip_path = parse_arguments()
    plugin_args = {"file_path": trip_path}
    plot_manager.load_plugins_from_directory(plugin_dir, plugin_args=plugin_args)
    
    # Create the main window
    win, plot_manager = create_main_window(plot_manager=plot_manager)
    win.show()

    # ** Request initial data for timestamp 0 **
    # This ensures that the plots are initialized with data at the start
    if "timestamps" in plot_manager.signal_plugins:
        initial_timestamp = plot_manager.plugins["CarPosePlugin"].signals["timestamps"]["func"]()[0] # Fetch timestamps from the CarPosePlugin - use () to call the lambda       
        plot_manager.request_data(initial_timestamp)
        
    # Start the event loop
    app.exec()

if __name__ == '__main__':
    main()
