#!/usr/bin/env python3

"""
View Manager for the Debug Player.

This module provides a flexible system for managing different view types
and coordinating the display of data from various signals.
"""

from typing import Dict, Any, List, Type, Optional, Set
from PySide6.QtWidgets import QWidget
import logging

logger = logging.getLogger(__name__)

class ViewBase:
    """
    Base class for all view types in the Debug Player.
    
    Views are responsible for displaying data from signals. Each view type
    handles specific signal types and provides visualization options.
    """
    
    def __init__(self, view_id: str, parent: Optional[QWidget] = None):
        """
        Initialize a new view.
        
        Args:
            view_id: Unique identifier for this view
            parent: Optional parent widget
        """
        self.view_id = view_id
        self.parent = parent
        self.supported_signal_types: Set[str] = set()
        self.widget: Optional[QWidget] = None
        
    def can_display_signal(self, signal_type: str) -> bool:
        """
        Check if this view can display a specific signal type.
        
        Args:
            signal_type: The type of signal to check
            
        Returns:
            True if this view can display the signal, False otherwise
        """
        return signal_type in self.supported_signal_types
        
    def update_data(self, signal_name: str, data: Any) -> bool:
        """
        Update the view with new data.
        
        Args:
            signal_name: Name of the signal providing the data
            data: The data to display
            
        Returns:
            True if the update was successful, False otherwise
        """
        raise NotImplementedError("View classes must implement update_data")
        
    def get_widget(self) -> QWidget:
        """
        Get the Qt widget for this view.
        
        Returns:
            The QWidget that displays this view
        """
        if self.widget is None:
            raise ValueError(f"View {self.view_id} has no widget")
        return self.widget


class ViewManager:
    """
    Manager for coordinating different view types.
    
    The ViewManager:
    1. Registers and manages different view types
    2. Creates view instances for specific signal display
    3. Coordinates data flow from signals to views
    4. Supports custom view templates and layouts
    """
    
    def __init__(self):
        """Initialize an empty view manager."""
        # Available view classes by type
        self.view_classes: Dict[str, Type[ViewBase]] = {}
        
        # Active view instances
        self.views: Dict[str, ViewBase] = {}
        
        # View templates (predefined configurations)
        self.templates: Dict[str, Dict[str, Any]] = {}
        
        # Signal-to-view mapping
        self.signal_views: Dict[str, List[str]] = {}
        
        # View configurations
        self.view_configs: Dict[str, Dict[str, Any]] = {}
        
    def register_view_class(self, view_type: str, view_class: Type[ViewBase]) -> None:
        """
        Register a view class with the manager.
        
        Args:
            view_type: Identifier for this view type
            view_class: The view class to register
        """
        self.view_classes[view_type] = view_class
        logger.debug(f"Registered view class: {view_type}")
        
    def create_view(self, view_id: str, view_type: str, 
                   config: Optional[Dict[str, Any]] = None,
                   parent: Optional[QWidget] = None) -> ViewBase:
        """
        Create a new view instance.
        
        Args:
            view_id: Unique identifier for the new view
            view_type: The type of view to create
            config: Optional configuration for the view
            parent: Optional parent widget
            
        Returns:
            The created view instance
            
        Raises:
            ValueError: If the view type is not registered or the view_id already exists
        """
        if view_type not in self.view_classes:
            raise ValueError(f"Unknown view type: {view_type}")
            
        if view_id in self.views:
            raise ValueError(f"View ID already exists: {view_id}")
            
        # Create view instance
        view_class = self.view_classes[view_type]
        view = view_class(view_id, parent)
        
        # Apply configuration if provided
        if config:
            self._apply_config(view, config)
            self.view_configs[view_id] = config
            
        # Store the view
        self.views[view_id] = view
        logger.debug(f"Created view: {view_id} (type: {view_type})")
        
        return view
        
    def get_view(self, view_id: str) -> Optional[ViewBase]:
        """
        Get a view by its ID.
        
        Args:
            view_id: The ID of the view to retrieve
            
        Returns:
            The view if found, None otherwise
        """
        return self.views.get(view_id)
        
    def remove_view(self, view_id: str) -> bool:
        """
        Remove a view by its ID.
        
        Args:
            view_id: The ID of the view to remove
            
        Returns:
            True if the view was removed, False otherwise
        """
        if view_id not in self.views:
            return False
            
        # Clean up signal mappings
        for signal, views in list(self.signal_views.items()):
            if view_id in views:
                views.remove(view_id)
                if not views:
                    del self.signal_views[signal]
                    
        # Remove configuration
        if view_id in self.view_configs:
            del self.view_configs[view_id]
            
        # Remove the view
        del self.views[view_id]
        logger.debug(f"Removed view: {view_id}")
        
        return True
        
    def connect_signal_to_view(self, signal_name: str, view_id: str) -> bool:
        """
        Connect a signal to a view.
        
        Args:
            signal_name: The name of the signal to connect
            view_id: The ID of the view to connect to
            
        Returns:
            True if the connection was made, False otherwise
        """
        if view_id not in self.views:
            logger.warning(f"Cannot connect signal to unknown view: {view_id}")
            return False
            
        # Initialize signal views list if needed
        if signal_name not in self.signal_views:
            self.signal_views[signal_name] = []
            
        # Add the view if not already connected
        if view_id not in self.signal_views[signal_name]:
            self.signal_views[signal_name].append(view_id)
            logger.debug(f"Connected signal '{signal_name}' to view '{view_id}'")
            
        return True
        
    def disconnect_signal_from_view(self, signal_name: str, view_id: str) -> bool:
        """
        Disconnect a signal from a view.
        
        Args:
            signal_name: The name of the signal to disconnect
            view_id: The ID of the view to disconnect from
            
        Returns:
            True if the disconnection was made, False otherwise
        """
        if signal_name not in self.signal_views:
            return False
            
        if view_id in self.signal_views[signal_name]:
            self.signal_views[signal_name].remove(view_id)
            logger.debug(f"Disconnected signal '{signal_name}' from view '{view_id}'")
            
            # Clean up empty signal mappings
            if not self.signal_views[signal_name]:
                del self.signal_views[signal_name]
                
            return True
            
        return False
        
    def update_signal_data(self, signal_name: str, data: Any) -> int:
        """
        Update all views connected to a signal with new data.
        
        Args:
            signal_name: The name of the signal with new data
            data: The new data
            
        Returns:
            The number of views updated
        """
        if signal_name not in self.signal_views:
            return 0
            
        updated_count = 0
        for view_id in self.signal_views[signal_name]:
            view = self.views.get(view_id)
            if view and view.update_data(signal_name, data):
                updated_count += 1
                
        return updated_count
        
    def register_template(self, template_name: str, template_config: Dict[str, Any]) -> None:
        """
        Register a view template for easy instantiation.
        
        Args:
            template_name: Name for this template
            template_config: Configuration dict for the template
        """
        self.templates[template_name] = template_config
        logger.debug(f"Registered view template: {template_name}")
        
    def create_view_from_template(self, view_id: str, template_name: str,
                                 parent: Optional[QWidget] = None) -> Optional[ViewBase]:
        """
        Create a view from a template.
        
        Args:
            view_id: Unique identifier for the new view
            template_name: Name of the template to use
            parent: Optional parent widget
            
        Returns:
            The created view, or None if the template wasn't found
        """
        if template_name not in self.templates:
            logger.warning(f"Unknown template: {template_name}")
            return None
            
        template = self.templates[template_name]
        view_type = template.get("type")
        
        if not view_type:
            logger.error(f"Template {template_name} missing required 'type' field")
            return None
            
        view = self.create_view(view_id, view_type, template.get("config"), parent)
        
        # Connect signals if specified in the template
        signals = template.get("signals", [])
        for signal in signals:
            self.connect_signal_to_view(signal, view_id)
            
        return view
        
    def get_views_for_signal(self, signal_name: str) -> List[ViewBase]:
        """
        Get all views connected to a specific signal.
        
        Args:
            signal_name: The name of the signal
            
        Returns:
            List of views connected to the signal
        """
        if signal_name not in self.signal_views:
            return []
            
        return [self.views[view_id] for view_id in self.signal_views[signal_name]
                if view_id in self.views]
                
    def save_layout(self) -> Dict[str, Any]:
        """
        Save the current view layout configuration.
        
        Returns:
            Dictionary containing the layout configuration
        """
        layout = {
            "views": {},
            "connections": {},
        }
        
        # Save view configurations
        for view_id, view in self.views.items():
            view_type = next((k for k, v in self.view_classes.items() 
                           if isinstance(view, v)), None)
            if view_type:
                layout["views"][view_id] = {
                    "type": view_type,
                    "config": self.view_configs.get(view_id, {})
                }
        
        # Save signal connections
        for signal, view_ids in self.signal_views.items():
            layout["connections"][signal] = view_ids.copy()
            
        return layout
        
    def load_layout(self, layout: Dict[str, Any], 
                   parent: Optional[QWidget] = None) -> bool:
        """
        Load a saved view layout configuration.
        
        Args:
            layout: Layout configuration dictionary
            parent: Optional parent widget
            
        Returns:
            True if the layout was loaded successfully, False otherwise
        """
        try:
            # Clear existing views and connections
            self.views.clear()
            self.signal_views.clear()
            self.view_configs.clear()
            
            # Create views
            for view_id, view_info in layout.get("views", {}).items():
                view_type = view_info.get("type")
                config = view_info.get("config", {})
                self.create_view(view_id, view_type, config, parent)
                
            # Set up connections
            for signal, view_ids in layout.get("connections", {}).items():
                for view_id in view_ids:
                    self.connect_signal_to_view(signal, view_id)
                    
            logger.info("Successfully loaded view layout")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load layout: {str(e)}")
            return False
            
    def _apply_config(self, view: ViewBase, config: Dict[str, Any]) -> None:
        """
        Apply configuration to a view.
        
        Args:
            view: The view to configure
            config: Configuration dictionary
        """
        # Generic configuration application
        # Specific view types may override or extend this
        for key, value in config.items():
            if hasattr(view, key):
                setattr(view, key, value)
                
        # Call configure method if it exists
        if hasattr(view, "configure") and callable(getattr(view, "configure")):
            view.configure(config)
