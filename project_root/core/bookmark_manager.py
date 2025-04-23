#!/usr/bin/env python3

"""
Bookmark Manager for the Debug Player.

This module provides functionality for saving, organizing, and retrieving
timestamp bookmarks, allowing users to mark and quickly navigate to
important points in their data.
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Bookmark:
    """
    Represents a single bookmark in the Debug Player.
    
    Attributes:
        timestamp: The timestamp value (in seconds)
        name: User-friendly name for this bookmark
        description: Optional longer description
        created_at: When this bookmark was created
        tags: Optional list of tags for categorization
        color: Optional color for visual identification
    """
    timestamp: float
    name: str
    description: str = ""
    created_at: str = ""
    tags: List[str] = None
    color: str = "#3498db"  # Default blue color
    
    def __post_init__(self):
        # Set created_at to current time if not provided
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        
        # Initialize tags as empty list if None
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bookmark to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "tags": self.tags,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bookmark':
        """Create a bookmark from a dictionary."""
        return cls(
            timestamp=data["timestamp"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            tags=data.get("tags", []),
            color=data.get("color", "#3498db")
        )


class BookmarkManager:
    """
    Manages bookmarks for the Debug Player.
    
    This class handles the creation, deletion, and organization of bookmarks,
    as well as loading and saving bookmarks to a file for persistence.
    """
    
    def __init__(self, save_path: Optional[str] = None):
        """
        Initialize the bookmark manager.
        
        Args:
            save_path: Optional path to save bookmarks. If None, bookmarks
                      will not be persisted between sessions.
        """
        self.bookmarks: List[Bookmark] = []
        self.save_path = save_path
        self.current_session_tag = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Load bookmarks if save path exists
        if save_path and os.path.exists(save_path):
            self.load_bookmarks()
    
    def add_bookmark(self, timestamp: float, name: str, description: str = "", 
                     tags: List[str] = None, color: str = "#3498db") -> Bookmark:
        """
        Add a new bookmark.
        
        Args:
            timestamp: The timestamp to bookmark
            name: Name for the bookmark
            description: Optional description
            tags: Optional list of tags
            color: Optional color in hex format
            
        Returns:
            The created Bookmark object
        """
        # Add session tag to tags list
        all_tags = tags or []
        if self.current_session_tag not in all_tags:
            all_tags.append(self.current_session_tag)
            
        # Create and add the bookmark
        bookmark = Bookmark(
            timestamp=timestamp,
            name=name,
            description=description,
            tags=all_tags,
            color=color
        )
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        return bookmark
    
    def remove_bookmark(self, bookmark_idx: int) -> bool:
        """
        Remove a bookmark by index.
        
        Args:
            bookmark_idx: Index of the bookmark to remove
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= bookmark_idx < len(self.bookmarks):
            self.bookmarks.pop(bookmark_idx)
            self.save_bookmarks()
            return True
        return False
    
    def get_bookmarks(self, tag: Optional[str] = None) -> List[Bookmark]:
        """
        Get all bookmarks, optionally filtered by tag.
        
        Args:
            tag: Optional tag to filter by
            
        Returns:
            List of bookmarks
        """
        if tag is None:
            return self.bookmarks
        
        return [b for b in self.bookmarks if tag in b.tags]
    
    def get_closest_bookmark(self, timestamp: float) -> Tuple[int, Bookmark]:
        """
        Find the bookmark closest to the given timestamp.
        
        Args:
            timestamp: The reference timestamp
            
        Returns:
            Tuple of (index, bookmark) or (-1, None) if no bookmarks exist
        """
        if not self.bookmarks:
            return -1, None
        
        closest_idx = 0
        closest_diff = abs(self.bookmarks[0].timestamp - timestamp)
        
        for i, bookmark in enumerate(self.bookmarks[1:], 1):
            diff = abs(bookmark.timestamp - timestamp)
            if diff < closest_diff:
                closest_diff = diff
                closest_idx = i
        
        return closest_idx, self.bookmarks[closest_idx]
    
    def save_bookmarks(self):
        """
        Save bookmarks to the specified file path.
        """
        if not self.save_path:
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        
        # Convert bookmarks to dictionaries
        bookmark_dicts = [b.to_dict() for b in self.bookmarks]
        
        # Save to file
        with open(self.save_path, 'w') as f:
            json.dump(bookmark_dicts, f, indent=2)
    
    def load_bookmarks(self):
        """
        Load bookmarks from the specified file path.
        """
        if not self.save_path or not os.path.exists(self.save_path):
            return
        
        try:
            with open(self.save_path, 'r') as f:
                bookmark_dicts = json.load(f)
            
            # Convert dictionaries to Bookmark objects
            self.bookmarks = [Bookmark.from_dict(d) for d in bookmark_dicts]
        except (json.JSONDecodeError, FileNotFoundError):
            # Start with empty bookmarks if file is invalid or missing
            self.bookmarks = []
            
    def get_all_tags(self) -> List[str]:
        """
        Get a list of all unique tags used in bookmarks.
        
        Returns:
            List of unique tags
        """
        tags = set()
        for bookmark in self.bookmarks:
            tags.update(bookmark.tags)
        return sorted(list(tags))
