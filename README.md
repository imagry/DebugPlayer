# DebugPlayer
Debug data player

Install libxcb:
pip install setuptools
sudo apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev

pip install pyside6 matplotlib pyqtgraph SciPy NumPy python-opengl spatialmath-python 


Overview of File Structure:
main.py: Entry point for launching the application.
playback_viewer.py: Sets up the main window, integrates different modules, and manages interactions.
data_handler.py: Manages data loading, storage, and access.
playback_controls.py: Handles playback control logic, including play/pause, speed adjustment, and time navigation.
plot_manager.py: Responsible for managing all plots and updating them based on the data.
signal_manager.py: Manages the signal selection UI and updates the temporal plot based on user selections.

Utils:
