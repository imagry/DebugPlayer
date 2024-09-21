# signal_manager.py

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QCheckBox

class SignalManager:
    def __init__(self, update_temporal_plot_callback):
        self.update_temporal_plot_callback = update_temporal_plot_callback
        self.signal_checkboxes = []
        self.signals = []

        # Create the signal selection layout
        self.signal_selection_layout = QVBoxLayout()
        self.signal_selection_widget = QWidget()
        self.signal_selection_widget.setLayout(self.signal_selection_layout)

    def get_signal_selection_widget(self):
        """
        Returns the widget containing the signal selection checkboxes.
        """
        return self.signal_selection_widget

    def update_signal_checkboxes(self, signals):
        """
        Updates the signal checkboxes based on the available signals.
        """
        # Clear existing checkboxes
        for checkbox in self.signal_checkboxes:
            self.signal_selection_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        
        self.signal_checkboxes = []
        self.signals = signals

        # Create a new checkbox for each signal
        for signal in self.signals:
            checkbox = QCheckBox(signal)
            checkbox.stateChanged.connect(self.update_signals)
            self.signal_selection_layout.addWidget(checkbox)
            self.signal_checkboxes.append(checkbox)

    def update_signals(self):
        """
        Updates the temporal plot based on selected signals.
        """
        selected_signals = [cb.text() for cb in self.signal_checkboxes if cb.isChecked()]
        self.update_temporal_plot_callback(selected_signals)

    
    