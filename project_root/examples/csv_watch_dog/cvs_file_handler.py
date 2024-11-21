import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from io import StringIO
import queue
import logging
import numpy as np
import os

# Set up basic logging configuration
# logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, data_queue):
        self.file_path = file_path
        self.last_position = 0
        self.data_queue = data_queue
        self.linesread = 0

    def on_modified(self, event):
        if event.src_path == self.file_path: # Only read the file if the event is from the file being watched
            # logging.debug("File modified detected, reading new data.")
            self.read_new_data()

    def read_new_data(self):
        try:
            with open(self.file_path, 'r') as f:
                f.seek(self.last_position)
                new_data = f.readlines()
                self.last_position = f.tell()

            # Check if this is the first line of the file (header row)
            if self.last_position == 0:
                return
            
            if new_data:
                # Process the new data into a DataFrame
                new_lines_df = pd.read_csv(
                StringIO(''.join(new_data)), 
                header=None,                # Treat all rows as data (no header row)
                names=['Time', 'Value'],    # Explicitly assign column names
            )
            if self.linesread == 0:
                self.linesread +=1
                return
            
            self.linesread +=1
            
            # if 'Time' in new_lines_df.columns and 'Value' in new_lines_df.columns:
            self.data_queue.put(new_lines_df, block=True)
            print(f'[CSVFileHandler::read_new_data] New data detected and added to the queue: {new_lines_df}')
            # else:
            #     print(f"[CSVFileHandler::read_new_data] Error: 'Time' or 'Value' column not found in new_data:\n{new_lines_df}")

        except Exception as e:
            logging.error(f"Error reading or updating data: {e}")


def watch_csv(file_path, event_handler, k_seconds, ss_seconds):
    start_time = time.time()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(file_path) or '.', recursive=False)
    
    while time.time() - start_time < k_seconds:
        try:
            observer.start()
            break
        except FileNotFoundError:
            logging.error(f"No such file or directory: '{file_path}'")
            time.sleep(ss_seconds)
        except Exception as e:
            logging.error(f"Error starting observer: {e}")
            time.sleep(ss_seconds)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()