from PySide6.QtCore import Qt, QUrl
from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaFormat
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtMultimediaWidgets import QVideoWidget


from examples.video_sync.vs_main_window import VideoPlayer
import ffmpeg



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    path_to_your_video = '/home/thh3/dev/DebugPlayer/project_root/examples/video_sync/vs_data/ARIYA_TO_01__2024-11-13T14_16_15.mp4'
    # Example timestamps in milliseconds for each frame you want to control
    timestamps = [0, 1000, 2000, 3000, 4000]  # Replace with actual frame timestamps
   
    # Extract metadata, including frame timestamps
    probe = ffmpeg.probe(path_to_your_video)
    for stream in probe['streams']:
        if stream['codec_type'] == 'video':
            frame_rate = eval(stream['r_frame_rate'])
            duration = float(stream['duration'])
            # Extract additional useful fields, like "tags" with timecode or PTS
            print(f"Frame rate: {frame_rate}, Duration: {duration}")
            print("Metadata:", stream.get('tags', {}))
        
    player = VideoPlayer(timestamps)
    player.load_video(path_to_your_video)
    player.show()
    
    sys.exit(app.exec())
