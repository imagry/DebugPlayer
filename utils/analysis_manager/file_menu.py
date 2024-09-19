# file_menu.py
import os
import sys
import tkinter as tk
from tkinter import Menu, font, filedialog

def create_file_menu(menu_bar, root, state, refresh_callback, custom_font):
    file_menu = Menu(menu_bar, tearoff=0, font=custom_font)
    file_menu.add_command(label="Open Trips Folder", command=lambda: select_trips_folder(state), font=custom_font)
    file_menu.add_command(label="Select Trip", command=lambda: select_trip(state, refresh_callback), font=custom_font)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit, font=custom_font)
    menu_bar.add_cascade(label="File", menu=file_menu)

def create_edit_menu(menu_bar, custom_font):
    edit_menu = Menu(menu_bar, tearoff=0, font=custom_font)
    edit_menu.add_command(label="Undo", command=undo_action, font=custom_font)
    edit_menu.add_command(label="Redo", command=redo_action, font=custom_font)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

def select_trips_folder(state):
    initial_dir = state.trips_folder if state.trips_folder else os.path.expanduser("~/data/trips")
    folder_selected = filedialog.askdirectory(initialdir=initial_dir)
    
    if folder_selected:
        state.trips_folder = folder_selected
        print(f"Selected trips folder: {folder_selected}")
    else:
        print("No folder selected.")

def select_trip(state, refresh_callback):
    trips_folder = os.path.expanduser(state.trips_folder)
    
    if not os.path.exists(trips_folder):
        print(f"Directory does not exist: {trips_folder}")
        return

    trips = [trip for trip in os.listdir(trips_folder) if os.path.isdir(os.path.join(trips_folder, trip))]

    if trips:
        selection_window = tk.Toplevel()
        selection_window.title("Select Trip")

        custom_font = font.Font(family="Helvetica", size=12)

        label = tk.Label(selection_window, text="Select a trip from the list:", font=custom_font)
        label.pack(pady=10)

        listbox = tk.Listbox(selection_window, font=custom_font)
        for trip in trips:
            listbox.insert(tk.END, trip)
        listbox.pack(pady=10)

        def on_select():
            selected_index = listbox.curselection()
            if selected_index:
                state.selected_trip = trips[selected_index[0]]
                print(f"Selected trip: {state.selected_trip}")
                refresh_callback(state.selected_trip)
                selection_window.destroy()
            else:
                print("No trip selected.")

        select_button = tk.Button(selection_window, text="Select", command=on_select, font=custom_font)
        select_button.pack(pady=10)
    else:
        print("No trips available in the selected folder.")

def undo_action():
    pass

def redo_action():
    pass