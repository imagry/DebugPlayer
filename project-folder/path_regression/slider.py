# slider.py
from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
class TimestampSlider(QWidget):
    def __init__(self, timestamps,  plugin_registry, parent=None):
        super().__init__(parent)

        self.timestamps = timestamps  # Actual timestamps array
        self.num_ticks = len(timestamps) - 1  # Number of slider ticks (integer range)
        self.plugin_registry = plugin_registry  # Store plugin_registry directly

        # Initialize slider to cover integer range
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.num_ticks)                

        # Label to display current timestamp
        self.label = QLabel(f"Timestamp: {self.timestamps[0]}")
        
        # Play/Pause/Stop buttons
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        
        # Timer for automatic playback
        self.timer = QTimer()
        self.timer.timeout.connect(self.playback_step)

        # Layout
        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()

        # Add slider and label
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        
        # Add playback controls
        slider_layout.addWidget(self.play_button)
        slider_layout.addWidget(self.pause_button)
        slider_layout.addWidget(self.stop_button)
        layout.addLayout(slider_layout)
        
        self.setLayout(layout)

        # Connect slider movement to timestamp update
        self.slider.valueChanged.connect(self.update_label)
        
        # Connect buttons to playback control
        self.play_button.clicked.connect(self.start_playback)
        self.pause_button.clicked.connect(self.pause_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        
        # Debug: Print the parent widget type and attributes
        parent = self.parent()
        if parent:
            print(f"Parent widget type: {type(parent)}")
            print(f"Parent widget attributes: {dir(parent)}")
        else:
            print("No parent widget assigned.")                        

    def update_label(self, value):
        """Update the label and sync data based on slider's value."""
        timestamp = self.timestamps[value]
        self.label.setText(f"Timestamp: {timestamp}")
                        
        # Notify all plugins directly that the timestamp has changed
        if self.plugin_registry and hasattr(self.plugin_registry, 'plugins'):
            for plugin in self.plugin_registry.plugins:
                plugin.sync_data_with_timestamp(timestamp)

    def set_range(self, min_time, max_time):
        """Set the range of the slider based on the data."""
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.num_ticks)
        self.label.setText(f"Timestamp: {min_time}")

    def start_playback(self):
        """Start playback by moving through timestamps."""
        self.timer.start(100)  # Adjust playback speed here (e.g., 100 ms for each step)

    def pause_playback(self):
        """Pause the playback."""
        self.timer.stop()

    def stop_playback(self):
        """Stop the playback and reset the slider."""
        self.timer.stop()
        self.slider.setValue(0)

    def playback_step(self):
        """Move the slider one step at a time during playback."""
        current_value = self.slider.value()
        if current_value < self.num_ticks:
            self.slider.setValue(current_value + 1)
        else:
            self.timer.stop()  # Stop at the end of the range
        
    def value(self):
        return self.slider.value()
    