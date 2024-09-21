# interactivity.py

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
import tkinter as tk
from tkinter import filedialog
import os
import time
import numpy as np

# from config import increment
class SharedState:
    def __init__(self, increment, trips_folder="default/path/to/trips"):
        self.increment = increment
        self.trips_folder = trips_folder
        self.selected_trip = None
        self.playback_active = False
        self.paused = False

def setup_trips_folder_button(fig, state):
    """Create and configure a button to select the trips folder."""
    def select_trips_folder(event):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        selected_folder = filedialog.askdirectory(initialdir=state.trips_folder, title="Select Trips Folder")
        if selected_folder:
            state.trips_folder = selected_folder
            print(f"Trips folder selected: {state.trips_folder}")
    
    # Create the button for selecting trips folder
    ax_button_trips_folder = plt.axes([0.05, 0.85, 0.2, 0.05])  # Position of the button
    button_trips_folder = Button(ax_button_trips_folder, 'Select Trips Folder')
    button_trips_folder.on_clicked(select_trips_folder)
    
def setup_trip_selection_button(fig, state, refresh_callback):
    """Create and configure a button to select a specific trip from the folder."""
    def select_trip(event):
        trips = [trip for trip in os.listdir(state.trips_folder) if os.path.isdir(os.path.join(state.trips_folder, trip))]
        
        if trips:
            print("Available trips:")
            for i, trip in enumerate(trips):
                print(f"{i + 1}. {trip}")
            
            # For simplicity, we'll use a console-based selection
            trip_index = int(input("Enter the number of the trip to select: ")) - 1
            if 0 <= trip_index < len(trips):
                state.selected_trip = trips[trip_index]
                print(f"Selected trip: {state.selected_trip}")
                refresh_callback(state.selected_trip)
            else:
                print("Invalid selection.")
        else:
            print("No trips available in the selected folder.")
    
    # Create the button for selecting a specific trip
    ax_button_trip_selection = plt.axes([0.3, 0.85, 0.2, 0.05])  # Position of the button
    button_trip_selection = Button(ax_button_trip_selection, 'Select Trip')
    button_trip_selection.on_clicked(select_trip)

            
def old_setup_slider(fig, cp_time_seconds):
    """Create and configure the slider."""
    # Placing the slider below the plots, leaving space for buttons below it
    ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])  # Manual positioning
    slider = Slider(ax_slider, 'Time [s]', cp_time_seconds[0], cp_time_seconds[-1], valinit=cp_time_seconds[0])
    return slider


def setup_slider(fig, cp_time_seconds, state):
    """Create and configure a slider."""
    ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
    # slider = Slider(ax_slider, 'Value', 0, 100, valinit=0, valstep=1)
    slider = Slider(ax_slider, 'Time [s]', cp_time_seconds[0], cp_time_seconds[-1], valinit=cp_time_seconds[0])
    def on_key(event):
        if event.key == 'a':
            state.playback_active = not state.playback_active
            if state.playback_active:
                playback()
        elif event.key == ' ':
            state.paused = not state.paused

    def playback():
        while state.playback_active:
            if not state.paused:
                current_val = slider.val
                if current_val < slider.valmax:
                    new_val = max(slider.val + state.increment[0] / 1000.0, slider.valmin)
                    slider.set_val(new_val)
                    plt.draw()
                    time.sleep(0.02)  # 20ms pause between frames
                else:
                    state.playback_active = False
            plt.pause(0.01)  # Allow GUI to update

    fig.canvas.mpl_connect('key_press_event', on_key)

    return slider

def setup_buttons(fig, slider, increment):
    """Create and configure the 'BWD' and 'FWD' buttons below the slider."""
    
    def move_slider_bwd(event, increment):
        # Move the slider backward by the increment (converted from ms to s)
        new_val = max(slider.val - increment[0] / 1000.0, slider.valmin)
        slider.set_val(new_val)
    
    # # Create Backward Button
    # ax_button_bwd = plt.axes([0.2, 0.05, 0.1, 0.04])  # Positioned below the slider
    # button_bwd = Button(ax_button_bwd, 'BWD')
    # button_bwd.on_clicked(lambda event: move_slider_bwd(event, increment))

    def move_slider_fwd(event, increment):
        # Move the slider forward by the increment (converted from ms to s)
        new_val = min(slider.val + increment[0] / 1000.0, slider.valmax)
        slider.set_val(new_val)
    
    # # Create Forward Button
    # ax_button_fwd = plt.axes([0.35, 0.05, 0.1, 0.04])  # Positioned next to BWD
    # button_fwd = Button(ax_button_fwd, 'FWD')
    # button_fwd.on_clicked(lambda event: move_slider_fwd(event, increment))   

    def on_key_press(event, increment):
        if event.key == 'right':
            move_slider_fwd(event, increment)
        elif event.key == 'left':
            move_slider_bwd(event, increment)
        elif event.key == 'up':
            increment[0] = min(increment[0]*1.1, 10.0*1000)  # Reduce increment by 10% of its previous state 
            print('up %s' % increment[0])
        elif event.key == 'down':
            increment[0] = max(increment[0]*0.9, 1.0 / 1000)  # Reduce increment by 10% of its previous state 
            print('down %s' % increment[0])
            
    # Connect the key press event to the handler            
    fig.canvas.mpl_connect('key_press_event',  lambda event:on_key_press(event, increment))
            
def update_increment(new_value, increment):
        increment[0] = new_value
        
def setup_increment_input(fig, initial_increment, update_increment_callback):
    """Create and configure a text box for increment input (1 ms to 1,000,000 ms)."""
    ax_textbox = plt.axes([0.5, 0.05, 0.2, 0.04])  # Positioned next to the FWD button
    text_box = TextBox(ax_textbox, 'Increment (ms)', initial=str(initial_increment))
        
    def validate_increment(text):
        try:
            value = int(text)
            if 1 <= value <= 1000000:
                update_increment_callback(value)  # Update the increment value
            else:
                print("Invalid value! Must be between 1 and 1,000,000 ms.")
        except ValueError:
            print("Invalid input! Please enter an integer.")

    text_box.on_submit(validate_increment)
    return text_box

def on_click_event(event, ax_steering, ax_steering_rate, ax_speed, slider, cp_time_seconds):
    """Handle mouse click events to update plots."""
    if event.inaxes in [ax_steering, ax_steering_rate, ax_speed]:
        clicked_time = event.xdata
        slider.set_val(clicked_time)

def on_drag_event(event, slider, cp_time_seconds):
    """Handle mouse dragging events to update plots while moving the cursor."""
    if event.inaxes and event.button == 1:  # Ensure left mouse button is pressed
        # check if the even inaxes title is of ax_steering or ax_steering_rate or ax_speed
        if 'Steering' in event.inaxes.get_title():
            dragged_time = event.xdata
            # Update the slider to reflect the dragged time
            slider.set_val(dragged_time)

def setup_mouse_events(fig, slider, cp_time_seconds, ax_steering, ax_steering_rate, ax_speed):
    """Set up mouse events for clicking, dragging, and releasing."""
    # Register click event
    fig.canvas.mpl_connect('button_press_event', lambda event: on_click_event(event, ax_steering, ax_steering_rate, ax_speed, slider, cp_time_seconds))
    
    # Register motion event (for dragging with left button pressed)
    fig.canvas.mpl_connect('motion_notify_event', lambda event: on_drag_event(event, slider, cp_time_seconds))
    
    

    
