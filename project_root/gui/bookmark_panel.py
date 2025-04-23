#!/usr/bin/env python3

"""
Bookmark Panel for the Debug Player.

This module provides a dockable panel for managing bookmarks,
allowing users to save, organize, and quickly navigate to important
timestamps in their data.
"""

from typing import List, Callable, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLineEdit, QLabel, QListWidget, QListWidgetItem,
                              QMenu, QInputDialog, QColorDialog, QMessageBox,
                              QDialog, QDialogButtonBox, QFormLayout, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QColor, QBrush
import os

from core.bookmark_manager import BookmarkManager, Bookmark


class BookmarkDialog(QDialog):
    """
    Dialog for adding or editing a bookmark.
    """
    def __init__(self, parent=None, timestamp=0.0, existing_bookmark: Optional[Bookmark] = None):
        super().__init__(parent)
        self.setWindowTitle("Add Bookmark" if existing_bookmark is None else "Edit Bookmark")
        self.resize(400, 300)
        
        # Store the existing bookmark if editing
        self.existing_bookmark = existing_bookmark
        
        # Create form layout
        layout = QFormLayout(self)
        
        # Timestamp field (readonly if editing existing bookmark)
        self.timestamp_field = QLineEdit(str(timestamp))
        if existing_bookmark:
            self.timestamp_field.setText(str(existing_bookmark.timestamp))
            self.timestamp_field.setReadOnly(True)
        layout.addRow("Timestamp:", self.timestamp_field)
        
        # Name field
        self.name_field = QLineEdit()
        if existing_bookmark:
            self.name_field.setText(existing_bookmark.name)
        layout.addRow("Name:", self.name_field)
        
        # Description field
        self.description_field = QTextEdit()
        if existing_bookmark:
            self.description_field.setText(existing_bookmark.description)
        layout.addRow("Description:", self.description_field)
        
        # Tags field
        self.tags_field = QLineEdit()
        if existing_bookmark and existing_bookmark.tags:
            self.tags_field.setText(", ".join(existing_bookmark.tags))
        layout.addRow("Tags (comma separated):", self.tags_field)
        
        # Color button
        self.color = QColor(existing_bookmark.color if existing_bookmark else "#3498db")
        self.color_button = QPushButton()
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        self.color_button.clicked.connect(self.choose_color)
        layout.addRow("Color:", self.color_button)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def choose_color(self):
        color = QColorDialog.getColor(self.color, self, "Select Bookmark Color")
        if color.isValid():
            self.color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
    
    def get_bookmark_data(self):
        """Get the data for creating a bookmark."""
        try:
            timestamp = float(self.timestamp_field.text())
        except ValueError:
            timestamp = 0.0
            
        name = self.name_field.text().strip()
        if not name:
            name = f"Bookmark at {timestamp:.2f}s"
            
        description = self.description_field.toPlainText()
        
        # Split tags by comma and strip whitespace
        tags_text = self.tags_field.text().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        
        return {
            "timestamp": timestamp,
            "name": name,
            "description": description,
            "tags": tags,
            "color": self.color.name()
        }


class BookmarkPanel(QWidget):
    """
    Panel for displaying and managing bookmarks.
    """
    # Signal emitted when a bookmark is selected for navigation
    bookmark_selected = Signal(float)  # timestamp in seconds
    
    def __init__(self, parent=None, bookmark_manager: Optional[BookmarkManager] = None):
        super().__init__(parent)
        
        # Initialize bookmark manager if not provided
        self.bookmark_manager = bookmark_manager or BookmarkManager()
        
        # Track current timestamp for adding bookmarks
        self.current_timestamp = 0.0
        
        self._setup_ui()
        self._populate_bookmark_list()
    
    def _setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Header with title
        header_layout = QHBoxLayout()
        title_label = QLabel("Bookmarks")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)
        
        # Button row
        button_layout = QHBoxLayout()
        
        # Add bookmark button
        self.add_button = QPushButton("Add")
        self.add_button.setToolTip("Add bookmark at current timestamp")
        self.add_button.clicked.connect(self.add_bookmark)
        button_layout.addWidget(self.add_button)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search bookmarks...")
        self.search_field.textChanged.connect(self._filter_bookmarks)
        button_layout.addWidget(self.search_field)
        
        layout.addLayout(button_layout)
        
        # Bookmark list
        self.bookmark_list = QListWidget()
        self.bookmark_list.setAlternatingRowColors(True)
        self.bookmark_list.itemDoubleClicked.connect(self._on_bookmark_double_clicked)
        self.bookmark_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.bookmark_list)
    
    def _populate_bookmark_list(self, filter_text: str = ""):
        """Populate the bookmark list, optionally filtering by text."""
        self.bookmark_list.clear()
        
        # Get bookmarks from manager
        bookmarks = self.bookmark_manager.get_bookmarks()
        
        # Apply filter if needed
        if filter_text:
            filter_text = filter_text.lower()
            bookmarks = [
                b for b in bookmarks if (
                    filter_text in b.name.lower() or
                    filter_text in b.description.lower() or
                    any(filter_text in tag.lower() for tag in b.tags)
                )
            ]
        
        # Sort bookmarks by timestamp
        bookmarks.sort(key=lambda b: b.timestamp)
        
        # Add to list widget
        for idx, bookmark in enumerate(bookmarks):
            item = QListWidgetItem(f"{bookmark.timestamp:.2f}s - {bookmark.name}")
            item.setData(Qt.UserRole, idx)  # Store original index
            
            # Set item color
            brush = QBrush(QColor(bookmark.color))
            item.setForeground(brush)
            
            self.bookmark_list.addItem(item)
    
    def _filter_bookmarks(self):
        """Filter bookmarks based on search text."""
        filter_text = self.search_field.text()
        self._populate_bookmark_list(filter_text)
    
    def _on_bookmark_double_clicked(self, item):
        """Handle double-click on bookmark item."""
        idx = item.data(Qt.UserRole)
        bookmark = self.bookmark_manager.bookmarks[idx]
        self.bookmark_selected.emit(bookmark.timestamp)
    
    def _show_context_menu(self, position):
        """Show context menu for bookmark item."""
        item = self.bookmark_list.itemAt(position)
        if not item:
            return
        
        # Get bookmark index
        idx = item.data(Qt.UserRole)
        bookmark = self.bookmark_manager.bookmarks[idx]
        
        # Create context menu
        menu = QMenu()
        go_to_action = menu.addAction("Go to Bookmark")
        edit_action = menu.addAction("Edit Bookmark")
        delete_action = menu.addAction("Delete Bookmark")
        
        # Show menu and handle actions
        action = menu.exec_(self.bookmark_list.mapToGlobal(position))
        
        if action == go_to_action:
            self.bookmark_selected.emit(bookmark.timestamp)
        elif action == edit_action:
            self._edit_bookmark(idx, bookmark)
        elif action == delete_action:
            self._delete_bookmark(idx)
    
    def _edit_bookmark(self, idx, bookmark):
        """Open dialog to edit bookmark."""
        dialog = BookmarkDialog(self, bookmark.timestamp, bookmark)
        if dialog.exec_():
            # Get updated data
            data = dialog.get_bookmark_data()
            
            # Update bookmark
            self.bookmark_manager.bookmarks[idx].name = data["name"]
            self.bookmark_manager.bookmarks[idx].description = data["description"]
            self.bookmark_manager.bookmarks[idx].tags = data["tags"]
            self.bookmark_manager.bookmarks[idx].color = data["color"]
            
            # Save and refresh
            self.bookmark_manager.save_bookmarks()
            self._populate_bookmark_list(self.search_field.text())
    
    def _delete_bookmark(self, idx):
        """Delete bookmark after confirmation."""
        bookmark = self.bookmark_manager.bookmarks[idx]
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Delete Bookmark",
            f"Are you sure you want to delete the bookmark '{bookmark.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.bookmark_manager.remove_bookmark(idx)
            self._populate_bookmark_list(self.search_field.text())
    
    def add_bookmark(self):
        """Open dialog to add a new bookmark."""
        dialog = BookmarkDialog(self, self.current_timestamp)
        if dialog.exec_():
            # Get bookmark data
            data = dialog.get_bookmark_data()
            
            # Add bookmark
            self.bookmark_manager.add_bookmark(
                timestamp=data["timestamp"],
                name=data["name"],
                description=data["description"],
                tags=data["tags"],
                color=data["color"]
            )
            
            # Refresh list
            self._populate_bookmark_list(self.search_field.text())
    
    def set_current_timestamp(self, timestamp):
        """Update the current timestamp for adding bookmarks."""
        self.current_timestamp = timestamp
    
    def navigate_to_next_bookmark(self):
        """Navigate to the next bookmark after the current timestamp."""
        bookmarks = self.bookmark_manager.get_bookmarks()
        if not bookmarks:
            return
        
        # Sort bookmarks by timestamp
        bookmarks.sort(key=lambda b: b.timestamp)
        
        # Find next bookmark
        next_bookmark = None
        for bookmark in bookmarks:
            if bookmark.timestamp > self.current_timestamp:
                next_bookmark = bookmark
                break
        
        # If no next bookmark, loop back to first
        if next_bookmark is None and bookmarks:
            next_bookmark = bookmarks[0]
        
        # Navigate to bookmark
        if next_bookmark:
            self.bookmark_selected.emit(next_bookmark.timestamp)
    
    def navigate_to_previous_bookmark(self):
        """Navigate to the previous bookmark before the current timestamp."""
        bookmarks = self.bookmark_manager.get_bookmarks()
        if not bookmarks:
            return
        
        # Sort bookmarks by timestamp
        bookmarks.sort(key=lambda b: b.timestamp)
        
        # Find previous bookmark
        prev_bookmark = None
        for bookmark in reversed(bookmarks):
            if bookmark.timestamp < self.current_timestamp:
                prev_bookmark = bookmark
                break
        
        # If no previous bookmark, loop to last
        if prev_bookmark is None and bookmarks:
            prev_bookmark = bookmarks[-1]
        
        # Navigate to bookmark
        if prev_bookmark:
            self.bookmark_selected.emit(prev_bookmark.timestamp)
