from datetime import datetime
from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon

class TimestampSlider(QWidget):
    # Define the signal that emits the updated timestamp
    timestamp_changed = Signal(object)
    
    def __init__(self, plot_manager, timestamps, parent=None):
        super().__init__(parent)
        self.plot_manager = plot_manager
        self.timestamps = timestamps  # Array of real timestamps from the data
        self.num_ticks = len(timestamps) - 1  # Number of slider ticks (integer range)
        self.is_playing = False  # Track play/pause state
        self.mode = "Frame"  # Initial mode is "Frame"

        # Initialize slider to cover integer range
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.num_ticks)  # Set the range according to timestamps
        self.slider.valueChanged.connect(self.on_slider_changed)
        
        # Label to display current timestamp                
        self.label = QLabel(f"Timestamp: {self.time_ms_to_datetime(self.timestamps[0])} ({self.timestamps[0]}[ms])")  # Initial timestamp    
        
        # Play/Pause Button
        self.play_pause_button = QPushButton()
        self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_pause_button.clicked.connect(self.toggle_play_pause)

        # Stop Button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)

        # Speed Control Slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider_values = [1/8, 1/4, 1/2, 3/4, 1, 1.5, 2, 4, 10, 32]
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(len(self.speed_slider_values) - 1)
        self.speed_slider.setValue(4)  # Default speed is 1x
        self.speed_slider.setTickPosition(QSlider.TicksAbove)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setToolTip("Playback Speed")
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        # self.slider.sliderMoved.connect(self.on_slider_moved)  # Connect to sliderMoved signal

        # Speed Label
        self.speed_label = QLabel("Speed: 1x")
        
        # Mode Selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Frame", "Time"])
        self.mode_selector.currentIndexChanged.connect(self.update_mode)
        
        # Layout
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.speed_label)
        controls_layout.addWidget(self.speed_slider)
        controls_layout.addWidget(self.mode_selector)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.label)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(slider_layout)
        main_layout.setStretch(0, 1)  # Make controls layout take less space
        main_layout.setStretch(1, 6)  # Make slider layout take more space
        self.setLayout(main_layout)

        # Timer for playback
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_playback)
        
    def on_slider_changed(self, value):
        """Handle slider value changes, map to actual timestamps, and update."""
        timestamp_ms = self.get_timestamp(value)  # Get actual timestamp from slider value
        self.label.setText(f"Timestamp: {self.time_ms_to_datetime(timestamp_ms)} ({timestamp_ms}[ms])")  # Update the label
        self.plot_manager.request_data(timestamp_ms)  # Request data for this timestamp
        self.timestamp_changed.emit(timestamp_ms)
        
        
    def on_slider_moved(self, value):
        """Handle real-time slider movement."""
        print(f"Slider moved to position: {value}")
        slider_geometry = self.slider.geometry()
        print(f"Slider Geometry: x={slider_geometry.x()}, y={slider_geometry.y()}, width={slider_geometry.width()}, height={slider_geometry.height()}")

        self.slider_position_changed.emit(value)  # Emit signal for real-time slider position change


    def get_timestamp(self, slider_value):
        """Map the slider's integer value to the corresponding timestamp."""
        return self.timestamps[slider_value]  # Return the actual timestamp
    
    def time_ms_to_datetime(self, time_ms):
        """Convert a time in milliseconds to a datetime object."""
        time_stamp_datatime =  datetime.fromtimestamp(time_ms / 1000)
        formatted_time = time_stamp_datatime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Truncate to 3 digits of the seconds fraction
        return formatted_time
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.is_playing:
            self.timer.stop()
            self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.timer.start(200)  # Start timer with an interval of 200ms
            self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.is_playing = not self.is_playing
    
    def stop(self):
        """Stop the playback and reset to the beginning."""
        self.timer.stop()
        self.is_playing = False
        self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.slider.setValue(0)  # Reset slider to the start
    
    def update_playback(self):
        """Update the slider position during playback."""
        current_value = self.slider.value()
        speed_multiplier = self.speed_slider_values[self.speed_slider.value()]
        if self.mode == "Time":
            elapsed_ms = speed_multiplier * 200  # Assume 200ms timer interval
            new_value = min(current_value + int(elapsed_ms / (self.timestamps[1] - self.timestamps[0])), self.num_ticks)
        else:  # Frame mode
            new_value = current_value + speed_multiplier

        if new_value >= self.num_ticks:
            self.timer.stop()
            self.is_playing = False
            self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-start"))
            new_value = self.num_ticks  # Cap at the maximum value
        self.slider.setValue(int(new_value))

    def update_speed_label(self, value):
        """Update speed label based on the speed slider value."""
        speed_multiplier = self.speed_slider_values[value]
        self.speed_label.setText(f"Speed: {speed_multiplier:.2f}x")

    def update_mode(self, index):
        """Update the playback mode between Frame and Time."""
        self.mode = self.mode_selector.currentText()
        if self.mode == "Time":
            self.speed_label.setText("Speed: 1x (Real-Time)")
        else:
            self.update_speed_label(self.speed_slider.value())