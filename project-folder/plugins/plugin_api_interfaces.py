# api_interfaces.py
class UserPluginInterface:
    def load_data(self, file_path: str):
        """This function should handle loading and parsing the user's data."""
        raise NotImplementedError("This method must be implemented by the user.")

    def set_display(self, display_options: dict):
        """This function should return a UI component to display the data in the main GUI."""
        raise NotImplementedError("This method must be implemented by the user.")

    def sync_data(self, backbone_data: dict):
        """This function should sync the user’s data with the backbone data."""
        raise NotImplementedError("This method must be implemented by the user.")

    def get_data_with_timestamp(self, timestamp: int, backbone_data: dict):
        """This function will sync the plugin's data with the given timestamp."""
        raise NotImplementedError("This method must be implemented by the user.")
