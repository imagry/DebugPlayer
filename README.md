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