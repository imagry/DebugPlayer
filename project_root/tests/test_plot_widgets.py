import sys
import numpy as np
import time
from PySide6.QtWidgets import QApplication, QMainWindow
from gui.custom_plot_widget import TemporalPlotWidget_plt, TemporalPlotWidget_pg

def main():
    # Initialize the QApplication
    app = QApplication(sys.argv)

    # Create a main window to hold the plot widget
    window = QMainWindow()
    window.setWindowTitle("Temporal Plot Widget Test")
    window.setGeometry(100, 100, 800, 600)

    # Initialize the TemporalPlotWidget
    temporal_plot_widget = TemporalPlotWidget_pg()
    
    # Add the TemporalPlotWidget to the main window
    window.setCentralWidget(temporal_plot_widget)
    window.show()

    # Register some example signals
    signals = ["current_speed", "target_speed", "current_steering"]
    axes = ["ax1", "ax2", "ax3"]
    
    for signal, ax_name in zip(signals, axes):
        temporal_plot_widget.register_signal(signal, ax_name)

    # Generate some example data and update the plot in a loop
    timestamps = np.linspace(0, 10, 500)  # Example timestamps
    data_values = {
        "current_speed": np.sin(timestamps),  # Sinusoidal example for current speed
        "target_speed": np.cos(timestamps),   # Cosine example for target speed
        "current_steering": np.tan(timestamps) % 1.0  # Tangent (bounded) for current steering
    }

    # Function to simulate data updates
    def update_plots():
        for i, timestamp in enumerate(timestamps):
            for signal in signals:
                value = data_values[signal][i]
                temporal_plot_widget.update_data(signal, value, timestamp)
            
            # Force a pause between each iteration to simulate a time delay
            app.processEvents()  # Process Qt events
            time.sleep(0.2)      # Adjust the pause duration as needed

    # Run the plot update function in a loop
    update_plots()

    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
