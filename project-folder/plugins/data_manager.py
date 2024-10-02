# data_manager.py

import pandas as pd

class DataManager:
    def __init__(self):
        self.data = {}

    def load_trip_data(self, trip_id, file_path):
        """Load trip data from a file (e.g., CSV)."""
        try:
            self.data[trip_id] = pd.read_csv(file_path)
            print(f"Trip {trip_id} data loaded from {file_path}")
        except Exception as e:
            print(f"Error loading data for {trip_id}: {e}")

    def get_data_by_timestamp(self, trip_id, timestamp):
        """Get data for a given trip and timestamp."""
        if trip_id in self.data:
            trip_data = self.data[trip_id]
            return trip_data[trip_data['timestamp'] == timestamp]
        else:
            print(f"Trip {trip_id} not loaded.")
            return pd.DataFrame()  # Empty DataFrame if no data
