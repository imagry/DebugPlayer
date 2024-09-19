# data_handler.py

from PySide6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd

class DataHandler:
    def __init__(self):
        self.time_data = []
        self.main_data = pd.DataFrame()
        self.secondary_data = pd.DataFrame()
        self.temporal_data = pd.DataFrame()

    def load_data(self):
        """
        Loads trip data from a file and stores it in respective dataframes.
        """
        file_name, _ = QFileDialog.getOpenFileName(None, "Open Data File", "", "CSV Files (*.csv);;JSON Files (*.json)")
        if file_name:
            try:
                if file_name.endswith('.csv'):
                    data = pd.read_csv(file_name)
                elif file_name.endswith('.json'):
                    data = pd.read_json(file_name)
                else:
                    raise ValueError("Unsupported file format.")
                
                # Assuming data has 'time', 'x', 'y', 'signal1', 'signal2'... columns
                self.time_data = data['time'].values
                self.main_data = data[['x', 'y']]
                self.secondary_data = data[['x', 'y']].copy()  # Example data, can be modified
                self.temporal_data = data.drop(columns=['time', 'x', 'y'])
                
                QMessageBox.information(None, "Success", "Data loaded successfully!")
                return True
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to load data: {e}")
        return False

    def get_time_data(self):
        return self.time_data

    def get_main_data(self):
        return self.main_data

    def get_secondary_data(self):
        return self.secondary_data

    def get_temporal_data(self):
        return self.temporal_data

    def get_signals(self):
        return list(self.temporal_data.columns)
