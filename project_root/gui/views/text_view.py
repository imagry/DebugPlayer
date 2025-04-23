#!/usr/bin/env python3

"""
TextView component for the Debug Player.

This module provides a text-based visualization for logs, messages,
and other textual data with filtering and highlighting capabilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import re
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit,
    QPushButton, QLineEdit, QLabel, QComboBox, QCheckBox, QFrame,
    QSplitter, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal, QRegularExpression, QSize
from PySide6.QtGui import QTextCharFormat, QColor, QBrush, QTextCursor, QIcon, QSyntaxHighlighter, QTextDocument

from core.view_manager import ViewBase


class TextHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for log messages, keywords, and patterns.
    """
    def __init__(self, document: QTextDocument, parent=None):
        super().__init__(document)
        self.parent = parent
        
        # Format for different highlight types
        self.formats = {
            "error": self._create_format(QColor(255, 80, 80)),
            "warning": self._create_format(QColor(255, 180, 0)),
            "info": self._create_format(QColor(80, 180, 255)),
            "debug": self._create_format(QColor(180, 180, 180)),
            "highlight": self._create_format(QColor(120, 255, 120), True),
            "timestamp": self._create_format(QColor(200, 200, 255)),
            "search": self._create_format(QColor(255, 255, 0), False, True)
        }
        
        # Define highlighting rules as (pattern, format)
        self.rules = [
            # Error patterns
            (QRegularExpression(r"\b(ERROR|CRITICAL|FATAL|EXCEPTION|FAIL(ED)?)\b", 
             QRegularExpression.CaseInsensitiveOption), self.formats["error"]),
            # Warning patterns
            (QRegularExpression(r"\b(WARNING|WARN|ALERT)\b", 
             QRegularExpression.CaseInsensitiveOption), self.formats["warning"]),
            # Info patterns
            (QRegularExpression(r"\b(INFO|NOTICE|NOTE)\b", 
             QRegularExpression.CaseInsensitiveOption), self.formats["info"]),
            # Debug patterns
            (QRegularExpression(r"\b(DEBUG|TRACE|VERBOSE)\b", 
             QRegularExpression.CaseInsensitiveOption), self.formats["debug"]),
            # Timestamp patterns (ISO format and common log formats)
            (QRegularExpression(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?"), 
             self.formats["timestamp"]),
        ]
        
        # Custom search pattern (will be set dynamically)
        self.search_pattern = None
        
    def _create_format(self, color: QColor, bold: bool = False, background: bool = False) -> QTextCharFormat:
        """
        Create a text format for highlighting.
        
        Args:
            color: Color to use
            bold: Whether to use bold formatting
            background: Whether to apply color to background instead of text
            
        Returns:
            Configured QTextCharFormat
        """
        fmt = QTextCharFormat()
        
        if background:
            fmt.setBackground(QBrush(color))
        else:
            fmt.setForeground(QBrush(color))
            
        if bold:
            fmt.setFontWeight(700)  # Bold weight
            
        return fmt
        
    def set_search_pattern(self, pattern: str):
        """
        Set the current search pattern for highlighting.
        
        Args:
            pattern: Regular expression pattern string
        """
        if pattern:
            # Create case-insensitive regex for the search pattern
            self.search_pattern = QRegularExpression(
                pattern, QRegularExpression.CaseInsensitiveOption
            )
        else:
            self.search_pattern = None
            
        # Rehighlight the document
        self.rehighlight()
        
    def highlightBlock(self, text: str):
        """
        Apply highlighting to a block of text.
        
        Args:
            text: The text block to highlight
        """
        # Apply standard rules
        for pattern, format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
                
        # Apply search highlighting if active
        if self.search_pattern:
            match_iterator = self.search_pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["search"])


class TextView(ViewBase):
    """
    Text view component for displaying logs and text-based data.
    
    This view provides a text display with support for syntax highlighting,
    filtering, and search capabilities suitable for logs and messages.
    """
    # Signal emitted when text is selected
    text_selected = Signal(str)
    
    def __init__(self, view_id: str, parent=None):
        super().__init__(view_id, parent)
        
        # Set supported signal types
        self.supported_signal_types = {'text', 'temporal', 'categorical'}
        
        # Initialize data structures
        self.signal_data: Dict[str, List[str]] = {}
        self.signal_metadata: Dict[str, Dict[str, Any]] = {}
        self.active_signal: Optional[str] = None
        
        # Text display settings
        self.auto_scroll = True
        self.show_timestamps = True
        self.max_lines = 5000  # Maximum number of lines to keep
        
        # Create the widget
        self._setup_ui()
        
    def _setup_ui(self):
        """
        Set up the user interface for the text view.
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
        self.search_input.setPlaceholderText("Search in text...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        controls_layout.addWidget(self.search_input)
        
        # Search controls
        self.search_prev_btn = QToolButton()
        self.search_prev_btn.setArrowType(Qt.UpArrow)
        self.search_prev_btn.setToolTip("Find previous match")
        self.search_prev_btn.clicked.connect(self._find_previous)
        controls_layout.addWidget(self.search_prev_btn)
        
        self.search_next_btn = QToolButton()
        self.search_next_btn.setArrowType(Qt.DownArrow)
        self.search_next_btn.setToolTip("Find next match")
        self.search_next_btn.clicked.connect(self._find_next)
        controls_layout.addWidget(self.search_next_btn)
        
        # Auto-scroll checkbox
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(self.auto_scroll)
        self.auto_scroll_check.stateChanged.connect(self._on_auto_scroll_changed)
        controls_layout.addWidget(self.auto_scroll_check)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        controls_layout.addWidget(self.clear_btn)
        
        # Add controls to main layout
        layout.addLayout(controls_layout)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Create text display
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.text_edit.setMaximumBlockCount(self.max_lines)  # Limit lines for performance
        self.text_edit.setFont(self.text_edit.font())  # Use monospace font
        self.text_edit.selectionChanged.connect(self._on_selection_changed)
        
        # Create highlighter
        self.highlighter = TextHighlighter(self.text_edit.document())
        
        # Add the text display to the layout
        layout.addWidget(self.text_edit)
        
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
        
        # Update the text display with the selected signal's data
        self._refresh_text_display()
        
    def _on_search_text_changed(self, text: str):
        """
        Handle changes to the search filter.
        
        Args:
            text: New search text
        """
        self.highlighter.set_search_pattern(text)
        self._update_status()
        
        # Move to the first match if text is non-empty
        if text:
            self._find_next()
            
    def _find_next(self):
        """
        Find and scroll to the next search match.
        """
        text = self.search_input.text()
        if not text:
            return
            
        # Get current cursor position
        cursor = self.text_edit.textCursor()
        start_position = cursor.position()
        
        # Start search from current position
        self.text_edit.find(text)
        
        # If no match found, wrap around to the start
        if cursor.position() == start_position:
            cursor.movePosition(QTextCursor.Start)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.find(text)
            
    def _find_previous(self):
        """
        Find and scroll to the previous search match.
        """
        text = self.search_input.text()
        if not text:
            return
            
        # Get current cursor position
        cursor = self.text_edit.textCursor()
        start_position = cursor.position()
        
        # Start search from current position going backward
        self.text_edit.find(text, QTextDocument.FindBackward)
        
        # If no match found, wrap around to the end
        if cursor.position() == start_position:
            cursor.movePosition(QTextCursor.End)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.find(text, QTextDocument.FindBackward)
        
    def _on_auto_scroll_changed(self, state: int):
        """
        Handle auto-scroll checkbox state change.
        
        Args:
            state: New checkbox state
        """
        self.auto_scroll = state == Qt.Checked
        
    def _on_clear_clicked(self):
        """
        Handle clear button click.
        """
        if self.active_signal:
            self.signal_data[self.active_signal] = []
            self.text_edit.clear()
            self._update_status()
        
    def _on_selection_changed(self):
        """
        Handle text selection change.
        """
        selected_text = self.text_edit.textCursor().selectedText()
        if selected_text:
            self.text_selected.emit(selected_text)
            
    def _format_message(self, message: str) -> str:
        """
        Format a message for display, potentially adding timestamps.
        
        Args:
            message: Raw message text
            
        Returns:
            Formatted message
        """
        if self.show_timestamps and not re.search(r"\d{2}:\d{2}:\d{2}", message):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            return f"[{timestamp}] {message}"
        else:
            return message
            
    def _refresh_text_display(self):
        """
        Refresh the text display with current data.
        """
        if not self.active_signal or self.active_signal not in self.signal_data:
            return
            
        # Temporarily disable updates for better performance
        self.text_edit.setUpdatesEnabled(False)
        
        # Clear and repopulate the text display
        self.text_edit.clear()
        
        messages = self.signal_data[self.active_signal]
        for message in messages:
            formatted_message = self._format_message(message)
            self.text_edit.appendPlainText(formatted_message)
            
        # Scroll to bottom if auto-scroll is enabled
        if self.auto_scroll:
            self.text_edit.moveCursor(QTextCursor.End)
            
        # Re-enable updates
        self.text_edit.setUpdatesEnabled(True)
        
        # Update status
        self._update_status()
        
    def _update_status(self):
        """
        Update the status bar with current information.
        """
        if self.active_signal:
            message_count = len(self.signal_data.get(self.active_signal, []))
            search_text = self.search_input.text()
            
            if search_text:
                # Count search matches
                doc = self.text_edit.document()
                matches = 0
                
                # Use QRegularExpression for search
                regex = QRegularExpression(search_text, QRegularExpression.CaseInsensitiveOption)
                for i in range(doc.blockCount()):
                    block = doc.findBlockByNumber(i)
                    match_iterator = regex.globalMatch(block.text())
                    while match_iterator.hasNext():
                        match_iterator.next()
                        matches += 1
                
                self.status_label.setText(
                    f"{self.active_signal}: {message_count} messages, {matches} matches for '{search_text}'"
                )
            else:
                self.status_label.setText(f"{self.active_signal}: {message_count} messages")
        else:
            self.status_label.setText("No data")
    
    def update_data(self, signal_name: str, data: Any) -> bool:
        """
        Update the view with new data for a signal.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display (string, list of strings, or object with __str__)
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Initialize the signal data list if needed
            if signal_name not in self.signal_data:
                self.signal_data[signal_name] = []
                
            # Process the incoming data
            if isinstance(data, str):
                # Single string message
                self.signal_data[signal_name].append(data)
            elif isinstance(data, list) and all(isinstance(item, str) for item in data):
                # List of string messages
                self.signal_data[signal_name].extend(data)
            else:
                # Convert anything else to string
                self.signal_data[signal_name].append(str(data))
                
            # Enforce line limit
            if len(self.signal_data[signal_name]) > self.max_lines:
                self.signal_data[signal_name] = self.signal_data[signal_name][-self.max_lines:]
            
            # Update the signal selector if needed
            if signal_name not in [self.signal_combo.itemText(i) for i in range(self.signal_combo.count())]:
                self.signal_combo.addItem(signal_name)
            
            # If this is the first signal or the active signal, update the display
            if self.active_signal is None or signal_name == self.active_signal:
                self.active_signal = signal_name
                self.signal_combo.setCurrentText(signal_name)
                
                # Add new messages to the display
                if isinstance(data, list) and all(isinstance(item, str) for item in data):
                    for message in data:
                        self.text_edit.appendPlainText(self._format_message(message))
                else:
                    message = str(data) if not isinstance(data, str) else data
                    self.text_edit.appendPlainText(self._format_message(message))
                
                # Scroll to bottom if auto-scroll is enabled
                if self.auto_scroll:
                    self.text_edit.moveCursor(QTextCursor.End)
                    
                self._update_status()
            
            return True
        except Exception as e:
            print(f"Error updating text view with signal {signal_name}: {str(e)}")
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
        
    def set_max_lines(self, max_lines: int):
        """
        Set the maximum number of lines to keep in the view.
        
        Args:
            max_lines: Maximum line count
        """
        self.max_lines = max_lines
        self.text_edit.setMaximumBlockCount(max_lines)
        
        # Trim existing data if needed
        for signal_name in self.signal_data:
            if len(self.signal_data[signal_name]) > max_lines:
                self.signal_data[signal_name] = self.signal_data[signal_name][-max_lines:]
                
        # Refresh display if active signal is affected
        if self.active_signal and len(self.signal_data.get(self.active_signal, [])) > max_lines:
            self._refresh_text_display()
            
    def clear(self):
        """
        Clear all data from the view.
        """
        self.signal_data.clear()
        self.active_signal = None
        self.signal_combo.clear()
        self.text_edit.clear()
        self.status_label.setText("No data")
