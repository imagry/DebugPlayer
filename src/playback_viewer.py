# playback_viewer.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSlider, QLabel, QCheckBox, QGridLayout, QMenuBar, QAction)
from PyQt5.QtCore import Qt
from plot_widget import PlotWidget

class PlaybackViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Playback Viewer')
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Menu bar setup
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        file_menu = self.menu_bar.addMenu('File')
        view_menu = self.menu_bar.addMenu('View')
        help_menu = self.menu_bar.addMenu('Help')

        # Add actions to file menu (save/reset)
        save_action = QAction('Save Current State', self)
        reset_action = QAction('Reset Trip', self)
        file_menu.addAction(save_action)
        file_menu.addAction(reset_action)

        # Create top section (Main Window and Secondary Window)
        self.main_window = PlotWidget("Main Window")
        self.secondary_window = PlotWidget("Secondary Window")

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.main_window)
        top_layout.addWidget(self.secondary_window)
        layout.addLayout(top_layout)

        # Create Temporal Window and signal selection
        self.temporal_window = PlotWidget("Temporal Window")

        self.signal_selection_layout = QVBoxLayout()
        self.signal_selection_layout.addWidget(QLabel("Temporal Window ->"))

        # Create checkboxes for signals
        self.signals = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4']
        self.signal_checkboxes = []
        for signal in self.signals:
            checkbox = QCheckBox(signal)
            checkbox.stateChanged.connect(self.update_signals)
            self.signal_selection_layout.addWidget(checkbox)
            self.signal_checkboxes.append(checkbox)

        # Place temporal window and signal selection in a horizontal layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(self.signal_selection_layout)
        bottom_layout.addWidget(self.temporal_window)
        layout.addLayout(bottom_layout)
        
        # Create slider and playback controls
        control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play/Pause")
        self.play_button.clicked.connect(self.toggle_playback)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self.update_slider_position)

        self.playback_speed_label = QLabel("Speed: 1.00x")
        self.playback_speed_label.mousePressEvent = self.change_speed
        
        self.time_label = QLabel("00:00/00:41")
        
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.playback_speed_label)
        control_layout.addWidget(self.time_label)
        
        layout.addLayout(control_layout)
    
    def toggle_playback(self):
        # Placeholder for play/pause functionality
        print("Toggled play/pause")
    
    def update_slider_position(self, position):
        # Placeholder for slider control functionality
        print(f"Slider moved to: {position}")
    
    def change_speed(self, event):
        # Placeholder for playback speed change functionality
        print("Playback speed changed")

    def update_signals(self):
        # Update signals based on checkbox selections
        selected_signals = [cb.text() for cb in self.signal_checkboxes if cb.isChecked()]
        print(f"Selected signals: {selected_signals}")
