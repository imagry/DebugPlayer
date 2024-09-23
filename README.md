# DebugPlayer
Debug data player

Install libxcb:
pip install setuptools
sudo apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev

pip install pyside6 matplotlib pyqtgraph SciPy NumPy spatialmath-python polars pandas

Overview of File Structure:
main.py: Entry point for launching the application.
playback_viewer.py: Sets up the main window, integrates different modules, and manages interactions.
data_handler.py: Manages data loading, storage, and access.
playback_controls.py: Handles playback control logic, including play/pause, speed adjustment, and time navigation.
plot_manager.py: Responsible for managing all plots and updating them based on the data.
signal_manager.py: Manages the signal selection UI and updates the temporal plot based on user selections.

Utils:

How to add new data - Step-by-Step Guide:
1. Data Preparation: Ensure your data is in a suitable format (e.g., CSV or JSON).
2. Loading the Data: Modify the DataHandler to load and structure your data.
3. Visualizing Data: Update the PlotManager to plot your specific data.
4. Interactive Features: Verify and customize tooltips, crosshairs, and other features to align with your data structure.
5. Testing and Refining: Test the integration and refine the UI/UX based on your needs.