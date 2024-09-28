# ui_components.py
from PySide6 import QtWidgets
import pyqtgraph as pg
from data_handlers import load_trip_path
from plot_functions import update_plot, save_figure, calculate_virtual_path

def create_main_window():
    """Create and set up the main window and UI components."""
    main_win = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout()
    main_win.setLayout(main_layout)
    main_win.setWindowTitle('Path Regression Analysis')
    main_win.resize(1200, 600)  # Increased size to accommodate additional controls

    # Create a horizontal layout for controls and plot
    h_layout = QtWidgets.QHBoxLayout()
    main_layout.addLayout(h_layout)

    # Create a vertical layout for controls
    controls_layout = QtWidgets.QVBoxLayout()
    h_layout.addLayout(controls_layout)

    # Add UI elements for the first trip
    controls_layout.addWidget(QtWidgets.QLabel('Trip 1 Settings'))
    load_button1 = QtWidgets.QPushButton('Load Trip 1 Path')
    controls_layout.addWidget(load_button1)

    # Add UI elements for the second trip
    controls_layout.addWidget(QtWidgets.QLabel('Trip 2 Settings'))
    load_button2 = QtWidgets.QPushButton('Load Trip 2 Path')
    controls_layout.addWidget(load_button2)
    
   # Add buttons to perform operations on both paths
    compare_button = QtWidgets.QPushButton('Compare Paths')
    controls_layout.addWidget(compare_button)
    
    
    # Add control widgets
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

    # Controls for virtual path extraction
    virtual_path_label = QtWidgets.QLabel('Virtual Path Extraction')
    virtual_path_label.setStyleSheet("font-weight: bold;")
    controls_layout.addWidget(virtual_path_label)

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

    # Add buttons
    run_button = QtWidgets.QPushButton('Run')
    controls_layout.addWidget(run_button)

    # load_button = QtWidgets.QPushButton('Load Trip Path')
    # controls_layout.addWidget(load_button)

    update_plot_button = QtWidgets.QPushButton('Update Plot')
    controls_layout.addWidget(update_plot_button)

    save_button = QtWidgets.QPushButton('Save Figure')
    controls_layout.addWidget(save_button)

    # Add spacer to push widgets to the top
    controls_layout.addStretch()

    # Create the pyqtgraph plot widget
    plt = pg.PlotWidget(title="2D Trajectory Plot")
    h_layout.addWidget(plt)

    # Set stretch factors to make the plot larger
    h_layout.setStretchFactor(controls_layout, 1)
    h_layout.setStretchFactor(plt, 4)

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)

    ui_elements = {
        'line_width_spin': line_width_spin,
        'marker_size_spin': marker_size_spin,
        'colors_num_spin': colors_num_spin,
        'colors_palette_list': colors_palette_list,
        'delta_t_input': delta_t_input,
        'pts_before_spin': pts_before_spin,
        'pts_after_spin': pts_after_spin,
        'plt': plt,
        'load_button1': load_button1,
        'load_button2': load_button2,
        'compare_button': compare_button
    }

    return main_win, run_button, load_button1, load_button2, update_plot_button, save_button, ui_elements
                    
def connect_signals(run_button, load_button1, load_button2, update_plot_button, save_button, prg_obj1, prg_obj2, ui_elements):
    
    """Connect UI signals to their respective slots."""
    run_button.clicked.connect(lambda: calculate_virtual_path(ui_elements, prg_obj1, prg_obj2))
    load_button1.clicked.connect(lambda: load_trip_path(prg_obj1, ui_elements))
    load_button2.clicked.connect(lambda: load_trip_path(prg_obj2, ui_elements))
    update_plot_button.clicked.connect(lambda: update_plot(ui_elements, prg_obj1, prg_obj2))
    save_button.clicked.connect(lambda: save_figure(ui_elements))
