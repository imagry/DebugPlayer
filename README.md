# Analysis Manager

Run the script: `/home/thh3/dev/DebugPlayer/analysis_manager/main_analysis_manager.py`

Most missing packages should be installed on the fly. If you encounter any issues with missing packages, install them manually and notify me if needed.

## Running a Trip from the Menu

### Steps:

1. **On the Menu:**
   - Press `File` -> `Open Trips Folder`: Select the folder where all your trips are located.
   - Press `File` -> `Select Trip`: Choose a trip from the list of available trips.

2. To open the playback window, press the `RUN` button.

## Loading a Trip with Command-Line Arguments

1. Go to `launch.json` and ensure the following configuration is set:
    ```json
    "args": ["--trip", "trip_path"]
    ```
2. Alternatively, you can call it directly from the terminal:
    ```bash
    python analysis_manager/main_analysis_manager.py --trip "/home/thamam/data/trips/2024-09-19T13_14_48/"
    ```

## **personal-folder setting**
1. This project supports a prsonal folder so you can configure the vscode according to your preference. For, example, you can config launch.json according to your local file structure, where trip are saved, or define list of extension that will be included when this project is in use. 
2. `personal-folder` and its content are already in the project .gitignore file.
### ***Loading the prject***
To properly process the usage of personal-folder, please make sure that the project Workspace is Opened Correctly:
Go to File > Open Workspace and select your DebugPlayer.code-workspace



# DebugPlayer - `UNDER CONSTRUCTIONS`

## Preparations

Install the necessary Python packages:
```bash
pip install pyside6 matplotlib pyqtgraph SciPy NumPy spatialmath-python polars pandas 
```

Optional Installs
```bash
pip install "dask[complete]" json5
```

### Install `libxcb` Dependencies

1. Update your system:
    ```bash
    sudo apt update
    ```
2. Install the required packages:
    ```bash
    pip install setuptools
    sudo apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev
    sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb1 libxcb-util1 libxkbcommon-x11-0
    ```

## Overview of File Structure

- **`main.py`:** Entry point for launching the application.
- **`playback_viewer.py`:** Sets up the main window, integrates different modules, and manages interactions.
- **`data_handler.py`:** Manages data loading, storage, and access.
- **`playback_controls.py`:** Handles playback control logic, including play/pause, speed adjustment, and time navigation.
- **`plot_manager.py`:** Responsible for managing all plots and updating them based on the data.
- **`signal_manager.py`:** Manages the signal selection UI and updates the temporal plot based on user selections.

## Utils

### How to Add New Data - Step-by-Step Guide

1. **Data Preparation:** Ensure your data is in a suitable format (e.g., CSV or JSON).
2. **Loading the Data:** Modify the `DataHandler` to load and structure your data.
3. **Visualizing Data:** Update the `PlotManager` to plot your specific data.
4. **Interactive Features:** Verify and customize tooltips, crosshairs, and other features to align with your data structure.
5. **Testing and Refining:** Test the integration and refine the UI/UX based on your needs.


## **Adding a new Plugin**
1. Step 1: Define the API Interface.
The first step will be to create a new class that adheres to the ```UserPluginInterface```.
This class will read the data file, parse the data, and provide functionality for visualizing the data over time.

2. Step 2: Create the NewPlugin Plugin Class
```python
import pandas as pd
from api_interfaces import UserPluginInterface

class NewPlugin(UserPluginInterface):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None  # Placeholder for the loaded CSV data
        self.current_paths = None  # Current paths at the selected timestamp

    def load_data(self):
        """Load the CSV data."""
        try:
            self.data = pd.read_csv(self.file_path)
            # Ensure the data is sorted by timestamp
            self.data = self.data.sort_values(by='timestamp')
            print(f"Loaded data from {self.file_path}")
        except Exception as e:
            print(f"Failed to load CSV file: {e}")

    def set_display(self, plot_widget):
        """Display the paths on the plot widget."""
        if self.current_paths is not None and not self.current_paths.empty:
            # Extract the x and y coordinates
            x_values = self.current_paths['x']
            y_values = self.current_paths['y']
            
            # Clear the plot and replot the current paths
            plot_widget.clear()
            plot_widget.plot(x_values, y_values, pen=None, symbol='o', symbolSize=5, symbolBrush='b')
        else:
            print("No paths available for the current timestamp.")
```
### Explanation:
#### load_data: Loads the CSV file and stores the data in a Pandas DataFrame.
#### sync_data_with_timestamp: Filters the data for the given timestamp and extracts the corresponding paths.
#### display: Displays the paths on the provided plot widget.

3. Step 3: Register the Plugin
Once we have the NewPlugin class, we need to register it in the main application.

we do so by instantiating it in main() in the main_path_regression.py. 

First, add it in the include, e.g.
``` from plugins.newplugin import NewPlugin ```

<!-- TBD: create a registration as separate file -->
Then, add the two liines by writing two lines under the comment "# REGISTER PLUGINS":
    ```newplugin_plugin = NewPlugin()```
    ```regression_app.load_plugins([newplugin_plugin]) ```
    

### Some tips and guidelines regarding data format:

```python
# Check if the DataFrame index is already in Unix timestamp format
if self.path_obj.timestamps.dtype != 'int64':
    self.timestamps = self.path_obj.get_timestamps().view('int64') // 10**6 
else:
    self.timestamps = self.path_obj.timestamps
```

### Explanation:

1. **Check Data Type:**
    - The code first checks if the `timestamps` attribute of `self.path_obj` is not of type `int64`.
    - This is done using the condition `self.path_obj.timestamps.dtype != 'int64'`.

2. **Convert to Unix Timestamp:**
    - If the condition is true (i.e., the timestamps are not in `int64` format), it converts the timestamps to Unix timestamp format.
    - This is achieved by calling `self.path_obj.get_timestamps().view('int64') // 10**6`.
    - The `view('int64')` method changes the data type to `int64`, and the division by `10**9` converts the timestamps to seconds.

3. **Assign Timestamps:**
    - If the timestamps are already in `int64` format, it directly assigns `self.path_obj.timestamps` to `self.timestamps`.

This code ensures that the timestamps are always in Unix timestamp format (in seconds) before proceeding with further operations.


## **Top-level diagram** 
```mermaid
graph TD;
  MainPathRegression --> PluginRegistry
  MainPathRegression --> PathViewPlugin
  MainPathRegression --> TimestampSlider
  PluginRegistry --> sync_all_plugins
  PluginRegistry --> display_all_plugins
  PathViewPlugin --> load_data
  PathViewPlugin --> sync_data_with_timestamp
  PathViewPlugin --> display
   ``` 
