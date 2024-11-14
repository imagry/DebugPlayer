from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import sys

trip_video_path = '/home/thh3/dev/DebugPlayer/project_root/examples/video_sync/vs_data/ARIYA_TO_01__2024-11-14T14_09_32.mp4'
class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window layout
        self.setWindowTitle("Video Player with Slider Control")
        self.setGeometry(100, 100, 800, 600)
        
        # Create QMediaPlayer and QVideoWidget
        self.media_player = QMediaPlayer(self)
        # self.audio_output = QAudioOutput(self)
        # self.media_player.setAudioOutput(self.audio_output)
        
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Play button
        self.play_button = QPushButton("Play Video")
        self.play_button.clicked.connect(self.play_video)
        
        # Slider to control video position
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)  # Arbitrary range; we'll update it based on the video length
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderMoved.connect(self.update_fsm)  # Connect slider to custom_function as well

        # Connect the media player's positionChanged and durationChanged signals to update the slider
        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.durationChanged.connect(self.update_duration)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def play_video(self):
        # Load the video file
        video_url = QUrl.fromLocalFile(trip_video_path)  # Replace with your video path
        self.media_player.setSource(video_url)
        
        # Play the video
        self.media_player.play()
    
    def set_position(self, position):
        """Seek to the position in milliseconds."""
        duration = self.media_player.duration()
        new_position = position / 1000 * duration  # Convert slider value to position in ms
        self.media_player.setPosition(new_position)
    
    def update_slider(self, position):
        """Update the slider position as the video plays."""
        duration = self.media_player.duration()
        if duration > 0:
            self.slider.setValue(int((position / duration) * 1000))
    
    def update_duration(self, duration):
        """Update the slider range based on the video duration."""
        self.slider.setRange(0, 1000)  # Keep slider at a consistent scale of 0-1000

    def update_fsm(self, position):
        """Custom function that is triggered when the slider is moved."""
        print(f"Slider moved to position: {position}")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
