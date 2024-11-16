from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QSlider, QLabel, QHBoxLayout, QSizePolicy, QLineEdit
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from datetime import datetime
import pytz
from PySide6.QtGui import QFont
import pytz
from datetime import datetime
import time
        
class VideoPlayerWidget(QWidget):
    def __init__(self, video_start_time, parent=None):
        super().__init__(parent)
        self.video_start_time = video_start_time  # Store video start time
        
        # Initialize offset
        self.time_offset = 0.0  # Start with zero offset
        
        # Create QMediaPlayer and QVideoWidget
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        # Initialize the video timer display widget with the start time
        self.video_time_display = VideoTimeDisplayWidget(font_size=14, font_color="orange")
                        
        # Set the video widget to expand with the window
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        
        # Slider to control video position
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)  # Arbitrary range; we’ll scale it with the video duration
        
        # Connect slider events to update functions
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        self.slider.sliderMoved.connect(self.set_position)
        
        # Track slider dragging state
        self.is_slider_dragging = False
        
        # Label to display the current timestamp
        self.timestamp_label = QLabel("Timestamp: 0 ms")
                
        # Offset controls
        self.offset_label = QLabel("Time Offset:")
        self.offset_label.setToolTip("Adjust the offset between video time and actual time (in seconds)")
        
        self.offset_edit = QLineEdit(f"{self.time_offset:.4f}")
        self.offset_edit.setFixedWidth(80)
        self.offset_edit.setAlignment(Qt.AlignRight)
        
        self.offset_up_button = QPushButton("▲")
        self.offset_down_button = QPushButton("▼")

        # Connect buttons and edit field
        self.offset_up_button.clicked.connect(self.increase_offset)
        self.offset_down_button.clicked.connect(self.decrease_offset)
        self.offset_edit.returnPressed.connect(self.update_offset_from_text)
        
        # Connect the media player's signals
        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.positionChanged.connect(self.update_time_display)
        self.media_player.durationChanged.connect(self.update_duration)
        
                    
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.video_time_display)  # Add the time display widget        
        # Layout for offset controls
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(self.offset_label)
        offset_layout.addWidget(self.offset_edit)
        offset_layout.addWidget(self.offset_up_button)
        offset_layout.addWidget(self.offset_down_button)
        layout.addLayout(offset_layout)
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)               
        # layout.addWidget(self.timestamp_label) # Optional
        self.setLayout(layout)
    
    def on_slider_pressed(self):
        """Handle slider press event to mark the beginning of dragging."""
        self.is_slider_dragging = True
    
    def on_slider_released(self):
        """Handle slider release event to finalize the dragging."""
        self.is_slider_dragging = False
        # Explicitly set the video position to the slider’s final value
        final_slider_position = self.slider.value()
        self.set_position(final_slider_position)
            
        # Notify MainWindow to update FSM timer based on the final slider value
        if self.parent():  # Check if there's a parent (i.e., MainWindow)
            self.parent().update_fsm_timer(final_slider_position)            
            
    def load_video(self, trip_video_path):
        """Load a video from the given path."""
        video_url = QUrl.fromLocalFile(trip_video_path)  # Use the preferred path method
        self.media_player.setSource(video_url)
    
    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.media_player.isPlaying():
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
    
    def set_position(self, position):
        """Set video position based on slider."""
        duration = self.media_player.duration()
        if duration > 0:
            new_position = position / 1000 * duration  # Convert slider value to position in ms
            
            # Block signals to avoid feedback loops during updates
            self.media_player.blockSignals(True)
            print(f"set_position called with position: {position}")
            self.media_player.setPosition(new_position)
            self.media_player.blockSignals(False)
    
    def update_slider(self, position):
        """Update the slider position and FSM timer during video playback."""
        duration = self.media_player.duration()
        if duration > 0:
            slider_value = int((position / duration) * 1000)
            
            # Update slider only if not dragging
            if not self.is_slider_dragging:
                self.slider.blockSignals(True)
                self.slider.setValue(slider_value)
                self.slider.blockSignals(False)
        
        # Update the timestamp label and video timer plot
        # self.timestamp_label.setText(f"Timestamp: {position} ms")
        # self.video_timer_widget.update_timer(position)
            
    def update_duration(self, duration):
        """Update the slider range based on video duration."""
        print(f"Video duration received: {duration} ms")
        self.slider.setRange(0, duration)  # Duration is in milliseconds
            
    def update_time_display(self, position):
        """Update the video time display widget with the current video position."""
        try:
            self.video_time_display.update_time(position, self.video_start_time, self.time_offset)
        except Exception as e:
            print(f"Error in update_time_display: {e}")
            
    def get_current_timestamp(self):
        """Return the current timestamp in milliseconds."""
        return self.media_player.position()

    def stop_video(self):
        """Stop the video playback and reset the slider and timestamp."""
        self.media_player.stop()
        self.slider.setValue(0)
        # self.timestamp_label.setText("Timestamp: 0 ms")

    def increase_offset(self):
        """Increase the offset by a fixed increment (e.g., 0.1 seconds)."""
        self.time_offset += 0.1  # Adjust increment as needed
        self.update_offset_display()
        self.update_time_display(self.media_player.position())  # Update time display

    def decrease_offset(self):
        """Decrease the offset by a fixed increment (e.g., 0.1 seconds)."""
        self.time_offset -= 0.1  # Adjust decrement as needed
        self.update_offset_display()
        self.update_time_display(self.media_player.position())  # Update time display

    def update_offset_from_text(self):
        """Update the offset value based on the text entered by the user."""
        try:
            new_offset = float(self.offset_edit.text())
            self.time_offset = new_offset
            self.update_time_display(self.media_player.position())  # Update time display
        except ValueError:
            # Reset the text to the current offset if parsing fails
            self.offset_edit.setText(f"{self.time_offset:.4f}")

    def update_offset_display(self):
        """Update the offset display in the QLineEdit."""
        self.offset_edit.setText(f"{self.time_offset:.4f}")

    def parse_video_start_time(self, video_path):
        """Extract and convert the video start time from the filename."""
        # Assume the timestamp is in the format "YYYY-MM-DDTHH_MM_SS" at the end of the filename
        try:
            # Extract timestamp part of the filename (e.g., "2024-11-13T14_16_15")
            timestamp_str = video_path.split("__")[-1].replace(".mp4", "")
            
            # Parse timestamp to a datetime object
            video_start_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H_%M_%S")
            
            # Define Tokyo timezone
            tokyo_tz = pytz.timezone("Asia/Tokyo")
        
            # Localize the naive datetime to Tokyo time
            video_start_dt_tokyo = tokyo_tz.localize(video_start_dt)
                
            # Convert datetime to Unix time
            video_start_unix = int(video_start_dt_tokyo.timestamp())
        
            return video_start_unix
        
        except ValueError:
            print("Error: Video filename format is incorrect or timestamp is missing.")
            return None   

    def closeEvent(self, event):
        """Handle the event when the video player window is closed."""
        # Stop the media player
        self.media_player.stop()
        # Delete the media player to release resources
        self.media_player.deleteLater()
        # Call the base class implementation (optional but recommended)
        super().closeEvent(event)
class VideoTimeDisplayWidget(QWidget):
    """Widget to display the current video time in Unix and Tokyo time formats."""

    def __init__(self, font_size=12, font_color="orange", parent=None):
        super().__init__(parent)
        
        # Set up labels to show Unix time and Tokyo time
        self.unix_time_label = QLabel("Unix Time: ")
        self.tokyo_time_label = QLabel("Tokyo Time: ")
        
        # Apply font size and color
        self.set_font_size(font_size)
        self.set_font_color(font_color)
        
        # Background Color
        # self.setStyleSheet("background-color: black;")

        # Arrange labels in a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.unix_time_label)
        layout.addWidget(self.tokyo_time_label)
        self.setLayout(layout)
        
        # Set up Tokyo timezone
        self.tokyo_tz = pytz.timezone("Asia/Tokyo")
    
    def set_font_size(self, size):
        """Set the font size for the labels."""
        font = QFont()
        font.setPointSize(size)
        self.unix_time_label.setFont(font)
        self.tokyo_time_label.setFont(font)
    
    def set_font_color(self, color):
        """Set the font color for the labels."""
        self.unix_time_label.setStyleSheet(f"color: {color};")
        self.tokyo_time_label.setStyleSheet(f"color: {color};")
    
    def update_time(self, current_video_time_ms, video_start_time, time_offset=0.0):
        """Update the displayed time based on the video position."""
        try:
            # Calculate the current Unix time
            current_unix_time = video_start_time + (current_video_time_ms / 1000.0) + time_offset

            # Convert Unix time to Tokyo time
            current_tokyo_time = datetime.fromtimestamp(current_unix_time, self.tokyo_tz).strftime('%Y-%m-%d %H:%M:%S')
            
            # Update labels
            self.unix_time_label.setText(f"Unix Time: {current_unix_time:.4f}")
            self.tokyo_time_label.setText(f"Tokyo Time: {current_tokyo_time}")
        except Exception as e:
            print(f"Error in update_time: {e}")


# Usage Example in Another Tool
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    # Main window example to embed the VideoPlayerWidget
    main_window = QMainWindow()
    video_player = VideoPlayerWidget()
    main_window.setCentralWidget(video_player)
    main_window.setWindowTitle("Embedded Video Player")
    main_window.resize(800, 600)
    trip_video_path = '/home/thh3/dev/DebugPlayer/project_root/examples/video_sync/vs_data/ARIYA_TO_01__2024-11-13T14_16_15.mp4'

    # Load a video file (replace with your actual path)
    video_player.load_video(trip_video_path)
    
    main_window.show()
    sys.exit(app.exec())
