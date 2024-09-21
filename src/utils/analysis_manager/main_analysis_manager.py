# main_analysis_manager.py

# %% Import libraries
import os
import sys

# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.init_utils import initialize_environment

# Initialize the environment
initialize_environment()

import matplotlib
# matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'
from analysis_manager.cross_analysis import cross_analysis
from analysis_manager.data_preparation import load_data_for_trip
from analysis_manager.config import initialize_parameters

import tkinter as tk
from tkinter import Menu, font

from file_menu import create_file_menu, create_edit_menu

# Placeholder state object
class State:
    def __init__(self):
        self.trips_folder = None
        self.selected_trip = None

state = State()

# Initialize state by reading the environment variable
def init_state():
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
def main():
    root = tk.Tk()
    root.title("Analysis Manager")
    root.geometry("800x600")
    
    custom_font = font.Font(family="Helvetica", size=12)
    
    menu_bar = Menu(root, font=custom_font)
    
    create_file_menu(menu_bar, root, state, refresh_callback, custom_font)
    create_edit_menu(menu_bar, custom_font)
    
    root.config(menu=menu_bar)
    
    play_button = tk.Button(root, text="Play", command=on_play_button_pressed, font=custom_font)
    play_button.pack(pady=20)
    
    init_state()
    
    root.mainloop()

if __name__ == "__main__":
    main()