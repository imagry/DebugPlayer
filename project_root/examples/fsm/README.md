# Requirements

### Creating conda environment from YML requirments
conda env create -f environment.yml

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

# Running the FSM tool:
## Standalone mode:
### 1. Update the path to the fsm log file in fsm_main.py and run it from fsm_main.py.

## Connect to other tool using time_stamp synchronization
It will depend on how you want to embed it, but essentially here are some pointers that will help:
### 1. fsm_main_window.py 
#### 1.1 look at  'main_layout' this is the layout you will want to embed in your other view
#### 1.2 self.slider.valueChanged.connect(self.update_fsm_state) - this is where the slider updates the FSM and the signals. 
#### 1.2 def update_fsm_state(self, index) - this is the updating mechanism. It currently uses the index so you will need to update the header to accept time stamp instead of index and later on find the index closest to the time_stamp, or you can do it by wrapping this function with your own and just pass index to this callback. 


### 2. 


