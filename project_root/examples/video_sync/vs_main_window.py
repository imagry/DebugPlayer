from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QMainWindow):
    def __init__(self, timestamps):
        super().__init__()
        
        self.timestamps = timestamps  # External timestamps
        self.current_timestamp_index = 0
        
        # Video player setup
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        
        # Video display widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Slider setup
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, len(self.timestamps) - 1)
        self.slider.valueChanged.connect(self.update_frame_position)
        
        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.slider)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def load_video(self, video_path):
        """Load video from file path."""
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        
    def update_frame_position(self, index):
        """Update video position based on slider."""
        self.current_timestamp_index = index
        timestamp = self.timestamps[index]
        self.media_player.setPosition(timestamp)
