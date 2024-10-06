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
conda env export --no-builds | grep -v "prefix" > environment.yml

### Creating conda environment from YML requirments
conda env create -f environment.yml

### Running the package
```bash
./main --trip1 /home/thh3/data/trips/nissan/2024-10-01T13_46_59/
```



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
                car_pose_plot = CustomPlotWidget(signal_names=["car_pose(t)", "route"])
                route_plot = CustomPlotWidget(signal_names=["route"])

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

