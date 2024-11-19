import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from io import StringIO
import queue
import logging
import numpy as np

# Set up basic logging configuration
# logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, data_queue):
        self.file_path = file_path
        self.last_position = 0
        self.data_queue = data_queue

    def on_modified(self, event):
        if event.src_path == self.file_path:
            # logging.debug("File modified detected, reading new data.")
            self.read_new_data()

    def read_new_data(self):
        try:
            with open(self.file_path, 'r') as f:
                f.seek(self.last_position)
                new_data = f.readlines()
                self.last_position = f.tell()

            if new_data:
                # logging.debug("New data detected and added to the queue.")
                new_lines_df = pd.read_csv(StringIO(''.join(new_data)))
                self.data_queue.put(new_lines_df)

        except Exception as e:
            logging.error(f"Error reading or updating data: {e}")

def watch_csv(file_path, event_handler):
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
