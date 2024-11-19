import matplotlib
import time
import numpy as np

# Set the backend to ensure compatibility in standalone scripts
matplotlib.use("TkAgg")

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
        while time.time() - start_time < duration:
            current_time = round(time.time() - start_time, 3)
            value = round(random.uniform(0, 100), 2)
            writer.writerow([current_time, value])
            f.flush()  # Ensure data is flushed immediately
            time.sleep(1 / frequency)  # Sleep for the desired frequency in seconds


# Plotting function that runs in the main thread
def update_plot(data_queue):
    plt.ion()  # Interactive mode on
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-')
    df = pd.DataFrame()

    plot_mode = 0
    data_count = 0
    x_data, y_data = [], []  # Accumulate data points for plotting

    while True:
        try:
            # Fetch all data currently in the queue without waiting
            while not data_queue.empty():
                new_lines_df = data_queue.get_nowait()  # Dequeue the data
                df = pd.concat([df, new_lines_df], ignore_index=True)
                logging.debug("New data dequeued for plotting.")

                if not plot_mode:
                    data_count += 1
                    # Log the entire data frame for verification
                    if not new_lines_df.empty:
                        print(f"Data frame {data_count} dequeued:\n{new_lines_df}")
                    
                    # Convert new_lines_df to numpy array for additional verification
                    np_new_lines_df = new_lines_df.to_numpy()
                    if np_new_lines_df.size > 0:
                        x, y = np_new_lines_df[-1, 0], np_new_lines_df[-1, 1]
                        print(f'Count {data_count}, x_new = {x}, y_new = {y}')
                        
                        # Append new point to data lists
                        x_data.append(x)
                        y_data.append(y)
                        
                        # Update scatter plot with all points
                        ax.clear()  # Clear to prevent overwriting
                        ax.scatter(x_data, y_data, color='red')
                        ax.relim()
                        ax.autoscale_view()

                        plt.draw()  # Redraw the plot
                        plt.pause(0.01)  # Pause briefly to allow GUI update

        except queue.Empty:
            logging.debug("Queue is empty, waiting for new data.")
            pass

        # Minimal sleep to allow continuous queue checking
        time.sleep(0.01)
        
# Main function to run the test bench
if __name__ == "__main__":
    csv_file_path = "examples/csv_watch_dog/csvw_data/test_data.csv"
    # 
    data_queue = queue.Queue() #

    # Create an instance of CSVFileHandler and pass the data queue
    event_handler = CSVFileHandler(csv_file_path, data_queue)

    # Start CSV sniffer in a separate thread
    sniffer_thread = threading.Thread(target=watch_csv, args=(csv_file_path, event_handler))
    sniffer_thread.daemon = True
    sniffer_thread.start()

    # Start writing data to the CSV file in a separate thread
    writer_thread = threading.Thread(target=write_to_csv_simulator, args=(csv_file_path, 20,   1))
    writer_thread.daemon = True
    writer_thread.start()

    # Start plotting in the main thread
    update_plot(data_queue)


