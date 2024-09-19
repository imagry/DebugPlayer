from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QHBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from pyqtgraph.dockarea import DockArea, Dock
from playback_controls import PlaybackControls
from plot_manager import PlotManager
from data_handler import DataHandler
from signal_manager import SignalManager

class PlaybackViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Playback Viewer with PyQtGraph Docks')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Menu bar setup
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        file_menu = self.menu_bar.addMenu('File')

        # Add actions to file menu (save/load/reset)
        load_action = QAction('Load Trip Data', self)
        load_action.triggered.connect(self.load_data)
        save_action = QAction('Save Current State', self)
        save_action.triggered.connect(self.save_state)
        reset_action = QAction('Reset Trip', self)
        reset_action.triggered.connect(self.reset_trip)
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addAction(reset_action)

        # Create DockArea
        self.dock_area = DockArea()
        layout.addWidget(self.dock_area)

        # Instantiate Managers
        self.data_handler = DataHandler()
        self.plot_manager = PlotManager(self.dock_area)
        self.signal_manager = SignalManager(self.plot_manager.update_temporal_plot)

        # Create Docks
        self.main_dock = Dock("Main Window", size=(500, 300))
        self.secondary_dock = Dock("Secondary Window", size=(500, 300))
        self.temporal_dock = Dock("Temporal Window", size=(1000, 200))

        # Add Docks to DockArea
        self.dock_area.addDock(self.main_dock, 'left')
        self.dock_area.addDock(self.secondary_dock, 'right', self.main_dock)
        self.dock_area.addDock(self.temporal_dock, 'bottom')

        # Add plots to docks
        self.plot_manager.initialize_plots(self.main_dock, self.secondary_dock, self.temporal_dock)

        # Signal selection layout
        self.signal_selection_widget = self.signal_manager.get_signal_selection_widget()
        self.temporal_dock.addWidget(self.signal_selection_widget, row=1, col=0)

        # Create playback controls
        self.playback_controls = PlaybackControls(self.plot_manager.update_plots, self.data_handler.get_time_data)
        control_layout = self.playback_controls.get_control_layout()

        layout.addLayout(control_layout)

    def load_data(self):
        """
        Loads trip data from a file and updates the viewer.
        """
        success = self.data_handler.load_data()
        if success:
            self.signal_manager.update_signal_checkboxes(self.data_handler.get_signals())
            self.plot_manager.update_data(self.data_handler.get_main_data(), self.data_handler.get_secondary_data())
            self.plot_manager.update_temporal_plot(self.data_handler.get_temporal_data())
    
    def save_state(self):
        """
        Placeholder for saving the current state.
        """
        print("Save state functionality not yet implemented.")

    def reset_trip(self):
        """
        Placeholder for resetting the trip to the initial state.
        """
        self.playback_controls.reset_playback()
        self.plot_manager.reset_plots()
