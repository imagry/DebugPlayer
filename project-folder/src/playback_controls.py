# playback_controls.py

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSlider, QLabel, QInputDialog
from PySide6.QtCore import QTimer, Qt

class PlaybackControls:
    def __init__(self, update_plots_callback, get_time_data_callback):
        self.update_plots_callback = update_plots_callback
        self.get_time_data_callback = get_time_data_callback

        # Initialize playback variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_playback)
        self.playing = False
        self.current_time = 0
        self.playback_speed = 1.0

        self.time_data = self.get_time_data_callback()
        
        # Create playback controls
        self.play_button = QPushButton("Play/Pause")
        self.play_button.clicked.connect(self.toggle_playback)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self.update_slider_position)

        self.playback_speed_label = QLabel("Speed: 1.00x")
        self.playback_speed_label.mousePressEvent = self.change_speed
        
        self.time_label = QLabel("00:00/00:41")
        self.time_label.mousePressEvent = self.jump_to_time

    def get_control_layout(self):
        """
        Returns the playback control layout.
        """
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.playback_speed_label)
        control_layout.addWidget(self.time_label)
        return control_layout

    def toggle_playback(self):
        self.playing = not self.playing
        if self.playing:
            self.timer.start(int(100 / self.playback_speed))  # Adjust timer based on playback speed
        else:
            self.timer.stop()

    def update_slider_position(self, position):
        self.current_time = position
        self.update_plots_callback()

    def change_speed(self, event):
        """
        Changes the playback speed.
        """
        current_speed = round(self.playback_speed * 10) / 10
        new_speed = {0.5: 1.0, 1.0: 1.5, 1.5: 2.0, 2.0: 0.5}.get(current_speed, 1.0)
        self.playback_speed = new_speed
        self.playback_speed_label.setText(f"Speed: {new_speed:.2f}x")
        if self.playing:
            self.timer.setInterval(int(100 / self.playback_speed))

    def jump_to_time(self, event):
        """
        Allows jumping to a specific timestamp by clicking on the time display.
        """
        time, ok = QInputDialog.getInt(None, "Jump to Time", "Enter time in seconds:", min=0, max=int(self.time_data.max()))
        if ok:
            self.current_time = time
            self.update_slider_position(time)
        
    def update_playback(self):
        self.current_time += 1
        if self.current_time > len(self.time_data) - 1:
            self.current_time = 0
        self.slider.setValue(self.current_time)
        self.update_plots_callback()

    def reset_playback(self):
        """
        Resets playback to the beginning.
        """
        self.current_time = 0
        self.slider.setValue(0)
        self.update_plots_callback()

