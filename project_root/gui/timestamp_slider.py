from datetime import datetime
from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class TimestampSlider(QWidget):
    def __init__(self, plot_manager, timestamps, parent=None):
        super().__init__(parent)
        self.plot_manager = plot_manager
        self.timestamps = timestamps  # Array of real timestamps from the data
        self.num_ticks = len(timestamps) - 1  # Number of slider ticks (integer range)

        # Initialize slider to cover integer range
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.num_ticks)  # Set the range according to timestamps
        self.slider.valueChanged.connect(self.on_slider_changed)
        
        # Label to display current timestamp                
        self.label = QLabel(f"Timestamp: {self.time_ms_to_datetime(self.timestamps[0])} ({self.timestamps[0]}[ms])")  # Initial timestamp    
        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        
    def on_slider_changed(self, value):
        """Handle slider value changes, map to actual timestamps, and update."""
        timestamp_ms = self.get_timestamp(value)  # Get actual timestamp from slider value
        self.label.setText(f"Timestamp: {self.time_ms_to_datetime(timestamp_ms)} ({timestamp_ms}[ms])")  # Update the label
        self.plot_manager.request_data(timestamp_ms)  # Request data for this timestamp

    def get_timestamp(self, slider_value):
        """Map the slider's integer value to the corresponding timestamp."""
        return self.timestamps[slider_value]  # Return the actual timestamp
    
    def time_ms_to_datetime(self, time_ms):
        """Convert a time in milliseconds to a datetime object."""
        time_stamp_datatime =  datetime.fromtimestamp(time_ms / 1000)
        formatted_time = time_stamp_datatime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Truncate to 3 digits of the seconds fraction
        return formatted_time