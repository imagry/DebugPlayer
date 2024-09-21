# cross_analysis.py

from analysis_manager.data_preparation import merge_and_prepare_data, prepare_time_data
from plotting import setup_figure, plot_time_series, plot_car_pose
from interactivity import setup_slider, setup_buttons, setup_increment_input, setup_mouse_events, update_increment, setup_trips_folder_button, setup_trip_selection_button, SharedState
from utils import update_plots
import matplotlib.pyplot as plt
from analysis_manager.config import DataFrameType, ClassObjType
from analysis_manager.data_preparation import load_data_for_trip
import os

def cross_analysis(df_list, ClassObjList, zero_time=False):
        
    # Merge and prepare data
    df = merge_and_prepare_data(df_list[DataFrameType.STEERING], df_list[DataFrameType.CAR_POSE])
    cp_time_seconds, str_time_seconds = prepare_time_data(df_list[DataFrameType.STEERING], df_list[DataFrameType.CAR_POSE], zero_time)        
    try:
        PathObj = ClassObjList[ClassObjType.PATH]
    except:
        PathObj = None
    try:
        PathExtractionObj = ClassObjList[ClassObjType.PATH_EXTRACTION]
    except:
        PathExtractionObj = None
    try:
        PathAdjustmentObj = ClassObjList[ClassObjType.PATH_ADJUSTMENT]
    except:
        PathAdjustmentObj = None
    
    # Setup figure and subplots
    fig, ax_steering, ax_steering_rate, ax_speed, ax_pose = setup_figure()

    # Plot the time-series data
    plot_time_series(ax_steering, ax_steering_rate, df_list[DataFrameType.STEERING], str_time_seconds)

    # Initialize markers
    marker_steering, = ax_steering.plot([], [], 'go', label='Current Time', markersize=10)
    marker_steering_rate, = ax_steering_rate.plot([], [], 'mo', label='Current Time', markersize=10)

    # Initialize SharedState
    from config import increment  # Assuming this was an integer
    state = SharedState(increment=[increment])
        
    # Setup slider
    slider = setup_slider(fig, cp_time_seconds, state)

    # slider = setup_slider(fig, cp_time_seconds)

    # Setup buttons (BWD, FWD) and increment input field
    setup_buttons(fig, slider, state.increment)

    # Define a refresh callback to reload data when a trip is selected
    def refresh_data(selected_trip):
        trip_path = os.path.join(state.trips_folder, selected_trip)
        print(f"Refreshing data for trip: {trip_path}")
        # Here you would reload the data for the selected trip and update the plots
        new_df_steering, new_df_car_pose = load_data_for_trip(trip_path)  # Implement this
        cross_analysis(new_df_steering, new_df_car_pose)  # Recursively reload the analysis
        
    # Setup mouse events for click and dragging
    setup_mouse_events(fig, slider, cp_time_seconds, ax_steering, ax_steering_rate, ax_speed)

    # Slider update function
    # Todo:
    # change def update(val):
        # Update the plots based on the slider value
    # and definbe update_plots function
    # update_plots(...)
    # slider.on_changed(update)

    slider.on_changed(lambda val: update_plots(val, cp_time_seconds, str_time_seconds, df_list[DataFrameType.STEERING],
                                               ax_pose, marker_steering, marker_steering_rate,
                                               df_list[DataFrameType.CAR_POSE]['cp_x'],
                                               df_list[DataFrameType.CAR_POSE]['cp_y'],
                                               df_list[DataFrameType.CAR_POSE]['cp_yaw_deg'],
                                               PathObj, PathExtractionObj, PathAdjustmentObj))

    # Show the plot
    plt.show()

