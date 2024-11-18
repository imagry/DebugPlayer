import threading
import time
import csv
import random
import os

# Import the previously defined CSV watcher (assuming it's in the same file or imported appropriately)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import matplotlib.pyplot as plt

from examples.csv_watch_dog.cvs_file_handler import CSVFileHandler, watch_csv

# Test Bench to simulate real-time writing to CSV file
def write_to_csv_simulator(file_path, duration=10, frequency=20):
    """
    Write new lines to the CSV file at a specified frequency.
    Args:
    - file_path: Path to the CSV file.
    - duration: Duration to run the writer in seconds.
    - frequency: Frequency of writes per second.
    """
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
            value = round(random.uniform(0, 100), 2)  # Generate a random value for testing
            writer.writerow([current_time, value])
            time.sleep(1 / frequency)

# Main function to run the test bench
if __name__ == "__main__":
    csv_file_path = "examples/csv_watch_dog/csvw_data/test_data.csv"

    # Start CSV sniffer in a separate thread
    sniffer_thread = threading.Thread(target=watch_csv, args=(csv_file_path,))
    sniffer_thread.daemon = True
    sniffer_thread.start()

    # Simulate writing to the CSV file
    write_to_csv_simulator(csv_file_path, duration=10, frequency=20)
