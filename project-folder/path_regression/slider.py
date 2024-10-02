# slider.py
from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class TimestampSlider(QWidget):
    def __init__(self, min_time, max_time):
        super().__init__()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_time)
        self.slider.setMaximum(max_time)
        self.label = QLabel(f"Timestamp: {min_time}")

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.update_label)

    def update_label(self, value):
        self.label.setText(f"Timestamp: {value}")
        self.sync_data(value)

    def sync_data(self, timestamp):
        """This method will sync all the data based on the current timestamp.
        It can trigger a callback in the main framework to adjust views in the plugins."""
        # This is where you'd call a method to sync all plugins based on the timestamp.
        pass
    