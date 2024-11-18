import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Usage
csv_file_path = "path/to/your/file.csv"  # Replace with your CSV file path
watch_csv(csv_file_path)

