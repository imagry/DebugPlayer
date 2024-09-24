import argparse
from PySide6.QtWidgets import QApplication
from playback_viewer import PlaybackViewer
import sys

if __name__ == '__main__':
      # Step 1: Create the parser
    parser = argparse.ArgumentParser(description='Process some flags.')
    
    # Step 2: Define the arguments
    parser.add_argument('--trip_dir', type=str, help='path to the directory containing trip data')
    # parser.add_argument('--flag2', type=int, help='Description for flag2')
    
    # Step 3: Parse the arguments
    args = parser.parse_args()
    
    # Step 4: Initialize the QApplication
    app = QApplication(sys.argv)
    
    viewer = PlaybackViewer(args.trip_dir)
    viewer.show()
    
    sys.exit(app.exec())
    