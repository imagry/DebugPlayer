from abc import ABC, abstractmethod

class PluginBase(ABC):
    @abstractmethod
    def __init__(self, file_path):
        """
        Initialize the plugin with the given file path.

        Parameters:
        file_path (str): The path to the data file.
        """
        self.file_path = file_path
        self.signals = {}

    @abstractmethod
    def has_signal(self, signal_name):
        """
        Check if this plugin provides the requested signal.

        Parameters:
        signal_name (str): The name of the signal.

        Returns:
        bool: True if the signal is provided, False otherwise.
        """
        pass

    @abstractmethod
    def get_data_for_timestamp(self, signal_name, timestamp):
        """
        Fetch data for a specific signal and timestamp.

        Parameters:
        signal_name (str): The name of the signal.
        timestamp (float): The timestamp to fetch data for.

        Returns:
        dict: The data for the requested signal and timestamp.
        """
        pass