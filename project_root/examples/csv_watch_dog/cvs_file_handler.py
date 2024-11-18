import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_position = 0
        self.df = pd.DataFrame()

        # Setting up the plot
        plt.ion()  # Interactive mode on
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-')  # Empty plot with blue line

    def on_modified(self, event):
        if event.src_path == self.file_path:
            self.update_plot()

    def update_plot(self):
        # Open the CSV file and read any new lines
        try:
            with open(self.file_path, 'r') as f:
                f.seek(self.last_position)
                new_data = f.readlines()
                self.last_position = f.tell()

            if new_data:
                # Append new data to DataFrame
                new_lines_df = pd.read_csv(pd.compat.StringIO(''.join(new_data)))
                self.df = pd.concat([self.df, new_lines_df], ignore_index=True)

                # Update plot
                if not self.df.empty:
                    x_data = self.df.iloc[:, 0]  # Assuming first column is x-axis data
                    y_data = self.df.iloc[:, 1]  # Assuming second column is y-axis data
                    self.line.set_xdata(x_data)
                    self.line.set_ydata(y_data)
                    self.ax.relim()
                    self.ax.autoscale_view()
                    plt.draw()
                    plt.pause(0.01)  # Pause to update the plot

        except Exception as e:
            print(f"Error reading or updating data: {e}")

def watch_csv(file_path):
    event_handler = CSVFileHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

