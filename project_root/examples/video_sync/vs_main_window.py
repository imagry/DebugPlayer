from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
import sys

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window layout
        self.setWindowTitle("Video Player with Slider Control")
        self.setGeometry(100, 100, 800, 600)
        
        # Create QMediaPlayer and QVideoWidget
        self.media_player = QMediaPlayer(self)
        
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Play button
        self.play_button = QPushButton("Play Video")
        self.play_button.clicked.connect(self.play_video)
        
        # Slider to control video position
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)  # Arbitrary range; we'll update it based on the video length
        self.slider.sliderMoved.connect(self.set_position)
        
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
        video_url = QUrl.fromLocalFile("/path/to/your/video.mp4")  # Replace with your video path
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
        self.slider.setRange(0, duration)  # Duration is in milliseconds
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
