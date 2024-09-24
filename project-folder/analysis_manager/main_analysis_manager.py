# main_analysis_manager.py
import argparse

# %% Import libraries
import os
import sys

# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from init_utils import initialize_environment

# Initialize the environment
initialize_environment()

import matplotlib
# matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'
from analysis_manager.cross_analysis import cross_analysis
from analysis_manager.data_preparation import load_data_for_trip
from analysis_manager.config import initialize_parameters

import tkinter as tk
from tkinter import Menu, font

from file_menu import create_file_menu, create_edit_menu, update_selection_labels

# Placeholder state object
class State:
    def __init__(self):
        self.trips_folder = None
        self.selected_trip = None

state = State()

def split_trip_path(trip_path):
    """
    Splits the trip path into trips_folder and selected_trip, ensuring consistent results
    for paths with or without trailing slashes.

    Args:
        trip_path (str): The path to the trip.

    Returns:
        tuple: A tuple containing trips_folder and selected_trip.
    """
    # Normalize the path to remove any trailing slashes
    normalized_path = os.path.normpath(trip_path)
    
    # Split the normalized path
    trips_folder, selected_trip = os.path.split(normalized_path)
    
    return trips_folder, selected_trip

# Initialize state by reading the environment variable
def init_state(trip_dir=None):
    if trip_dir is not None:
        # split trip_dir into trips_folder and selected_trip - trip_dir parent folder is trips_folder
        state.trips_folder, state.selected_trip  = split_trip_path(trip_dir)
        return
    
    trip_path_env = os.getenv('OFFLINE_DATA_PATH_URBAN')
    
    if trip_path_env and os.path.exists(trip_path_env):
        default_trips_folder = os.path.dirname(trip_path_env)
        state.trips_folder = default_trips_folder
        state.selected_trip = trip_path_env
        print(f"Using environment variable for trips folder: {default_trips_folder}")
        print(f"Default selected trip: {trip_path_env}")
    else:
        state.trips_folder = os.path.expanduser("~/data/trips")
        print(f"Default trips folder: {state.trips_folder}")

# Function to be called when the Play button is pressed
def on_play_button_pressed():
    params = initialize_parameters()
    trip_path = os.path.join(state.trips_folder, state.selected_trip)  
    
    df_list, ClassObjList = load_data_for_trip(trip_path)
    
    cross_analysis(df_list, ClassObjList, zero_time=False)

def refresh_callback(selected_trip):
    print(f"Refreshing with selected trip: {selected_trip}")

#%% Main function to execute the process
def main(trip_dir = None):
        
      # Create an argument parser
    parser = argparse.ArgumentParser(description="Main Analysis Manager")
    
    # Add the --trip argument
    parser.add_argument('--trip', type=str, help='Path to the trip file')
    
    # Parse the command-line arguments
    args = parser.parse_args()
                  
    root = tk.Tk()
    root.title("Analysis Manager")
    root.geometry("800x600")
    
    custom_font = font.Font(family="Helvetica", size=12)
    Run_font = font.Font(family="Helvetica", size=22)
    menu_bar = Menu(root, font=custom_font)
           
    create_file_menu(menu_bar, root, state, refresh_callback, custom_font)
    create_edit_menu(menu_bar, custom_font)
    
    root.config(menu=menu_bar)
    
    play_button = tk.Button(root, text="RUN", command=on_play_button_pressed, font=Run_font)
    play_button.pack(pady=20)

    # Check if the --trip flag is provided
    if args.trip:
        trip_dir = args.trip
    else:
        trip_dir = None   
        
    init_state(trip_dir)
    
    update_selection_labels(root, state)
    
    root.mainloop()

if __name__ == "__main__":
                      
    main()