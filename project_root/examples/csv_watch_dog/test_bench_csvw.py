import os
import sys
import queue
import threading
import numpy as np
import pandas as pd
from PySide6 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg
from examples.csv_watch_dog.cvs_file_handler import CSVFileHandler, watch_csv
import time 
import matplotlib

# Set the backend to ensure compatibility in standalone scripts
# matplotlib.use("TkAgg")
matplotlib.use("Qt5Agg")
import csv
import random
import matplotlib.pyplot as plt
import logging 


# # Test Bench to simulate real-time writing to CSV file
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

class PlotUpdaterMPL(QtCore.QObject):
    data_signal = QtCore.Signal(object)

    def __init__(self, data_queue, plot_widget):
        super().__init__()
        self.data_queue = data_queue
        self.plot_widget = plot_widget
        self.x_data = []
        self.y_data = []

        # Create a matplotlib figure and axis
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.plot_widget.layout().addWidget(self.canvas)

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
        
        # print(f"x_data: {self.x_data}")  # Debugging statement
        # print(f"y_data: {self.y_data}")  # Debugging statement

        self.ax.clear()
        self.ax.scatter(self.x_data, self.y_data, color='red')  # Use scatter plot
        self.canvas.draw()
        
class PlotUpdater(QtCore.QObject):
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
        
        # print(f"x_data: {self.x_data}")  # Debugging statement
        # print(f"y_data: {self.y_data}")  # Debugging statement

        self.plot_widget.clear()
        self.plot_widget.plot(self.x_data, self.y_data, pen=None, symbol='o')  # Use symbol='o' for scatter plot

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

    plotmodes = ['pyqtgraph', 'matplotlib']
    
    PLOTMODE = plotmodes[1]
    
    # Define QT main window and add a timeseries layout where the data will be plotted
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("CSV Watch Dog")
    window.setGeometry(100, 100, 800, 600)
    central_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(central_widget)
    window.setCentralWidget(central_widget)
    
    if PLOTMODE == 'matplotlib':
        timeseries = QtWidgets.QWidget()
        timeseries.setLayout(QtWidgets.QVBoxLayout())
    elif PLOTMODE == 'pyqtgraph':
        timeseries = pg.PlotWidget()
    
    layout.addWidget(timeseries)
    window.show()

    # Start writing data to the CSV file in a separate thread
    duration = 200
    frequency = 10
    writer_thread = threading.Thread(target=write_to_csv_simulator, args=(csv_file_path, duration, frequency))
    writer_thread.daemon = True
    writer_thread.start()

    # Create and start the plot updater
    if PLOTMODE == 'matplotlib':
        plot_updater = PlotUpdaterMPL(data_queue, timeseries)
    elif PLOTMODE == 'pyqtgraph':
        plot_updater = PlotUpdater(data_queue, timeseries)

    plot_updater.start()
    
    sys.exit(app.exec())
    # On exit, delete the test CSV file
    os.remove(csv_file_path)
    
