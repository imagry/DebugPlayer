from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QVBoxLayout, QComboBox
from PySide6.QtWidgets import QListWidget, QPushButton, QMessageBox, QCheckBox
from PySide6.QtCore import Qt
from gui.custom_plot_widget import CustomPlotWidget
from gui.timestamp_slider import TimestampSlider
from core.plot_manager import PlotManager
from gui.menu_bar import setup_menu_bar


def create_main_window(plot_manager):
    win = QMainWindow()  # Create the main window object
    win.resize(1200, 800)  # Resize the main window
    win.setWindowTitle('Motion Planning Playback Debug Tool')  # Set the window title
  
    current_timestamp = 0  # Initialize the current timestamp

    
    # Save the initial layout
    def save_layout():
        win.saved_layout = win.saveState()

    # Restore the saved layout
    def restore_layout():
        if hasattr(win, 'saved_layout'):
            win.restoreState(win.saved_layout)
                        
   # Add a method to toggle the control panel
    def toggle_control_panel():
        if signal_selector_dock.isHidden():
            signal_selector_dock.show()
        else:
            signal_selector_dock.hide()
    
    # Attach toggle_control_panel to the window object so the menu can access it
    win.toggle_control_panel = toggle_control_panel                
    # Attach restore_layout and save_layout to window object
    win.save_layout = save_layout
    win.restore_layout = restore_layout
    
    # Create a dock for signal and plot selection
    signal_selector_dock = QDockWidget("Signal & Plot Selector", win)
    signal_selector_dock.setObjectName("SignalPlotSelectorDock")  # Set object name
    signal_selector_widget = QWidget()
    signal_selector_layout = QVBoxLayout(signal_selector_widget)
    
    # Combo box for selecting signals
    signal_selector = QComboBox()
    signal_selector.addItems(list(plot_manager.signal_plugins.keys()))  # Populate with available signals
    signal_selector_layout.addWidget(signal_selector)
       
    # Add the signal selector widget to the dock
    signal_selector_dock.setWidget(signal_selector_widget)
    signal_selector_dock.setFixedWidth(200)
    win.addDockWidget(Qt.LeftDockWidgetArea, signal_selector_dock)

    # Create and wrap the plots in QDockWidgets
    car_pose_plot = CustomPlotWidget(signal_names=[])
    car_signals_plot = CustomPlotWidget(signal_names=[])
    
    car_pose_dock = QDockWidget("Car Pose Plot", win)
    car_pose_dock.setObjectName("CarPosePlotDock")  # Set object name
    car_pose_dock.setWidget(car_pose_plot) # wrap the plot in a dock QDockWidget
    win.addDockWidget(Qt.RightDockWidgetArea, car_pose_dock) # add the dock to the main window
    
    car_signals_dock = QDockWidget("Car Signals", win)
    car_signals_dock.setObjectName("CarSignalsPlotDock")  # Set object name    
    car_signals_dock.setWidget(car_signals_plot) # wrap the plot in a dock QDockWidget
    win.addDockWidget(Qt.RightDockWidgetArea, car_signals_dock) # add the dock to the main window    
        
    plot_manager.register_plot(car_pose_plot)
    plot_manager.register_plot(car_signals_plot)
    
    # Combo box for selecting plots
    plot_selector = QComboBox()
    plot_selector.addItem("Car Pose Plot")
    plot_selector.addItem("Car Signals Plot")
    signal_selector_layout.addWidget(plot_selector)
    # win.addDockWidget(Qt.LeftDockWidgetArea, plot_selector)

    # TODO: Have this a generic option to add a new plot from the menu

    def get_selected_plot():
        """Get the selected plot based on user choice from plot_selector."""
        selected_plot = plot_selector.currentText()
        if selected_plot == "Car Pose Plot":
            return car_pose_plot
        elif selected_plot == "Car Signals Plot":
            return car_signals_plot
        return None
        
    def get_selected_signal():
        """Get the selected signal based on user choice from signal_selector."""
        return signal_selector.currentText()
    
    def update_timestamp(new_timestamp):
        nonlocal current_timestamp
        current_timestamp = new_timestamp  # Update the current timestamp
        plot_manager.request_data(current_timestamp)
            
    def add_signal_checkbox(plot_widget, signal_name):
        """Create a checkbox to control the visibility of the signal."""
        checkbox = QCheckBox(signal_name)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda: plot_widget.toggle_signal_visibility(signal_name, checkbox.isChecked()))
        signal_selector_layout.addWidget(checkbox)
        
    # Define the add_signal method (if needed separately for buttons)
    def add_signal():
        nonlocal current_timestamp  # Reference the current timestamp variable
        selected_signal = get_selected_signal()
        target_plot = get_selected_plot()  # Get the selected plot
        if not target_plot:
            return

        available_signals = [s for s in plot_manager.signal_plugins.keys() if s not in target_plot.signal_names]
        if not available_signals:
            QMessageBox.information(win, "No Signals", "No available signals to add.")
            return
        
        # Prevent adding the same signal multiple times
        if selected_signal in target_plot.signal_names:
            QMessageBox.information(win, "Signal Already Added", f"{selected_signal} is already assigned to the plot.")
            return  # Do nothing if the signal is already assigned
        
        # Assign the signal to the selected plot               
        target_plot.signal_names.append(selected_signal)
        plot_manager.assign_signal_to_plot(target_plot, selected_signal)
        
        # Use the current timestamp instead of resetting to 0       
        plot_manager.request_data(current_timestamp)
        target_plot.add_signal_to_legend(selected_signal)
        
        # TODO: Have signals selection be as a drop down menu in the plot itself where each plot can only have 
        # signals that are available fot the plot type, e.g. spatial, tempporal, etc.

        # Add a checkbox for signal visibility control
        add_signal_checkbox(target_plot, selected_signal)
        
            
    # Define the remove_signal method
    def remove_signal():
        target_plot = get_selected_plot()  # Get the selected plot
        if not target_plot or not target_plot.signal_names:
            QMessageBox.information(win, "No Signals", "No signals to remove.")
            return

        signal_to_remove = get_selected_signal()
        target_plot.signal_names.remove(signal_to_remove)
        plot_manager.remove_signal_from_plot(target_plot, signal_to_remove)
        target_plot.plot_data()

        if signal_to_remove in target_plot.legend_items:
            legend_checkbox = target_plot.legend_items.pop(signal_to_remove)
            target_plot.legend.removeItem(legend_checkbox)
   
    # Attach these methods to the window so that menu_bar.py can access them
    win.add_signal = add_signal
    win.remove_signal = remove_signal
       
    # Set up the menu bar
    setup_menu_bar(win)  # Call the setup function from menu_bar.py   

    # Create Car Pose Plot as d2
    d2 = QDockWidget("Car Pose Plot", win)
    d2.setObjectName("CarPosePlotDock2")  # Set object name for second dock
    d2.setWidget(car_pose_plot)

    # Create Route Plot as d3
    d3 = QDockWidget("Route Plot", win)
    d3.setObjectName("RoutePlotDock")  # Set object name    
    d3.setWidget(car_signals_plot)

    win.addDockWidget(Qt.RightDockWidgetArea, d2)
    win.addDockWidget(Qt.RightDockWidgetArea, d3)
    
    # Make sure d3 is below d2 (vertically stacked)
    win.splitDockWidget(d2, d3, Qt.Vertical)
       
    # Fetch timestamps from the PlotManager
    # Assuming "timestamps" is a signal provided by one of the plugins
    if "timestamps" in plot_manager.signal_plugins:
        # Get the "timestamps" signal from the CarPosePlugin
        timestamps = plot_manager.plugins["CarPosePlugin"].signals["timestamps"]
        plugin_name = plot_manager.signal_plugins["timestamps"][0]
    else:
        timestamps = []  # Fallback in case no plugin provides timestamps
    # Create TimestampSlider as d4
    d4 = QDockWidget("Timestamp Slider", win)
    d4.setObjectName("TimestampSliderDock")  # Set object name    
    slider = TimestampSlider(plot_manager, timestamps)  # Initialize slider with timestamps
    slider.timestamp_changed.connect(update_timestamp)  # Connect the slider to the timestamp update
    d4.setWidget(slider)
    d4.setFixedHeight(100)  # Set a height for the slider dock
    win.addDockWidget(Qt.BottomDockWidgetArea, d4)

    save_layout()  # Save the default layout state after initialization
    
    return win, plot_manager  # Return the window and the PlotManager

# TODO: Have signals selection be as a drop down menu in the plot itself where each plot can only have signals that are available fot the plot type, e.g. spatial, tempporal, etc.    
# TODO: Add to each signal an attribute whether it is a spatial or temporal signal
# TODO: 
# 1. Box Zoom and Pan for the plots
# 2. Avoide reseting of slider when loading a signal
# 3. Add a timestamp to the slider
# 4. Add a play button to the slider
# 5. Add a speed control to the slider
# 6. Add a pause button to the slider
# 7. Add a stop button to the slider
# 8. Add a reset button to the slider
# 9. Add a save button to the slider
# 10. Add a load button to the slider
# 11. Add a button to select a specific timestamp
# 12. Add a button to select a specific range
# 13. Add a button to select a specific signal
# 14. Add a button to select a specific plot
# 15. Add a button to select a specific plugin
# 16. Add a button to select a specific data source
# 17. Add a button to select a specific data type
# 18. Add a button to select a specific data format
# 19. Add a button to select a specific data structure
# 20. Add a button to select a specific data source type
# 21. Add a button to select a specific data source format
# 22. Add a button to select a specific data source structure
# 23. Add a button to select a specific data source type
# 24. Add a button to select a specific data source format
# 25. Add a button to select a specific data source structure
# 26. Add a button to select a specific data source type
# 27. Add a button to select a specific data source format
# 28. Add a button to select a specific data source structure
# 29. Add a button to select a specific data source type
# 30. Add a button to select a specific data source format
# 31. Add a button to select a specific data source structure
# 32. Add a button to select a specific data source type
# 33. Add a button to select a specific data source format
# 34. Add a button to select a specific data source structure
# 35. Add a button to select a specific data source type
# 36. Add a button to select a specific data source format
# 37. Add a button to select a specific data source structure
# 38. Add a button to select a specific data



# # Create a QListWidget to display assigned signals
#     assigned_signals_list = QListWidget()
#     signal_selector_layout.addWidget(assigned_signals_list)

#     # Button to remove the selected signal
#     remove_signal_button = QPushButton("Remove Selected Signal")
#     signal_selector_layout.addWidget(remove_signal_button)
    
#     # Handle signal assignment to the selected plot
#     def assign_signal_to_plot():
#         selected_signal = signal_selector.currentText()  # Get the selected signal
#         selected_plot = plot_selector.currentText()  # Get the selected plot

#         # Determine which plot to assign the signal to
#         if selected_plot == "Car Pose Plot":
#             target_plot = car_pose_plot
#         elif selected_plot == "Car Signals Plot":
#             target_plot = car_signals_plot
#         else:
#             return  # If an unknown plot is selected, do nothing

#         # Assign the signal to the selected plot
#         target_plot.signal_names.append(selected_signal)
#         assigned_signals_list.addItem(f"{selected_plot}: {selected_signal}")  # Add to list for removal UI
#         plot_manager.assign_signal_to_plot(target_plot, selected_signal)
#         plot_manager.request_data(0)  # Request data for the initial timestamp

#     # Handle signal removal
#     def remove_signal_from_plot():
#         selected_item = assigned_signals_list.currentItem()
#         if selected_item:
#             text = selected_item.text()
#             selected_plot_name, selected_signal = text.split(": ")

#             # Determine which plot to remove the signal from
#             if selected_plot_name == "Car Pose Plot":
#                 target_plot = car_pose_plot
#             elif selected_plot_name == "Car Signals Plot":
#                 target_plot = car_signals_plot
#             else:
#                 return  # If an unknown plot is selected, do nothing

#             # Remove the signal from the plot and update the UI
#             if selected_signal in target_plot.signal_names:
#                 target_plot.signal_names.remove(selected_signal)
#                 assigned_signals_list.takeItem(assigned_signals_list.row(selected_item))  # Remove from list
#                 plot_manager.remove_signal_from_plot(target_plot, selected_signal)  # Call manager to handle removal
#                 target_plot.plot_data()  # Re-draw plot without the removed signal

#     # Connect signal assignment and removal to buttons
#     signal_selector.currentIndexChanged.connect(assign_signal_to_plot)
#     plot_selector.currentIndexChanged.connect(assign_signal_to_plot)
#     remove_signal_button.clicked.connect(remove_signal_from_plot)    
