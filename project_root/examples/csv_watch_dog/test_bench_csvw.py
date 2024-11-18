import threading
import time
import csv
import random
import os
import queue
import pandas as pd
import matplotlib.pyplot as plt
from examples.csv_watch_dog.cvs_file_handler import CSVFileHandler, watch_csv

# Test Bench to simulate real-time writing to CSV file
def write_to_csv_simulator(file_path, duration=10, frequency=20):
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
            time.sleep(1 / frequency)

# Plotting function that runs in the main thread
def update_plot(data_queue):
    plt.ion()  # Interactive mode on
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-')

    df = pd.DataFrame()

    while True:
        try:
            # Fetch data from the queue
            while not data_queue.empty():
                new_lines_df = data_queue.get_nowait()
                df = pd.concat([df, new_lines_df], ignore_index=True)

            if not df.empty:
                x_data = df.iloc[:, 0]  # Assuming first column is x-axis data
                y_data = df.iloc[:, 1]  # Assuming second column is y-axis data
                line.set_xdata(x_data)
                line.set_ydata(y_data)
                ax.relim()
                ax.autoscale_view()
                plt.draw()
                plt.pause(0.01)  # Pause to update the plot

        except queue.Empty:
            pass

        time.sleep(0.01)  # Small sleep to reduce CPU usage, frequent updates

# Main function to run the test bench
if __name__ == "__main__":
    csv_file_path = "examples/csv_watch_dog/csvw_data/test_data.csv"
    data_queue = queue.Queue()

    # Create an instance of CSVFileHandler and pass the data queue
    event_handler = CSVFileHandler(csv_file_path, data_queue)

    # Start CSV sniffer in a separate thread
    sniffer_thread = threading.Thread(target=watch_csv, args=(csv_file_path, event_handler))
    sniffer_thread.daemon = True
    sniffer_thread.start()

    # Start writing data to the CSV file in a separate thread
    writer_thread = threading.Thread(target=write_to_csv_simulator, args=(csv_file_path, 10, 20))
    writer_thread.daemon = True
    writer_thread.start()

    # Start plotting in the main thread
    update_plot(data_queue)
