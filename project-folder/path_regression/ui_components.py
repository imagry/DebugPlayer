# ui_components.py
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
import pyqtgraph as pg
from functools import partial
from data_handlers import load_trip_path
from plot_functions import update_plot, save_figure, calculate_virtual_path


def create_main_window():
    """Create the main window's control UI components, but no window or layout."""

        # Create a widget for the controls
    controls_widget = QtWidgets.QWidget()
    controls_layout = QtWidgets.QVBoxLayout()
    controls_widget.setLayout(controls_layout)
    
    # Add UI elements for the first trip
    controls_layout.addWidget(QtWidgets.QLabel('Trip 1 Settings'))
    load_button1 = QtWidgets.QPushButton('Load Trip 1 Path')
    controls_layout.addWidget(load_button1)

    # Add UI elements for the second trip
    controls_layout.addWidget(QtWidgets.QLabel('Trip 2 Settings'))
    load_button2 = QtWidgets.QPushButton('Load Trip 2 Path')
    controls_layout.addWidget(load_button2)    

    # Add buttons to compare paths
    compare_button = QtWidgets.QPushButton('Compare Paths')
    controls_layout.addWidget(compare_button) 
    
    # Plot settings
    plot_settings_label = QtWidgets.QLabel('Plot Settings')
    plot_settings_label.setStyleSheet("font-weight: bold;")
    controls_layout.addWidget(plot_settings_label)
    
        # Controls for line width
    line_width_label = QtWidgets.QLabel('Line Width:')
    line_width_spin = QtWidgets.QSpinBox()
    line_width_spin.setRange(1, 10)
    line_width_spin.setValue(1)
    controls_layout.addWidget(line_width_label)
    controls_layout.addWidget(line_width_spin)

    # Controls for marker size
    marker_size_label = QtWidgets.QLabel('Marker Size:')
    marker_size_spin = QtWidgets.QSpinBox()
    marker_size_spin.setRange(1, 20)
    marker_size_spin.setValue(5)
    controls_layout.addWidget(marker_size_label)
    controls_layout.addWidget(marker_size_spin)

    # Controls for colors_num
    colors_num_label = QtWidgets.QLabel('Colors Num:')
    colors_num_spin = QtWidgets.QSpinBox()
    colors_num_spin.setRange(1, 8)
    colors_num_spin.setValue(1)
    controls_layout.addWidget(colors_num_label)
    controls_layout.addWidget(colors_num_spin)
    
     # Add option to choose colors in the palette per the number of colors selected
    colors_palette_label = QtWidgets.QLabel('Colors Palette:')
    colors_palette_list = QtWidgets.QListWidget()
    colors_palette_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
    colors_palette_list.addItems(['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
    controls_layout.addWidget(colors_palette_label)
    controls_layout.addWidget(colors_palette_list)
    
    # Controls for turning on/off the display of trips and car pose
    display_trips1_checkbox = QtWidgets.QCheckBox('Display Trip 1')
    display_trips1_checkbox.setChecked(True)
    controls_layout.addWidget(display_trips1_checkbox)

    display_trips2_checkbox = QtWidgets.QCheckBox('Display Trip 2')
    display_trips2_checkbox.setChecked(True)
    controls_layout.addWidget(display_trips2_checkbox)

    display_carpose_checkbox = QtWidgets.QCheckBox('Display Car Pose')
    display_carpose_checkbox.setChecked(True)
    controls_layout.addWidget(display_carpose_checkbox)
    
    delta_t_label = QtWidgets.QLabel('delta_t_sec:')
    delta_t_input = QtWidgets.QLineEdit('0.1')
    controls_layout.addWidget(delta_t_label)
    controls_layout.addWidget(delta_t_input)

    pts_before_label = QtWidgets.QLabel('pts_before:')
    pts_before_spin = QtWidgets.QSpinBox()
    pts_before_spin.setRange(0, 100)
    pts_before_spin.setValue(0)
    controls_layout.addWidget(pts_before_label)
    controls_layout.addWidget(pts_before_spin)

    pts_after_label = QtWidgets.QLabel('pts_after:')
    pts_after_spin = QtWidgets.QSpinBox()
    pts_after_spin.setRange(0, 100)
    pts_after_spin.setValue(0)
    controls_layout.addWidget(pts_after_label)
    controls_layout.addWidget(pts_after_spin)
    
    
    # Add a button to run analysis
    run_button = QtWidgets.QPushButton('Run')
    controls_layout.addWidget(run_button)

    # Add a button to update the plot
    update_plot_button = QtWidgets.QPushButton('Update Plot')
    controls_layout.addWidget(update_plot_button)
    
    # Add a button to save the figure
    save_button = QtWidgets.QPushButton('Save Figure')
    controls_layout.addWidget(save_button)
    
        # Return just the widgets (not the main window) for use in docks
    ui_elements = {
        'line_width_spin': line_width_spin,
        'marker_size_spin': marker_size_spin,
        'colors_num_spin': colors_num_spin,
        'colors_palette_list': colors_palette_list,
        'delta_t_input': delta_t_input,
        'pts_before_spin': pts_before_spin,
        'pts_after_spin': pts_after_spin,
        'run_button': run_button,
        'update_plot_button': update_plot_button,
        'save_button': save_button,
        'load_button1': load_button1,
        'load_button2': load_button2,
        'compare_button': compare_button,
    }

    ui_display_elements = {
        'display_trips1_checkbox': display_trips1_checkbox,
        'display_trips2_checkbox': display_trips2_checkbox,
        'display_carpose_checkbox': display_carpose_checkbox
    }
    
    return controls_widget, ui_elements, ui_display_elements
    

def connect_signals(run_button, load_button1, load_button2, update_plot_button, save_button, ui_elements,
                    main_scope, ui_display_elements, display_trips1_checkbox_button, display_trips2_checkbox_button, display_carpose_checkbox_button):
    """Connect UI signals to their respective slots."""
    run_button.clicked.connect(partial(handle_calculate_virtual_path, ui_elements, ui_display_elements, main_scope))
    load_button1.clicked.connect(partial(handle_load_trip_path1, ui_elements, main_scope))
    load_button2.clicked.connect(partial(handle_load_trip_path2, ui_elements, main_scope))
    update_plot_button.clicked.connect(partial(update_plot, ui_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2')))
    save_button.clicked.connect(partial(save_figure, ui_elements))

    display_trips1_checkbox_button.clicked.connect(partial(update_plot, ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2')))
    display_trips2_checkbox_button.clicked.connect(partial(update_plot, ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2')))
    display_carpose_checkbox_button.clicked.connect(partial(update_plot, ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2')))

    
def handle_load_trip_path1(ui_elements, main_scope):
    prg_obj1 = load_trip_path(main_scope.get('prg_obj1'), ui_elements)
    main_scope['prg_obj1'] = prg_obj1


def handle_load_trip_path2(ui_elements, main_scope):
    prg_obj2 = load_trip_path(main_scope.get('prg_obj2'), ui_elements)
    main_scope['prg_obj2'] = prg_obj2


def handle_calculate_virtual_path(ui_elements, ui_display_elements, main_scope):
    result = calculate_virtual_path(ui_elements, ui_display_elements, main_scope.get('prg_obj1'), main_scope.get('prg_obj2'))
    main_scope['prg_obj1'], main_scope['prg_obj2'] = result
    