#!/usr/bin/env python3

"""
Signal Filter Panel for the Debug Player.

This module provides a UI panel for filtering and searching signals based on
their metadata, categories, and tags.
"""

from typing import List, Dict, Any, Optional, Set, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QCheckBox, QPushButton, QScrollArea, 
    QGroupBox, QFrame, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor

from core.signal_registry import SignalRegistry


class SignalFilterPanel(QWidget):
    """
    Panel for filtering and searching signals.
    
    This widget provides a UI for users to search and filter signals
    based on their metadata (categories, tags, types, etc.)
    and quickly locate signals of interest.
    """
    # Signal emitted when the selection of signals changes
    signal_selection_changed = Signal(list)  # List of selected signal names
    
    def __init__(self, signal_registry: SignalRegistry, parent=None):
        """
        Initialize the signal filter panel.
        
        Args:
            signal_registry: The signal registry containing signal metadata
            parent: Parent widget
        """
        super().__init__(parent)
        self.signal_registry = signal_registry
        
        # Track selected signals
        self.selected_signals: Set[str] = set()
        
        # Track filter state
        self.active_filters: Dict[str, Any] = {}
        self.search_text = ""
        
        # Setup UI
        self._setup_ui()
        
        # Initial population of signals
        self.refresh_signals()
    
    def _setup_ui(self):
        """
        Set up the user interface for the signal filter panel.
        """
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Signal Filters")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search signals...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Filter by type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types", None)
        self.type_combo.currentIndexChanged.connect(self.on_type_filter_changed)
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # Filter by category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories", None)
        self.category_combo.currentIndexChanged.connect(self.on_category_filter_changed)
        category_layout.addWidget(self.category_combo)
        
        layout.addLayout(category_layout)
        
        # Filter by tag section
        tag_group = QGroupBox("Tags")
        tag_layout = QVBoxLayout()
        tag_group.setLayout(tag_layout)
        
        self.tag_checkboxes: Dict[str, QCheckBox] = {}
        self.tag_container = QWidget()
        self.tag_container_layout = QVBoxLayout()
        self.tag_container.setLayout(self.tag_container_layout)
        
        # Make tags scrollable
        tag_scroll = QScrollArea()
        tag_scroll.setWidgetResizable(True)
        tag_scroll.setWidget(self.tag_container)
        tag_layout.addWidget(tag_scroll)
        
        layout.addWidget(tag_group)
        
        # Signal tree
        signal_group = QGroupBox("Available Signals")
        signal_layout = QVBoxLayout()
        signal_group.setLayout(signal_layout)
        
        self.signal_tree = QTreeWidget()
        self.signal_tree.setHeaderLabels(["Signal", "Type", "Description"])
        self.signal_tree.setColumnWidth(0, 150)  # Signal name
        self.signal_tree.setColumnWidth(1, 80)   # Signal type
        self.signal_tree.itemChanged.connect(self.on_signal_item_changed)
        signal_layout.addWidget(self.signal_tree)
        
        layout.addWidget(signal_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_signals)
        button_layout.addWidget(self.select_all_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_signals)
        button_layout.addWidget(self.clear_all_btn)
        
        self.clear_filters_btn = QPushButton("Clear Filters")
        self.clear_filters_btn.clicked.connect(self.clear_all_filters)
        button_layout.addWidget(self.clear_filters_btn)
        
        layout.addLayout(button_layout)
    
    def populate_filter_options(self):
        """
        Populate the filter dropdowns with available options from the signal registry.
        """
        # Temporarily block signals to prevent triggering filter updates
        self.type_combo.blockSignals(True)
        self.category_combo.blockSignals(True)
        
        # Remember selected values
        current_type = self.type_combo.currentData()
        current_category = self.category_combo.currentData()
        
        # Clear existing items
        while self.type_combo.count() > 1:  # Keep "All Types"
            self.type_combo.removeItem(1)
            
        while self.category_combo.count() > 1:  # Keep "All Categories"
            self.category_combo.removeItem(1)
        
        # Add available signal types
        for signal_type in sorted(self.signal_registry.signal_types.keys()):
            self.type_combo.addItem(signal_type.capitalize(), signal_type)
        
        # Add available categories
        for category in sorted(self.signal_registry.signal_categories.keys()):
            self.category_combo.addItem(category.replace('_', ' ').capitalize(), category)
        
        # Restore selected values if they still exist
        if current_type is not None:
            index = self.type_combo.findData(current_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
        if current_category is not None:
            index = self.category_combo.findData(current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        # Re-enable signals
        self.type_combo.blockSignals(False)
        self.category_combo.blockSignals(False)
        
        # Update tag checkboxes
        self._update_tag_checkboxes()
    
    def _update_tag_checkboxes(self):
        """
        Update the tag checkboxes based on available tags in the filtered signals.
        """
        # Clear existing tag checkboxes
        for checkbox in self.tag_checkboxes.values():
            self.tag_container_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.tag_checkboxes.clear()
        
        # Get tags from the filtered signals
        available_tags = set()
        filtered_signals = self._get_filtered_signals(include_tags=False)
        
        for signal_name in filtered_signals:
            metadata = self.signal_registry.get_signal_metadata(signal_name)
            tags = metadata.get("tags", [])
            available_tags.update(tags)
        
        # Create checkboxes for each tag
        for tag in sorted(available_tags):
            checkbox = QCheckBox(tag)
            checkbox.stateChanged.connect(lambda state, t=tag: self.on_tag_filter_changed(t, state))
            self.tag_checkboxes[tag] = checkbox
            self.tag_container_layout.addWidget(checkbox)
        
        # Add a stretch at the end
        self.tag_container_layout.addStretch()
    
    def refresh_signals(self):
        """
        Refresh the signal list based on current filters.
        """
        # Populate filter options
        self.populate_filter_options()
        
        # Get filtered signals
        filtered_signals = self._get_filtered_signals()
        
        # Update signal tree
        self.signal_tree.clear()
        
        # Group signals by plugin
        signals_by_plugin: Dict[str, List[str]] = {}
        
        for signal_name in filtered_signals:
            metadata = self.signal_registry.get_signal_metadata(signal_name)
            plugin_name = metadata.get("plugin", "Unknown")
            
            if plugin_name not in signals_by_plugin:
                signals_by_plugin[plugin_name] = []
                
            signals_by_plugin[plugin_name].append(signal_name)
        
        # Add signals to tree grouped by plugin
        for plugin_name in sorted(signals_by_plugin.keys()):
            plugin_item = QTreeWidgetItem(self.signal_tree)
            plugin_item.setText(0, plugin_name)
            plugin_item.setFlags(Qt.ItemIsEnabled)
            
            for signal_name in sorted(signals_by_plugin[plugin_name]):
                metadata = self.signal_registry.get_signal_metadata(signal_name)
                signal_type = metadata.get("type", "")
                description = metadata.get("description", "")
                
                signal_item = QTreeWidgetItem(plugin_item)
                signal_item.setText(0, signal_name)
                signal_item.setText(1, signal_type)
                signal_item.setText(2, description)
                signal_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
                signal_item.setData(0, Qt.UserRole, signal_name)  # Store signal name for reference
                
                # Set checked state based on current selection
                checked_state = Qt.Checked if signal_name in self.selected_signals else Qt.Unchecked
                signal_item.setCheckState(0, checked_state)
        
        # Expand all items
        self.signal_tree.expandAll()
    
    def _get_filtered_signals(self, include_tags=True) -> List[str]:
        """
        Get a list of signals that match the current filters.
        
        Args:
            include_tags: Whether to include tag filters
            
        Returns:
            List of signal names that match the filters
        """
        # Start with all signals
        all_signals = list(self.signal_registry.signals.keys())
        filtered_signals = all_signals
        
        # Apply type filter
        type_filter = self.type_combo.currentData()
        if type_filter is not None:
            filtered_signals = self.signal_registry.get_signals_by_type(type_filter)
        
        # Apply category filter
        category_filter = self.category_combo.currentData()
        if category_filter is not None:
            category_signals = self.signal_registry.filter_signals_by_category(category_filter)
            filtered_signals = [s for s in filtered_signals if s in category_signals]
        
        # Apply tag filters if requested
        if include_tags:
            active_tags = [tag for tag, checkbox in self.tag_checkboxes.items() 
                          if checkbox.isChecked()]
            
            if active_tags:
                # For each tag, get matching signals and take the intersection
                for tag in active_tags:
                    tag_signals = self.signal_registry.filter_signals_by_tag(tag)
                    filtered_signals = [s for s in filtered_signals if s in tag_signals]
        
        # Apply search text filter
        if self.search_text:
            search_matches = self.signal_registry.search_signals(self.search_text)
            filtered_signals = [s for s in filtered_signals if s in search_matches]
        
        return filtered_signals
    
    def on_search_text_changed(self, text):
        """
        Handle changes to the search text.
        
        Args:
            text: New search text
        """
        self.search_text = text.strip()
        self.refresh_signals()
    
    def on_type_filter_changed(self, index):
        """
        Handle changes to the type filter.
        
        Args:
            index: Selected index in the combo box
        """
        # Will trigger a refresh via refresh_signals()
        self._update_tag_checkboxes()
        self.refresh_signals()
    
    def on_category_filter_changed(self, index):
        """
        Handle changes to the category filter.
        
        Args:
            index: Selected index in the combo box
        """
        # Will trigger a refresh via refresh_signals()
        self._update_tag_checkboxes()
        self.refresh_signals()
    
    def on_tag_filter_changed(self, tag, state):
        """
        Handle changes to tag filters.
        
        Args:
            tag: The tag that changed
            state: New checkbox state
        """
        self.refresh_signals()
    
    def on_signal_item_changed(self, item, column):
        """
        Handle changes to signal selection in the tree.
        
        Args:
            item: Changed tree item
            column: Changed column
        """
        if column != 0 or not item.parent():
            return  # Only handle checkbox changes in the first column for signal items
        
        signal_name = item.data(0, Qt.UserRole)
        if not signal_name:
            return
        
        # Update selected signals set
        if item.checkState(0) == Qt.Checked:
            self.selected_signals.add(signal_name)
        else:
            self.selected_signals.discard(signal_name)
        
        # Emit selection changed signal
        self.signal_selection_changed.emit(list(self.selected_signals))
    
    def select_all_signals(self):
        """
        Select all signals currently visible in the tree.
        """
        self.signal_tree.blockSignals(True)
        
        # Loop through all plugin items
        for plugin_idx in range(self.signal_tree.topLevelItemCount()):
            plugin_item = self.signal_tree.topLevelItem(plugin_idx)
            
            # Loop through all signal items in this plugin
            for signal_idx in range(plugin_item.childCount()):
                signal_item = plugin_item.child(signal_idx)
                signal_name = signal_item.data(0, Qt.UserRole)
                
                signal_item.setCheckState(0, Qt.Checked)
                self.selected_signals.add(signal_name)
        
        self.signal_tree.blockSignals(False)
        self.signal_selection_changed.emit(list(self.selected_signals))
    
    def clear_all_signals(self):
        """
        Deselect all signals.
        """
        self.signal_tree.blockSignals(True)
        
        # Loop through all plugin items
        for plugin_idx in range(self.signal_tree.topLevelItemCount()):
            plugin_item = self.signal_tree.topLevelItem(plugin_idx)
            
            # Loop through all signal items in this plugin
            for signal_idx in range(plugin_item.childCount()):
                signal_item = plugin_item.child(signal_idx)
                signal_item.setCheckState(0, Qt.Unchecked)
        
        self.signal_tree.blockSignals(False)
        self.selected_signals.clear()
        self.signal_selection_changed.emit(list(self.selected_signals))
    
    def clear_all_filters(self):
        """
        Clear all filters and reset to default state.
        """
        # Clear search
        self.search_input.setText("")
        self.search_text = ""
        
        # Reset dropdowns
        self.type_combo.setCurrentIndex(0)  # "All Types"
        self.category_combo.setCurrentIndex(0)  # "All Categories"
        
        # Clear tag checkboxes
        for checkbox in self.tag_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        
        # Refresh display
        self.refresh_signals()
    
    def get_selected_signals(self) -> List[str]:
        """
        Get the currently selected signals.
        
        Returns:
            List of selected signal names
        """
        return list(self.selected_signals)
