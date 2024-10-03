# user_plugin.py
from plugins.plugin_api_interfaces import UserPluginInterface


class UserPlugin(UserPluginInterface):
    def load_data(self, file_path: str):
        # User-specific data loading and parsing
        print(f"Loading data from {file_path}")

    def display_data(self, display_options: dict):
        # User-specific data display logic
        print(f"Displaying data with options {display_options}")


