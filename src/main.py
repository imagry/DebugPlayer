from PySide6.QtWidgets import QApplication
from playback_viewer import PlaybackViewer
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    viewer = PlaybackViewer()
    viewer.show()
    
    sys.exit(app.exec())
