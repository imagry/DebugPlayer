+---------------------------------------------+
|                 Main Window                 |
|---------------------------------------------|
| - setup_plot_docks()                        |
| - setup_menu_bar()                          |
| - setup_timestamp_slider()                  |
|---------------------------------------------|
| Purpose:                                    |
| 1. Initializes the app layout and components|
| 2. Creates and organizes plot widgets       |
| 3. Initializes Plot Manager and plugins     |
+---------------------------------------------+
                 |
                 | Calls
                 |
                 v
+---------------------------------------------+
|               Plot Manager                  |
|---------------------------------------------|
| Attributes:                                 |
| - plugins (dict): Stores all registered     |
|   plugins                                   |
| - signals (dict): Tracks signal-to-plot     |
|   assignments                               |
| - signal_plugins (dict): Tracks plugins     |
|   providing each signal                     |
|---------------------------------------------|
| Methods:                                    |
| - register_plugin(plugin_name, plugin):     |
|    1. Registers plugin in 'plugins'         |
|    2. Extracts signals and registers each   |
|       with register_signal()                |
|                                             |
| - register_signal(signal, signal_info) |
|    1. Stores signal type (temporal/spatial) |
|    2. Adds signal to 'signal_plugins' dict  |
|                                             |
| - assign_signal_to_plot(plot_widget, signal)|
|    1. Links signal to specific plot widget  |
|    2. Updates 'signals' dict                |
|                                             |
| - request_data(timestamp):                  |
|    1. Calls plugin for signal data          |
|    2. Sends data to update_signal()         |
|                                             |
| - update_signal(signal, data):              |
|    1. Sends data to registered plot widget  |
|    2. Calls plot_widget.update_data()       |
+---------------------------------------------+
                 |
                 | register_plugin()
                 |
                 v
+---------------------------------------------+
|                   Plugins                   |
|---------------------------------------------|
| Attributes:                                 |
| - signals (dict): Each plugin has signals   |
|   with callable methods to retrieve data    |
|---------------------------------------------|
| Methods:                                    |
| - get_data_for_timestamp(signal, timestamp):|
|    Fetches data for signal at timestamp     |
|---------------------------------------------|
| Purpose:                                    |
| 1. Provides data for specific signals       |
| 2. Interacts with Plot Manager for updates  |
+---------------------------------------------+
                 |
                 | Signal data retrieval
                 |
                 v
+---------------------------------------------+
|           Temporal Plot Widget              |
|---------------------------------------------|
| Attributes:                                 |
| - signals (list): Tracks active signals|
| - data_store (dict): Stores timestamped data|
| - curves (dict): Stores plot lines for each |
|   signal                                     |
|---------------------------------------------|
| Methods:                                    |
| - update_data(signal, value, timestamp):    |
|    1. Updates data_store with timestamped   |
|       data for each signal                  |
|    2. Updates plot line (curve) for signal  |
|    3. Redraws plot to reflect new data      |
|---------------------------------------------|
| Purpose:                                    |
| 1. Plots real-time temporal data            |
| 2. Receives updates via Plot Manager        |
+---------------------------------------------+
                 |
                 | update_signal()
                 |
                 v
+---------------------------------------------+
|           Spatial Plot Widget               |
|---------------------------------------------|
| Attributes:                                 |
| - signals (list): Tracks spatial       |
|   signals                                   |
| - data_store (dict): Stores position data   |
| - curves (dict): Stores plot lines for each |
|   signal                                     |
|---------------------------------------------|
| Methods:                                    |
| - update_data(signal, data):                |
|    1. Updates data_store with spatial data  |
|    2. Updates plot line for signal          |
|    3. Redraws plot                          |
|---------------------------------------------|
| Purpose:                                    |
| 1. Plots real-time spatial data             |
| 2. Receives updates via Plot Manager        |
+---------------------------------------------+



+---------------------------+
|        Main Window        |
|      (QMainWindow)        |
|                           |
| +-----------------------+ |   
| |    Plot Docks         | |  
| |                       | |    
| | +-------------------+ | |   +-----------------+
| | | CustomPlotWidget  |<----->|   Plot Manager   |
| | | Car Pose Plot     | | |   |  (PlotManager)   |
| | +-------------------+ | |   +--------^--------+
| | +-------------------+ | |            |
| | | CustomPlotWidget  | |<-------------+
| | | Car Signals Plot  | | |    Manages data for plots
| | +-------------------+ | |       and signals.
| +-----------------------+ |
|                           |
| +-----------------------+ |
| | Timestamp Slider      |<-----> Emits `timestamp_changed`
| | (QSlider)             | |      | Signals `PlotManager`
| +-----------------------+ |
|                           |
| +-----------------------+ |
| |    Menu Bar           |<-----> Toggle signal visibility
| |  (QMenuBar)           |<-------- via `QAction`
| +-----------------------+ |
+---------------------------+
