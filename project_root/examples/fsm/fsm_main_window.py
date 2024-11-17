from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel,
                               QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QMainWindow, QLineEdit, QSplitter)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer, QSettings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from examples.fsm.fsm_core import FSM
from examples.fsm.fsm_plot_manager import GraphView, PlotWidget
from examples.fsm.video_player_widget import VideoPlayerWidget
import os
import time
from datetime import datetime
import pytz  # Import pytz for timezone conversion
import sys

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, fsm_file_path=None, trip_video_path = None, parent=None):
        super().__init__(parent)
        self.fsm = FSM(fsm_file_path)
        self.current_index = 0
        self.video_path = trip_video_path
        
                    
        # Initialize the video timer plot widget with the video start time in Unix time
        self.video_start_time = self.parse_video_start_time(self.video_path)                   
        
        # Initialize components
        self.initialize_components()
        
        # Set up the main layout
        self.setup_main_layout()
        
        # Connect signals
        self.setup_connections()
        
        # Initialize FSM-specific data and state
        self.initialize_fsm_data()
        
    def calculate_time_offset(self):
        """Calculate the offset between the FSM and video timestamps."""
        # Get the first FSM timestamp
        fsm_start_time = self.fsm.dataframe["time_stamp"].iloc[0]
        
        # Get the video start time from the filename
        video_start_time =  self.video_start_time
        
        # Calculate and return the offset
        if video_start_time is not None:
            # time_offset = fsm_start_time - video_start_time
            time_offset = 0 # Set to 0 for now - ideally, user will match the offset by looking at the video timer time to the actual time in the window. 
            return time_offset
        else:
            return 0  # Default to 0 if there was an error parsing the video time

    def initialize_components(self):
            """Initialize all components used in the main window."""
           
            k = min(len(self.fsm.signals_dict), len(self.fsm.signals_data_dict))
            
            # Create components
            self.table_widget = self.create_table_widget(k + 2)
            self.view = GraphView(self.fsm)
            self.plot_widget = PlotWidget(self.fsm)
            self.time_plot_widget = TimePlotWidget()  # Add time plot widget
            # self.time_display_widget = TimeDisplayWidget()  # Add time display widget
            self.time_display_widget = TimeDisplayWidget(font_size=14, font_color="cyan")  # Set size and color
           

            # Set font for the table widget
            font = QFont()
            font.setPointSize(12)
            self.table_widget.setFont(font)
            
            # Create the FSM state slider
            self.slider = self.create_slider()
            
            # Create combo boxes
            self.layout_combo = self.create_layout_combo()
            self.k_combo = self.create_k_combo()
            
            # Create button to open video player
            self.video_button = QPushButton("Open Video Player")
            self.video_button.clicked.connect(self.open_video_player)
            
            # Initialize the video player (it will be shown only when needed)
            self.video_player = None
        
    def create_table_widget(self, k = 10):
        """Creates a table widget for displaying tabular data."""
        table = QTableWidget()
        table.setRowCount(k)  # Set to the number of rows you need
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Data Name", "Data Value", "Signal Name", "Signal Value"])
        table.verticalHeader().setVisible(False)
        table.setColumnWidth(0, 400)
        table.setColumnWidth(2, 150)
        return table
    
    def parse_video_start_time(self, video_path):
        """Extract and convert the video start time from the filename."""
        # Assume the timestamp is in the format "YYYY-MM-DDTHH_MM_SS" at the end of the filename
        try:
            # Extract timestamp part of the filename (e.g., "2024-11-13T14_16_15")
            timestamp_str = video_path.split("__")[-1].replace(".mp4", "")
            
            # Parse timestamp to a datetime object
            video_start_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H_%M_%S")
            
            # Define Tokyo timezone
            tokyo_tz = pytz.timezone("Asia/Tokyo")
        
            # Localize the naive datetime to Tokyo time
            video_start_dt_tokyo = tokyo_tz.localize(video_start_dt)
                
            # Convert datetime to Unix time
            video_start_unix = int(video_start_dt_tokyo.timestamp())
        
            return video_start_unix
        
        except ValueError:
            print("Error: Video filename format is incorrect or timestamp is missing.")
            return None    
            
    def create_slider(self):
        """Create and return a slider for FSM state control."""
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(len(self.fsm.dataframe) - 1)
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBelow)
        return slider
    
    def create_layout_combo(self):
        """Create and return the combo box for layout selection."""
        layout_combo = QComboBox()
        layout_combo.addItems(self.view.get_layout_names())
        return layout_combo

    def create_k_combo(self):
        """Create and return the combo box for selecting number of edges to highlight."""
        k_combo = QComboBox()
        k_combo.addItems([str(i) for i in range(1, 11)])  # k from 1 to 10
        k_combo.setCurrentIndex(2)  # Default k is 3
        return k_combo
      
    def setup_main_layout(self):
        """Set up the main layout with all components and sub-layouts."""
              # Set up the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
                    
        # Create a splitter
        top_splitter_H = QSplitter(Qt.Horizontal)
                        
        # Top row layout with table and FSM view        
        top_splitter_H.addWidget(self.table_widget)
        top_splitter_H.addWidget(self.view)
        
        # main_layout.addWidget(top_splitter_H)

        # top_layout.addWidget(self.time_plot_widget, 1)  # Add time plot widget here
        # top_layout.addWidget(self.time_display_widget, 1)  # Add time display widget here

        middle_splitter_V = QSplitter(Qt.Vertical)
        middle_splitter_V.addWidget(top_splitter_H)
        middle_splitter_V.addWidget(self.plot_widget)
        
        main_layout.addWidget(middle_splitter_V)
        # Bottom layout with plot widget, slider, and combo boxes
        bottom_layout = QVBoxLayout()
               
        # Slider layout
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("FSM State Slider:"))
        slider_layout.addWidget(self.slider)
        bottom_layout.addLayout(slider_layout)
        
        # Timer layout (place it directly below the slider)
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(self.time_display_widget)  # Add time display widget here
        
        # Add timer and offset layouts to the bottom layout
        bottom_layout.addLayout(timer_layout)
                
        # Layout combo box layout
        layout_combo_layout = QHBoxLayout()
        layout_combo_layout.addWidget(QLabel("Select Layout:"))
        layout_combo_layout.addWidget(self.layout_combo)
        bottom_layout.addLayout(layout_combo_layout)
        
        # k combo box layout
        k_combo_layout = QHBoxLayout()
        k_combo_layout.addWidget(QLabel("Highlight last k edges:"))
        k_combo_layout.addWidget(self.k_combo)
        bottom_layout.addLayout(k_combo_layout)
        
        # Add video button to bottom layout
        bottom_layout.addWidget(self.video_button)
        
        # Add top and bottom layouts to the main layout
        main_layout.addLayout(bottom_layout) 
    
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def setup_connections(self):
        """Connect signals to their respective slots."""
    
        # Connect the FSM slider to update the FSM state
        self.slider.valueChanged.connect(self.update_fsm_state)
        
        # Connect the layout and k combo boxes to their respective slots
        self.layout_combo.currentTextChanged.connect(self.view.apply_layout)
        self.k_combo.currentTextChanged.connect(lambda k: self.view.set_k(int(k)))  
            
    def initialize_fsm_data(self):
        """Initialize FSM-specific data and set the initial state."""
        self.state_sequence = []
        self.traversed_edges = []
        self.update_fsm_state(0)      
    
    def open_video_player(self):
        """Open the video player window."""
        try:
            if not self.video_player:
                self.video_player = VideoPlayerWidget(self.video_start_time)
                self.video_player.setWindowTitle("Video Player")
                self.video_player.resize(800, 600)
                if os.path.exists(self.video_path):
                    trip_video_path = self.video_path 
                else:
                    print("Video file not found.")
                    return            
                self.video_player.load_video(trip_video_path)
                
                # Connect positionChanged signal to update FSM timer when video position changes
                self.video_player.media_player.positionChanged.connect(self.video_slider_moved)            
                # Synchronize video slider with main window slider
                self.video_player.slider.valueChanged.connect(self.video_slider_moved)
                self.slider.valueChanged.connect(self.main_slider_moved)
                
                # Connect the destroyed signal to a slot to clean up the reference
                self.video_player.destroyed.connect(self.on_video_player_closed)
            
            
            self.video_player.show()
            self.video_player.raise_()
        except Exception as e:
            print(f"Error in open_video_player: {e}")
            
    def video_slider_moved(self, video_position_ms):
        """Update main window slider and FSM state when video slider moves."""
    
        # Calculate the current video time in seconds
        current_video_position_s = video_position_ms / 1000  # Convert from ms to s

        # Use the offset from the video player
        if self.video_player:
            time_offset = self.video_player.time_offset
        else:
            time_offset = 0.0  # Default to zero if video_player is not initialized
        
        
        # Calculate the absolute video time (Unix timestamp)
        absolute_video_time = self.video_start_time + current_video_position_s + time_offset
        
        # Update FSM time display
        self.time_display_widget.update_time(absolute_video_time)
    
        # Find the closest FSM index corresponding to the absolute video time
        fsm_index = self.find_fsm_index_for_time(absolute_video_time)
           
        # Update the FSM slider without triggering signals
        self.slider.blockSignals(True)
        self.slider.setValue(fsm_index)
        self.slider.blockSignals(False)
        
        # Update FSM state and display
        self.update_fsm_state(fsm_index)

    def main_slider_moved(self, fsm_index):
        """Update video slider when main window FSM slider moves."""
        if self.video_player:  # Check if video player is initialized
            # Get the corresponding FSM time for the slider's index position
            fsm_time = self.fsm.dataframe["time_stamp"].iloc[fsm_index]
            
            # Use the offset from the video player
            time_offset = self.video_player.time_offset
        
            # Calculate the video time by subtracting the video start time and time offset
            video_time_s = fsm_time - self.video_start_time - time_offset
        
            # Convert video time to milliseconds
            video_position_ms = video_time_s * 1000

            # Ensure the calculated position is within the video duration
            video_duration_ms = self.video_player.media_player.duration()
            if 0 <= video_position_ms <= video_duration_ms:
                # Update the video player's slider and media player position without emitting signals
                self.video_player.slider.blockSignals(True)
                self.video_player.slider.setValue(video_position_ms)
                self.video_player.slider.blockSignals(False)

                self.video_player.media_player.blockSignals(True)
                self.video_player.media_player.setPosition(video_position_ms)
                self.video_player.media_player.blockSignals(False)
            
    def update_table_data(self, data):
        """Update the table with new data."""
        self.table_widget.setRowCount(len(data))
        for row, (name, value) in enumerate(data.items()):
            self.table_widget.setItem(row, 0, QTableWidgetItem(name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(value)))

    def update_table_signals(self, signals):
        """Update the table with new signals."""
        self.table_widget.setRowCount(len(signals))
        for row, (name, value) in enumerate(signals.items()):
            self.table_widget.setItem(row, 2, QTableWidgetItem(name))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(value)))

    def update_timestamp_marker(self, index):
        """Pass the timestamp of the current index to the PlotWidget to update the vertical bar."""
        timestamp = self.fsm.dataframe["time_stamp"].iloc[index]  # Assuming "time_stamp" column exists
        self.plot_widget.update_vertical_bar(timestamp)

    def update_fsm_state(self, index):
        """Update the FSM state based on the slider value with support for configurable signals."""
        
        if index == 0:
            self.state_sequence = []
            self.traversed_edges = []
            current_state = self.fsm.dataframe["Current State"].iloc[index]
            self.view.highlight_node(current_state)
            return  

        self.state_sequence = self.fsm.dataframe["Current State"].iloc[:index + 1].tolist()
        self.traversed_edges = list(zip(self.state_sequence[:-1], self.state_sequence[1:]))

        row = self.fsm.dataframe.iloc[index]
        current_state = row["Current State"]
           
        # Get the current FSM time from the dataframe using the slider index
        current_fsm_time = self.fsm.dataframe["time_stamp"].iloc[index]
        # Use the offset from the video player
        if self.video_player:
            time_offset = self.video_player.time_offset
        else:
            time_offset = 0.0
        # adjusted_fsm_time = current_fsm_time + time_offset
        # Update FSM time display widget with the adjusted time

        # Update FSM time display widget with the current FSM time
        self.time_display_widget.update_time(current_fsm_time)      
        
        self.view.highlight_node(current_state)

        # Highlight traversed edges
        d = len(self.traversed_edges)
        num_edges_to_highlight = min(self.view.k, d)
        self.traversed_edges = [edge for edge in self.traversed_edges if edge[0] != edge[1]]
        edges_to_highlight = self.traversed_edges[-num_edges_to_highlight:]
        self.view.highlight_last_k_edges(edges_to_highlight)

        # Update the timestamp marker in the PlotWidget
        self.update_timestamp_marker(index)
        signal_data_values = self.fsm.get_signals_data_at_index(index)
        self.update_table_data(signal_data_values)
        
        signals_values = self.fsm.get_signals_value_at_index(index)
        self.update_table_signals(signals_values)
    
    def find_fsm_index_for_time(self, fsm_time):
        """Find the closest FSM index for a given absolute time."""
        # Calculate the absolute difference between each timestamp and the target time
        time_diffs = (self.fsm.dataframe["time_stamp"] - fsm_time).abs()
        
        # Find the index of the minimum difference
        closest_index = time_diffs.idxmin()
        
        return int(closest_index)

    def on_video_player_closed(self):
        """Handle the video player window being closed."""
        print("Video player window closed.")
        self.video_player = None  # Remove the reference to allow garbage collection

    def closeEvent(self, event):
        """Handle the event when the main window is closed."""
        # Stop any remaining processes or threads if necessary
        # For example, stop the video player if it's still open
        if self.video_player:
            self.video_player.close()

        # Call the base class implementation (optional but recommended)
        super().closeEvent(event)

        # Exit the application
        sys.exit()

class TimePlotWidget(QWidget):
    """Widget to display current time in Unix time and OS time formats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize figure and canvas for plotting
        self.figure = Figure(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        
        # Set up a layout and add the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Initialize axes for time plots
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Current Time Plot")
        self.ax.set_xlabel("Time")
        
        # Initialize empty lines for Unix time and OS time
        self.unix_line, = self.ax.plot([], [], label="Unix Time (Linux)")
        self.os_line, = self.ax.plot([], [], label="OS Time (Local)")
        self.ax.legend()

        # Store timestamps and initialize data lists
        self.timestamps = []
        self.unix_times = []
        self.os_times = []

    def update_time(self, current_time_unix):
        """Update the time plot with a new timestamp."""
        # Convert Unix time to local time
        current_time_local = datetime.fromtimestamp(current_time_unix)
        
        # Update data lists
        self.timestamps.append(len(self.timestamps))  # Use index as the x-axis
        self.unix_times.append(current_time_unix)
        self.os_times.append(current_time_local.timestamp())
        
        # Update plot data
        self.unix_line.set_data(self.timestamps, self.unix_times)
        self.os_line.set_data(self.timestamps, self.os_times)
        
        # Adjust plot limits
        self.ax.relim()
        self.ax.autoscale_view()

        # Refresh canvas
        self.canvas.draw_idle()
            
    
class TimeDisplayWidget(QWidget):
    """Widget to display the current FSM time in Unix and local time formats based on the slider position."""

    def __init__(self, font_size=12, font_color="white", parent=None):
        super().__init__(parent)
        
        # Set up labels to show Unix time and local time
        self.unix_time_label = QLabel("Unix Time: ")
        self.tokyo_time_label = QLabel("Tokyo Time: ")
        
        # Apply font size and color
        self.set_font_size(font_size)
        self.set_font_color(font_color)
        
        # Arrange labels in a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.unix_time_label)
        layout.addWidget(self.tokyo_time_label)
        self.setLayout(layout)
    
    def set_font_size(self, size):
        """Set the font size for the labels."""
        font = QFont()
        font.setPointSize(size)
        self.unix_time_label.setFont(font)
        self.tokyo_time_label.setFont(font)
    
    def set_font_color(self, color):
        """Set the font color for the labels."""
        self.unix_time_label.setStyleSheet(f"color: {color};")
        self.tokyo_time_label.setStyleSheet(f"color: {color};")
    
    
    def update_time(self, fsm_unix_time):
        """Update the displayed time based on the FSM's current time in Unix and Tokyo time."""
        # Convert Unix time to Tokyo time
        tokyo_tz = pytz.timezone("Asia/Tokyo")
        current_tokyo_time = datetime.fromtimestamp(fsm_unix_time, tokyo_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # Update labels
        self.unix_time_label.setText(f"Unix Time: {fsm_unix_time:.4f}")
        self.tokyo_time_label.setText(f"Tokyo Time: {current_tokyo_time}")