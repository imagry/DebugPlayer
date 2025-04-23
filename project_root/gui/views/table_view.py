#!/usr/bin/env python3

"""
TableView component for the Debug Player.

This module provides a table-based visualization for structured data,
allowing users to view datasets in a tabular format with sorting and filtering.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QPushButton, QLineEdit, QLabel, QComboBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor, QBrush

from core.view_manager import ViewBase


class TableViewModel(QAbstractTableModel):
    """
    Table model for displaying structured data in a QTableView.
    
    This model handles conversion of different data formats (dictionaries, arrays, etc.)
    into a format suitable for table display.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers: List[str] = []
        self.data_rows: List[List[Any]] = []
        self.column_types: List[type] = []
        self.signal_metadata: Dict[str, Dict[str, Any]] = {}
        
    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of rows in the model.
        """
        return len(self.data_rows)
        
    def columnCount(self, parent=QModelIndex()):
        """
        Return the number of columns in the model.
        """
        return len(self.headers)
        
    def data(self, index, role=Qt.DisplayRole):
        """
        Return the data for the specified index and role.
        """
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            value = self.data_rows[index.row()][index.column()]
            
            # Format the value based on its type
            if isinstance(value, float):
                # Get column precision from signal metadata if available
                col_name = self.headers[index.column()]
                signal_name = next(iter(self.signal_metadata.keys()), None)
                
                if signal_name and 'precision' in self.signal_metadata.get(signal_name, {}):
                    precision = self.signal_metadata[signal_name]['precision']
                    return f"{value:.{precision}f}"
                else:
                    return f"{value:.2f}"
            else:
                return str(value)
                
        elif role == Qt.BackgroundRole:
            # Color critical values
            value = self.data_rows[index.row()][index.column()]
            if isinstance(value, (int, float)):
                col_name = self.headers[index.column()]
                signal_name = next(iter(self.signal_metadata.keys()), None)
                
                if signal_name and 'critical_values' in self.signal_metadata.get(signal_name, {}):
                    critical_values = self.signal_metadata[signal_name]['critical_values']
                    for critical_name, critical_value in critical_values.items():
                        if abs(value - critical_value) < 0.001:  # Close enough
                            return QBrush(QColor(255, 200, 200))  # Light red for critical values
        
        return None
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the header data for the view.
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        
        return None
        
    def set_data(self, data: Any, signal_name: str, signal_metadata: Dict[str, Any] = None):
        """
        Set the data for the table view.
        
        Args:
            data: Data in various formats (dict, list, numpy array)
            signal_name: Name of the signal providing this data
            signal_metadata: Metadata for the signal
        """
        self.beginResetModel()
        
        self.data_rows = []
        self.headers = []
        self.column_types = []
        
        if signal_metadata:
            self.signal_metadata[signal_name] = signal_metadata
        
        # Handle different data formats
        if isinstance(data, dict):
            self._process_dict_data(data)
        elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], dict):
            self._process_list_of_dicts(data)
        elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)):
            self._process_list_of_lists(data)
        elif isinstance(data, np.ndarray):
            self._process_numpy_array(data)
        else:
            # Default fallback
            self.headers = ["Value"]
            self.data_rows = [[data]]
            self.column_types = [type(data)]
            
        self.endResetModel()
        
    def _process_dict_data(self, data: Dict[str, Any]):
        """
        Process dictionary data for table display.
        """
        self.headers = list(data.keys())
        self.data_rows = [list(data.values())]
        self.column_types = [type(val) for val in data.values()]
        
    def _process_list_of_dicts(self, data: List[Dict[str, Any]]):
        """
        Process a list of dictionaries for table display.
        """
        if not data:
            return
            
        # Get all possible keys as column headers
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
            
        self.headers = list(all_keys)
        
        # Convert data to rows
        for item in data:
            row = [item.get(key, "") for key in self.headers]
            self.data_rows.append(row)
            
        # Get column types
        if self.data_rows:
            self.column_types = []
            for col_idx in range(len(self.headers)):
                # Find the first non-empty value to determine type
                for row in self.data_rows:
                    if col_idx < len(row) and row[col_idx] != "":
                        self.column_types.append(type(row[col_idx]))
                        break
                else:
                    self.column_types.append(str)  # Default to string if no value found
        
    def _process_list_of_lists(self, data: List[List[Any]]):
        """
        Process a list of lists for table display.
        """
        if not data:
            return
            
        # Create numeric headers
        max_columns = max(len(row) for row in data)
        self.headers = [f"Column {i+1}" for i in range(max_columns)]
        
        # Set data rows directly
        self.data_rows = []
        for row in data:
            # Pad rows if needed
            padded_row = row + [""] * (max_columns - len(row))
            self.data_rows.append(padded_row)
            
        # Get column types
        if self.data_rows:
            self.column_types = []
            for col_idx in range(max_columns):
                # Find the first non-empty value to determine type
                for row in self.data_rows:
                    if col_idx < len(row) and row[col_idx] != "":
                        self.column_types.append(type(row[col_idx]))
                        break
                else:
                    self.column_types.append(str)  # Default to string if no value found
        
    def _process_numpy_array(self, data: np.ndarray):
        """
        Process numpy array for table display.
        """
        if data.ndim == 1:
            # 1D array: convert to single column
            self.headers = ["Value"]
            self.data_rows = [[x] for x in data]
            if len(data) > 0:
                self.column_types = [type(data[0])]
            else:
                self.column_types = [float]
        elif data.ndim == 2:
            # 2D array: rows and columns
            self.headers = [f"Column {i+1}" for i in range(data.shape[1])]
            self.data_rows = [list(row) for row in data]
            if data.size > 0:
                self.column_types = [type(data[0, 0])] * data.shape[1]
            else:
                self.column_types = [float] * data.shape[1]
        else:
            # Higher dimensions not supported directly
            self.headers = ["Value"]
            self.data_rows = [[str(data)]]
            self.column_types = [str]


class TableView(ViewBase):
    """
    Table view component for displaying structured data.
    
    This view provides a tabular display for structured data sources,
    with support for sorting, filtering, and customizable formatting.
    """
    # Signal emitted when a cell is clicked (row, column, value)
    cell_clicked = Signal(int, int, object)
    
    def __init__(self, view_id: str, parent=None):
        super().__init__(view_id, parent)
        
        # Set supported signal types
        self.supported_signal_types = {'temporal', 'spatial', 'categorical', 'text'}
        
        # Initialize data structures
        self.signal_data: Dict[str, Any] = {}
        self.signal_metadata: Dict[str, Dict[str, Any]] = {}
        self.active_signal: Optional[str] = None
        
        # Create the widget
        self._setup_ui()
        
    def _setup_ui(self):
        """
        Set up the user interface for the table view.
        """
        # Main widget and layout
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.widget.setLayout(layout)
        
        # Add controls section at the top
        controls_layout = QHBoxLayout()
        
        # Signal selector
        controls_layout.addWidget(QLabel("Signal:"))
        self.signal_combo = QComboBox()
        self.signal_combo.currentTextChanged.connect(self._on_signal_changed)
        controls_layout.addWidget(self.signal_combo)
        
        # Search box
        controls_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter table...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        controls_layout.addWidget(self.search_input)
        
        # Add controls to main layout
        layout.addLayout(controls_layout)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Create table view
        self.table_view = QTableView()
        self.table_model = TableViewModel()
        
        # Create proxy model for sorting/filtering
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # Set up table view
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(True)
        
        # Connect signals
        self.table_view.clicked.connect(self._on_cell_clicked)
        
        # Add the table to the layout
        layout.addWidget(self.table_view)
        
        # Add status bar at the bottom
        self.status_label = QLabel("No data")
        layout.addWidget(self.status_label)
        
    def _on_signal_changed(self, signal_name: str):
        """
        Handle signal selection change.
        
        Args:
            signal_name: The newly selected signal name
        """
        if not signal_name or signal_name not in self.signal_data:
            return
            
        self.active_signal = signal_name
        
        # Update the table with the selected signal's data
        data = self.signal_data[signal_name]
        metadata = self.signal_metadata.get(signal_name, {})
        self.table_model.set_data(data, signal_name, metadata)
        
        # Update status
        self._update_status()
        
    def _on_search_text_changed(self, text: str):
        """
        Handle changes to the search filter.
        
        Args:
            text: New search text
        """
        self.proxy_model.setFilterFixedString(text)
        self._update_status()
        
    def _on_cell_clicked(self, index: QModelIndex):
        """
        Handle cell click in the table.
        
        Args:
            index: The clicked model index
        """
        # Get the actual source index from the proxy model
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        col = source_index.column()
        
        if row >= 0 and col >= 0 and row < len(self.table_model.data_rows):
            value = self.table_model.data_rows[row][col]
            self.cell_clicked.emit(row, col, value)
        
    def _update_status(self):
        """
        Update the status bar with current information.
        """
        total_rows = self.table_model.rowCount()
        visible_rows = self.proxy_model.rowCount()
        
        if self.active_signal:
            if total_rows == visible_rows:
                self.status_label.setText(f"{self.active_signal}: {total_rows} rows")
            else:
                self.status_label.setText(f"{self.active_signal}: {visible_rows} of {total_rows} rows")
        else:
            self.status_label.setText("No data")
    
    def update_data(self, signal_name: str, data: Any) -> bool:
        """
        Update the view with new data for a signal.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Store the data
            self.signal_data[signal_name] = data
            
            # Update the signal selector if needed
            if signal_name not in [self.signal_combo.itemText(i) for i in range(self.signal_combo.count())]:
                self.signal_combo.addItem(signal_name)
            
            # If this is the first signal or the active signal, update the display
            if self.active_signal is None or signal_name == self.active_signal:
                self.active_signal = signal_name
                self.signal_combo.setCurrentText(signal_name)
                self.table_model.set_data(data, signal_name, self.signal_metadata.get(signal_name))
                self._update_status()
            
            return True
        except Exception as e:
            print(f"Error updating table view with signal {signal_name}: {str(e)}")
            return False
    
    def get_widget(self) -> QWidget:
        """
        Get the Qt widget for this view.
        
        Returns:
            The QWidget that displays this view
        """
        return self.widget
    
    def set_signal_metadata(self, signal_name: str, metadata: Dict[str, Any]):
        """
        Set metadata for a signal.
        
        Args:
            signal_name: Name of the signal
            metadata: Metadata dictionary
        """
        self.signal_metadata[signal_name] = metadata
        
        # If this is the active signal, update the display
        if signal_name == self.active_signal and signal_name in self.signal_data:
            self.table_model.set_data(
                self.signal_data[signal_name], 
                signal_name, 
                metadata
            )
            
    def clear(self):
        """
        Clear all data from the view.
        """
        self.signal_data.clear()
        self.active_signal = None
        self.signal_combo.clear()
        self.table_model.set_data([], "", {})
        self.status_label.setText("No data")
