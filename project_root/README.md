Requirements

## Manually installing the requirments
```bash
conda create --name dbgenv python = 3.12
conda activate dbgenv
conda install 
conda create --name DbgPkg python=3.12
conda activate DbgPkg
conda install numpy -y
conda install scipy -y
conda install pip -y
conda install matplotlib -y
conda install conda-forge::spatialmath-python
conda install conda-forge::pyside6 -y
conda install conda-forge::pyqtgraph -y
conda install conda-forge::pyinstaller -y
conda install pandas -y
conda install conda-forge::polars
```

### creating the conda environment requirements YML file
```bash
conda env export --no-builds | grep -v "prefix" > environment.yml
conda env export --no-builds | grep -v "prefix" > environment_pyqt_pip_env.yml
```

### Missing xcb
```bash
sudp apt update
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0
```

### Creating conda environment from YML requirments
```bash
conda env create -f environment.yml
```

### Running the package
```bash
./main --trip1 /home/thh3/data/trips/nissan/2024-10-01T13_46_59/
```

### FAQ
### Issue with 'wayland'-
``` bash
qt.qpa.plugin: Could not find the Qt platform plugin "wayland" in ""
export QT_QPA_PLATFORM=xcb
```

You may need to install the QtCharts development package. For example, if you use a package manager like apt:

```bash
Copy code
sudo apt-get install libqt6charts6 libqt6charts6-dev
```

3. Verify LD_LIBRARY_PATH and QT_PLUGIN_PATH
Ensure that your Anaconda environment is set up correctly to find the Qt plugins:

Set LD_LIBRARY_PATH to prioritize libraries within your environment:

bash
Copy code
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
Set QT_PLUGIN_PATH to locate Qt plugins:

bash
Copy code
export QT_PLUGIN_PATH=$CONDA_PREFIX/lib/Qt/plugins




## **Some collected notes that needs to be organized**



2. Is the loading of plugins via PluginManager handled elsewhere?
Yes. Plugin registration and loading are now handled by the PlotManager.

When a plugin is initialized (like CarPosePlugin), it registers its signals and handles data provision directly via the PlotManager.
The PlotManager is responsible for coordinating between plugins and plots—so plugins no longer manage plotting directly but instead provide data to PlotManager for plots to render.

3. Handling Multiple Signals from a Single Plugin
If a plugin provides more than one signal, such as the CarPosePlugin providing both the route (a series of 2D points) and car pose (SE2 objects), the plugin can manage multiple signals and register them accordingly.

Updated Example for Handling Multiple Signals in a Plugin:
We can modify the CarPosePlugin to handle more than one signal. The plugin would advertise which signals it supports, and the PlotManager will query for the specific signal when necessary.


Debuging plotting issue- 
Recap of What to Do:
Add debugging to CarPosePlugin to confirm it’s providing data for the signal.
Add debugging to CustomPlotWidget to confirm it’s receiving the data and plotting.
Check the TimestampSlider to ensure it’s requesting data when the slider is moved.
Verify the data flow in PlotManager to ensure the correct signals are being requested and updated in the plots.

In not notes otherwise, units are meters, milliseconds, ENU, Right-Hand, x-fwd, carpose - center of front axle


Important windows - 

create_main_window - This where you register signals for plotting
        Note that there are two similar appearences: 
                # Initialize CustomPlotWidget and register signals
                car_pose_plot = CustomPlotWidget(signals=["car_pose(t)", "route"])
                route_plot = CustomPlotWidget(signals=["route"])

                # Register the plots with the PlotManager
                plot_manager.register_plot(car_pose_plot, ["car_pose(t)"])
                plot_manager.register_plot(route_plot, ["route"])
        


## **Quick overview over main components**


## How to construct a new plugin
Great! Let's move forward with Option 2: Explicit class registry for your plugins.

Here’s a step-by-step process to implement this across the system:

1. Update Each Plugin File
In each plugin file (like carpose_plugin.py), explicitly define the class to be used with a plugin_class variable.

Example in carpose_plugin.py:
```python
class CarPosePlugin:
    def __init__(self, file_path):
        self.file_path = file_path
        # Plugin initialization logic here...
        pass

# Explicitly define which class is the plugin
plugin_class = CarPosePlugin
```


### Adding new signals to plot

To add signals from PathViewPlugin to the plots, you need to ensure that the PlotManager correctly registers the plugin and its signals, and then updates the plots with the data from these signals. Here’s how you can achieve this:

Ensure PathViewPlugin is correctly registered with PlotManager.
Update the plots with data from the signals provided by PathViewPlugin.
Step-by-Step Implementation:
Register PathViewPlugin with PlotManager:

Ensure that PathViewPlugin is instantiated and registered with PlotManager.
This can be done in the main script where the PlotManager is initialized.
Update the plots with data from the signals:

Ensure that the PlotManager requests data from the plugin and updates the plots accordingly.

## Troubleshoot - issue with QCharts
Exception has occurred: ImportError
libQt6Charts.so.6: cannot open shared object file: No such file or directory
  File "/home/thh3/dev/DebugPlayer/project_root/gui/custom_plot_widget.py", line 8, in <module>
    from PySide6.QtCharts import QChart, QChartView, QLineSeries
  File "/home/thh3/dev/DebugPlayer/project_root/gui/main_window.py", line 3, in <module>
    from gui.custom_plot_widget import SpatialPlotWidget
  File "/home/thh3/dev/DebugPlayer/project_root/main.py", line 2, in <module>
    from gui.main_window import create_main_window
ImportError: libQt6Charts.so.6: cannot open shared object file: No such file or directory

ChatGPT said:
ChatGPT
The error ImportError: libQt6Charts.so.6: cannot open shared object file: No such file or directory indicates that the required QtCharts library for PySide6 is missing or not properly installed on your system.

How to Fix This:
To resolve this issue, you'll need to ensure that PySide6 and its QtCharts module are correctly installed. Here’s how you can do this:

1. Install or Reinstall PySide6:
If PySide6 is not installed or if the installation is missing components, you can install or reinstall it using pip:

bash
Copy code
pip install PySide6
This command installs the PySide6 library, which should include QtCharts.

2. Check System Libraries:
On Linux, missing libQt6Charts.so.6 might mean that the necessary Qt libraries are not properly linked or installed.

You may need to install the QtCharts development package. For example, if you use a package manager like apt:

```bash
Copy code
sudo apt-get install libqt6charts6 libqt6charts6-dev
```