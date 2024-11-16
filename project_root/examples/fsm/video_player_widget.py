from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QSlider, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from datetime import datetime
import pytz
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class VideoTimerPlotWidget(QWidget):
    """Widget to plot the video timer in Unix time and Tokyo time formats."""

    def __init__(self, video_start_time, parent=None):
        super().__init__(parent)
        
        # Store the video start time (Unix timestamp)
        self.video_start_time = video_start_time
        
        # Initialize the figure and canvas for the plot
        self.figure = Figure(figsize=(2, 1))
        self.canvas = FigureCanvas(self.figure)
        
        # Create layout and add the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Set up the axis for the plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Video Timer")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # Initialize text labels for Unix and Tokyo time
        self.unix_text = self.ax.text(0.5, 0.7, "", ha="center", va="center", fontsize=12)
        self.tokyo_text = self.ax.text(0.5, 0.3, "", ha="center", va="center", fontsize=12)
        
        # Set up Tokyo timezone
        self.tokyo_tz = pytz.timezone("Asia/Tokyo")
    
    def update_timer(self, current_video_time):
        """Update the video timer with the current timestamp."""
        # Calculate the current Unix time based on the video start time and current video position
        current_unix_time = self.video_start_time + current_video_time / 1000.0
        
        # Convert Unix time to Tokyo time
        current_tokyo_time = datetime.fromtimestamp(current_unix_time, self.tokyo_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # Update text labels in the plot
        self.unix_text.set_text(f"Unix Time: {current_unix_time:.0f}")
        self.tokyo_text.set_text(f"Tokyo Time: {current_tokyo_time}")
        
        # Refresh the canvas to show the updated timer
        self.canvas.draw_idle()
        
class VideoPlayerWidget(QWidget):
    def __init__(self, video_start_time, parent=None):
        super().__init__(parent)
        
        # Create QMediaPlayer and QVideoWidget
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        # Initialize the video timer plot widget with the start time
        self.video_timer_widget = VideoTimerPlotWidget(video_start_time)
                        
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

        # Track slider dragging state
        self.is_slider_dragging = False
        
        # Label to display the current timestamp
        self.timestamp_label = QLabel("Timestamp: 0 ms")
        
        # Connect the media player’s positionChanged and durationChanged signals to update the slider
        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.positionChanged.connect(self.update_timer_plot)
        self.media_player.durationChanged.connect(self.update_duration)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.video_timer_widget)  # Add the timer plot widget
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)
        layout.addWidget(self.timestamp_label)
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
        self.timestamp_label.setText(f"Timestamp: {position} ms")
        self.video_timer_widget.update_timer(position)
            
    def update_duration(self, duration):
        """Update the slider range based on video duration."""
        self.slider.setRange(0, duration)  # Duration is in milliseconds
        
    def update_timer_plot(self, position):
        """Update the video timer plot widget with the current video position."""
        self.video_timer_widget.update_timer(position)
        
    def get_current_timestamp(self):
        """Return the current timestamp in milliseconds."""
        return self.media_player.position()

    def stop_video(self):
        """Stop the video playback and reset the slider and timestamp."""
        self.media_player.stop()
        self.slider.setValue(0)
        self.timestamp_label.setText("Timestamp: 0 ms")


def parse_video_start_time(video_path):
    """Extract and convert the video start time from the filename."""
    # Assume the timestamp is in the format "YYYY-MM-DDTHH_MM_SS" at the end of the filename
    try:
        # Extract timestamp part of the filename (e.g., "2024-11-13T14_16_15")
        timestamp_str = video_path.split("__")[-1].replace(".mp4", "")
        # Parse timestamp to a datetime object
        video_start_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H_%M_%S")
        # Convert datetime to Unix time
        video_start_unix = int(video_start_dt.timestamp())
        return video_start_unix
    except ValueError:
        print("Error: Video filename format is incorrect or timestamp is missing.")
        return None

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
