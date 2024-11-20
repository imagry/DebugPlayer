import matplotlib
import time
import numpy as np
from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
import sys


# Set the backend to ensure compatibility in standalone scripts
# matplotlib.use("TkAgg")
matplotlib.use("Qt5Agg")
import threading
import time
import csv
import random
import os
import queue
import pandas as pd
import matplotlib.pyplot as plt
from examples.csv_watch_dog.cvs_file_handler import CSVFileHandler, watch_csv
import logging 


# Test Bench to simulate real-time writing to CSV file
def write_to_csv_simulator(file_path, duration=10, frequency=0.5):
    start_time = time.time()
    fields = ['Time', 'Value']

    # Check if file exists; create it if not, and write headers.
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

    # Write data to CSV file at approximately 'frequency' Hz.
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        t = 0
        delta_t = 1 / frequency
        freq =5
        while time.time() - start_time < duration:
            current_time = round(time.time() - start_time, 3)
            # value = round(random.uniform(0, 100), 2)
            angle_arg = 2*np.pi*t*freq
            rad_arg = np.radians(angle_arg)
            value  = np.sin(rad_arg)
            t = t + delta_t
            writer.writerow([current_time, value])
            f.flush()  # Ensure data is flushed immediately
            time.sleep(1 / frequency)  # Sleep for the desired frequency in seconds

def update_data(data_queue):
    # whenever new data is available, it is enqueued to the data_queue and we plot to the console the new data
    while True:
        try:
            while not data_queue.empty():
                new_lines_df = data_queue.get(block=True)# _nowait()
                print(f'[TB::update_data:]new_lines_df: {new_lines_df}')
        except queue.Empty:
            pass
        time.sleep(0.01)
            
# # Plotting function that runs in the main thread
# def update_plot(data_queue):
#     fig, ax = plt.subplots()
#     line, = ax.plot([], [], 'b-')
#     df = pd.DataFrame()

#     plot_mode = 0
#     data_count = 0
#     x_data, y_data = [], []  # Accumulate data points for plotting
#     plt.ion()  # Interactive mode on

#     while True:
#         # try:
#             # Fetch all data currently in the queue without waiting
#         while not data_queue.empty():
#             new_lines_df = data_queue.get_nowait()  # Dequeue the data
#             df = pd.concat([df, new_lines_df], ignore_index=True)
#             # logging.debug("New data dequeued for plotting.")
#             print(f'[TB::update_plot:]new_lines_df: {new_lines_df}')
#             if True:
#                 data_count += 1
#                 # Log the entire data frame for verification
#                 if not new_lines_df.empty:
#                     print(f"[TB::update_plot:]Data frame {data_count} dequeued:\n{new_lines_df}")
                
#                 if 'Time' in new_lines_df.columns and 'Value' in new_lines_df.columns:
#                     new_lines_df['Time'] = pd.to_numeric(new_lines_df['Time'].iloc[-1])
#                     new_lines_df['Value'] = pd.to_numeric(new_lines_df['Value'].iloc[-1])
#                     np_new_lines_df = new_lines_df.to_numpy()
                
#                 if np_new_lines_df.size > 0:
#                     x, y = np_new_lines_df[-1, 0], np_new_lines_df[-1, 1]
#                     print(f'[TB::update_plot:]Count {data_count}, x_new = {x}, y_new = {y}')
                    
#                     # Append new point to data lists
#                     x_data.append(x)
#                     y_data.append(y)
                    
#                     # Update scatter plot with all points
#                     ax.clear()  # Clear to prevent overwriting
#                     ax.scatter(x_data, y_data, color='red')
#                     print(f'Count {data_count}, x_data = {x_data}, y_data = {y_data}')
#                     ax.relim()
#                     ax.autoscale_view()

#                     # plt.draw()  # Redraw the plot
#                     plt.pause(0.11)  # Pause briefly to allow GUI update

#         # except queue.Empty:
#             # logging.debug("Queue is empty, waiting for new data.")
#             # pass

#         # Minimal sleep to allow continuous queue checking
#         time.sleep(0.01)


def update_plot(data_queue):
    fig, ax = plt.subplots()
    x_data, y_data = [], []  # Persistent lists for plotting data points
    plt.ion()  # Interactive mode on
    data_count = 0

    while True:
        while not data_queue.empty():
            new_lines_df = data_queue.get_nowait()  # Dequeue the data
            print(f'[TB::update_plot:] New data dequeued:\n{new_lines_df}')
            
            if not new_lines_df.empty and 'Time' in new_lines_df.columns and 'Value' in new_lines_df.columns:
                # Convert to numeric and extract the last row of new data
                new_lines_df['Time'] = pd.to_numeric(new_lines_df['Time'].iloc[1:])
                new_lines_df['Value'] = pd.to_numeric(new_lines_df['Value'].iloc[1:])
                x_new = new_lines_df['Time'].iloc[-1]
                y_new = new_lines_df['Value'].iloc[-1]
                print(f'[TB::update_plot:] New point: x = {x_new}, y = {y_new}')
                
                # Append new point to persistent lists
                x_data.append(x_new)
                y_data.append(y_new)
                data_count += 1
                
                # Update the plot with cumulative data
                ax.scatter(x_data, y_data, color='red')
                print(f'[TB::update_plot:] Total points plotted: {data_count}')
                ax.relim()
                ax.autoscale_view()
                plt.draw()  # Redraw the plot
                plt.pause(0.01)  # Allow GUI to refresh

        time.sleep(0.01)  # Minimal sleep for continuous queue checking


# define a plotting handler function that will be called whenever new data is available will plot to the QT window
def update_plot_qt(data_queue, timeseries):
    while True:
        try:
            while not data_queue.empty():
                new_lines_df = data_queue.get_nowait()
                print(f'[TB::update_plot_qt:]new_lines_df: {new_lines_df}')
                if not new_lines_df.empty:
                    x = new_lines_df['Time']
                    y = new_lines_df['Value']
                    timeseries.plot(x, y, clear=True)
        except queue.Empty:
            pass
        time.sleep(0.01)



class PlotUpdater(QtCore.QObject):
    """
    A class to update a plot widget with data from a queue at regular intervals.
    Attributes:
        data_signal (QtCore.Signal): A signal to emit data.
        data_queue (queue.Queue): A queue containing data to be plotted.
        plot_widget (pyqtgraph.PlotWidget): The widget where the data will be plotted.
        x_data (list): A list to store the x-axis data.
        y_data (list): A list to store the y-axis data.
    Methods:
        start():
            Starts the timer to update the plot at regular intervals.
        update_plot():
            Retrieves data from the queue and updates the plot widget.
    """
    data_signal = QtCore.Signal(object)

    def __init__(self, data_queue, plot_widget):
        super().__init__()
        self.data_queue = data_queue
        self.plot_widget = plot_widget
        self.x_data = []
        self.y_data = []

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100 ms

    def update_plot(self):
        while not self.data_queue.empty():
            new_data = self.data_queue.get()
            print(f"New data received: {new_data}")  # Debugging statement
            if 'Time' in new_data.columns and 'Value' in new_data.columns:
                self.x_data.extend(new_data['Time'].tolist())
                self.y_data.extend(new_data['Value'].tolist())
            else:
                print("Error: 'Time' or 'Value' column not found in new_data")  # Debugging statement
        
        self.plot_widget.clear()
        self.plot_widget.plot(self.x_data, self.y_data, pen='r')

if __name__ == "__main__":
    csv_file_path = "examples/csv_watch_dog/csvw_data/test_data.csv"
    data_queue = queue.Queue()

    # Create an instance of CSVFileHandler and pass the data queue
    event_handler = CSVFileHandler(csv_file_path, data_queue)

    # Parameters for retry mechanism
    k_seconds = 20  # Total time to keep trying
    ss_seconds = 2  # Rest time between attempts

    # Start CSV sniffer in a separate thread
    sniffer_thread = threading.Thread(target=watch_csv, args=(csv_file_path, event_handler, k_seconds, ss_seconds))
    sniffer_thread.daemon = True
    sniffer_thread.start()

    # Define QT main window and add a timeseries layout where the data will be plotted
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("CSV Watch Dog")
    window.setGeometry(100, 100, 800, 600)
    central_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(central_widget)
    window.setCentralWidget(central_widget)
    timeseries = pg.PlotWidget()
    layout.addWidget(timeseries)
    window.show()

    # Start writing data to the CSV file in a separate thread
    duration = 20
    frequency = 1
    writer_thread = threading.Thread(target=write_to_csv_simulator, args=(csv_file_path, duration, frequency))
    writer_thread.daemon = True
    writer_thread.start()

    # Start plotting in the main thread
    update_plot(data_queue)
    # update_data(data_queue)

    # Create and start the plot updater
    if False:
        plot_updater = PlotUpdater(data_queue, timeseries)
        plot_updater.start()
        
    sys.exit(app.exec())
    # On exit, delete the test CSV file
    os.remove(csv_file_path)