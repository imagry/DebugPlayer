from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl
import sys


trip_video_path = "/home/thh3/Videos/trips/ARIYA_TO_01__2024-11-15T10_41_48.mp4"   

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Player with Slider Control")
        self.setGeometry(100, 100, 800, 600)
        
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        
        self.play_button = QPushButton("Play Video")
        self.play_button.clicked.connect(self.play_video)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)  # Initial arbitrary range; will be updated based on video duration
        
        self.media_player.positionChanged.connect(self.update_slider)
        self.slider.sliderMoved.connect(self.set_position)
        self.media_player.durationChanged.connect(self.update_duration)
        
        self.timestamp_label = QLabel("Timestamp: 0 ms")
        
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)
        layout.addWidget(self.timestamp_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def play_video(self):
        video_url = QUrl.fromLocalFile(trip_video_path)
        self.media_player.setSource(video_url)
        self.media_player.play()
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def update_slider(self, position):
        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)
    
    def update_duration(self, duration):
        self.slider.setRange(0, duration)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())