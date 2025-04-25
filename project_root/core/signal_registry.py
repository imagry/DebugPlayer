#!/usr/bin/env python3

"""
Signal Registry for the Debug Player.

This module provides a centralized system for managing signals from plugins,
including registration, validation, and subscription management.
"""

from typing import Dict, Any, List, Callable, Set, Optional, Tuple
from core.signal_validation import validate_signal_definition, SignalValidationError
import logging

logger = logging.getLogger(__name__)

class SignalRegistry:
    """
    Centralized registry for managing signals from plugins.
    
    The SignalRegistry handles:
    1. Signal registration from plugins
    2. Signal validation and type checking
    3. Signal subscription management
    4. Signal metadata and discovery
    5. Signal filtering and categorization
    
    This class serves as the mediator between plugins (signal providers)
    and widgets (signal consumers), allowing for a flexible and organized
    signal management system with rich metadata support.
    """
    
    def __init__(self):
        """Initialize an empty signal registry."""
        # Main registry mapping signal names to metadata
        self.signals: Dict[str, Dict[str, Any]] = {}
        
        # Track which plugin provides each signal
        self.signal_providers: Dict[str, str] = {}
        
        # Track subscribers for each signal
        self.signal_subscribers: Dict[str, List[Any]] = {}
        
        # Store hierarchical signal information
        self.signal_hierarchy: Dict[str, Dict[str, List[str]]] = {}
        
        # Signal categorization and metadata indexes
        self.signal_categories: Dict[str, List[str]] = {}  # Categories to signal names
        self.signal_tags: Dict[str, List[str]] = {}  # Tags to signal names
        self.signal_types: Dict[str, List[str]] = {}  # Signal types to signal names
        
        # Cache of available signal types from each plugin
        self._plugin_signal_types: Dict[str, Dict[str, Set[str]]] = {}
        
    def register_signal(self, signal_name: str, signal_definition: Dict[str, Any], 
                       plugin_name: str) -> Dict[str, Any]:
        """
        Register a signal from a plugin.
        
        Args:
            signal_name: Name of the signal
            signal_definition: Dictionary containing signal metadata and access function
            plugin_name: Name of the plugin providing this signal
            
        Returns:
            The normalized signal definition dictionary
            
        Raises:
            SignalValidationError: If the signal definition is invalid
        """
        # Validate and normalize the signal definition
        normalized_signal = validate_signal_definition(signal_name, signal_definition, plugin_name)
        
        # Store in registry
        self.signals[signal_name] = normalized_signal
        self.signal_providers[signal_name] = plugin_name
        
        # Initialize subscriber list
        if signal_name not in self.signal_subscribers:
            self.signal_subscribers[signal_name] = []
            
        # Update plugin signal types cache
        signal_type = normalized_signal.get("type", "temporal")
        if plugin_name not in self._plugin_signal_types:
            self._plugin_signal_types[plugin_name] = {}
        
        if signal_type not in self._plugin_signal_types[plugin_name]:
            self._plugin_signal_types[plugin_name][signal_type] = set()
            
        self._plugin_signal_types[plugin_name][signal_type].add(signal_name)
        
        # Index by signal type for filtering
        if signal_type not in self.signal_types:
            self.signal_types[signal_type] = []
        if signal_name not in self.signal_types[signal_type]:
            self.signal_types[signal_type].append(signal_name)
        
        # Index by category for filtering
        category = normalized_signal.get("category")
        if category:
            if category not in self.signal_categories:
                self.signal_categories[category] = []
            if signal_name not in self.signal_categories[category]:
                self.signal_categories[category].append(signal_name)
        
        # Index by tags for filtering
        tags = normalized_signal.get("tags", [])
        for tag in tags:
            if tag not in self.signal_tags:
                self.signal_tags[tag] = []
            if signal_name not in self.signal_tags[tag]:
                self.signal_tags[tag].append(signal_name)
        
        # Add to signal hierarchy
        self._update_signal_hierarchy(signal_name, plugin_name, normalized_signal)
        
        logger.debug(f"Registered signal '{signal_name}' from plugin '{plugin_name}'")
        return normalized_signal
        
    def subscribe_to_signal(self, signal_name: str, subscriber: Any) -> bool:
        """
        Subscribe a widget or component to a signal.
        
        Args:
            signal_name: Name of the signal to subscribe to
            subscriber: Object that will receive signal updates
            
        Returns:
            True if subscription was successful, False otherwise
        """
        if signal_name not in self.signals:
            logger.warning(f"Cannot subscribe to unknown signal: {signal_name}")
            return False
            
        if subscriber not in self.signal_subscribers[signal_name]:
            self.signal_subscribers[signal_name].append(subscriber)
            logger.debug(f"Added subscriber to signal: {signal_name}")
        
        return True
    
    def unsubscribe_from_signal(self, signal_name: str, subscriber: Any) -> bool:
        """
        Unsubscribe a widget or component from a signal.
        
        Args:
            signal_name: Name of the signal
            subscriber: Object to unsubscribe
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        if signal_name not in self.signal_subscribers:
            return False
            
        if subscriber in self.signal_subscribers[signal_name]:
            self.signal_subscribers[signal_name].remove(subscriber)
            return True
            
        return False
    
    def get_signal_function(self, signal_name: str) -> Optional[Callable]:
        """
        Get the function that provides data for a signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            The function to call for getting signal data, or None if signal not found
        """
        if signal_name not in self.signals:
            return None
            
        return self.signals[signal_name].get("func")
    
    def get_signal_subscribers(self, signal_name: str) -> List[Any]:
        """
        Get all subscribers for a given signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            List of subscribers for the signal
        """
        return self.signal_subscribers.get(signal_name, [])
    
    def get_signals_by_type(self, signal_type: str) -> List[str]:
        """
        Get all signals of a particular type.
        
        Args:
            signal_type: Type of signals to find (e.g., "temporal", "spatial")
            
        Returns:
            List of signal names matching the requested type
        """
        return [
            signal_name for signal_name, signal_info in self.signals.items()
            if signal_info.get("type") == signal_type
        ]
    
    def get_signals_by_plugin(self, plugin_name: str) -> List[str]:
        """
        Get all signals provided by a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List of signal names provided by the plugin
        """
        return [
            signal_name for signal_name, provider in self.signal_providers.items()
            if provider == plugin_name
        ]
    
    def get_signal_metadata(self, signal_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Dictionary of signal metadata (empty if signal not found)
        """
        if signal_name not in self.signals:
            return {}
            
        # Return a copy without the function to avoid exposing implementation details
        metadata = dict(self.signals[signal_name])
        if "func" in metadata:
            del metadata["func"]
            
        return metadata
            
    def get_signal_units(self, signal_name: str) -> Optional[str]:
        """
        Get the units of measurement for a signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Units string if defined, None otherwise
        """
        if signal_name not in self.signals:
            return None
            
        return self.signals[signal_name].get("units")
    
    def get_signal_valid_range(self, signal_name: str) -> Optional[Tuple[float, float]]:
        """
        Get the valid range of values for a signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Tuple of (min, max) if defined, None otherwise
        """
        if signal_name not in self.signals:
            return None
            
        return self.signals[signal_name].get("valid_range")
    
    def get_signal_description(self, signal_name: str) -> str:
        """
        Get the human-readable description of a signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Description string, or a default description if not defined
        """
        if signal_name not in self.signals:
            return f"Unknown signal: {signal_name}"
            
        return self.signals[signal_name].get("description", f"Signal: {signal_name}")
    
    def get_critical_values(self, signal_name: str) -> Dict[str, Any]:
        """
        Get critical values for a signal (thresholds, limits, etc.).
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Dictionary of critical values if defined, empty dict otherwise
        """
        if signal_name not in self.signals:
            return {}
            
        return self.signals[signal_name].get("critical_values", {})
    
    def has_signal(self, signal_name: str) -> bool:
        """
        Check if a signal exists in the registry.
        
        Args:
            signal_name: Name of the signal to check
            
        Returns:
            True if the signal exists, False otherwise
        """
        return signal_name in self.signals
    
    def filter_signals_by_category(self, category: str) -> List[str]:
        """
        Get all signals belonging to a specific category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List of signal names in the specified category
        """
        return self.signal_categories.get(category, [])
    
    def filter_signals_by_tag(self, tag: str) -> List[str]:
        """
        Get all signals that have a specific tag.
        
        Args:
            tag: Tag name to filter by
            
        Returns:
            List of signal names with the specified tag
        """
        return self.signal_tags.get(tag, [])
    
    def filter_signals_by_metadata(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Filter signals based on arbitrary metadata criteria.
        
        This method allows for complex queries on signal metadata. For example:
        - Find all signals with units of 'm/s'
        - Find all signals with a valid range including a specific value
        - Find all signals that match multiple criteria
        
        Args:
            criteria: Dictionary of metadata field names and required values
            
        Returns:
            List of signal names matching ALL criteria
        """
        # Start with all signals
        matching_signals = set(self.signals.keys())
        
        # Filter by each criterion
        for field, value in criteria.items():
            # Handle special case for numerical range queries
            if field == "value_in_range" and isinstance(value, (int, float)):
                # Find signals where the value is within their valid range
                signals_with_valid_ranges = [
                    s for s in matching_signals
                    if self.get_signal_valid_range(s) is not None
                ]
                
                matches_this_criterion = [
                    s for s in signals_with_valid_ranges
                    if (self.get_signal_valid_range(s)[0] <= value <= 
                        self.get_signal_valid_range(s)[1])
                ]
            
            # Handle special case for tag queries (list membership)
            elif field == "tag":
                matches_this_criterion = self.filter_signals_by_tag(value)
            
            # Handle special case for category queries
            elif field == "category":
                matches_this_criterion = self.filter_signals_by_category(value)
            
            # Default case: direct metadata field matching
            else:
                matches_this_criterion = [
                    s for s in matching_signals
                    if s in self.signals and field in self.signals[s] and 
                    self.signals[s][field] == value
                ]
            
            # Intersection: signals must match ALL criteria
            matching_signals &= set(matches_this_criterion)
            
            # Early exit if no matches left
            if not matching_signals:
                break
        
        return list(matching_signals)
    
    def search_signals(self, search_term: str) -> List[str]:
        """
        Search for signals by name or description.
        
        Args:
            search_term: Text to search for in signal names and descriptions
            
        Returns:
            List of signal names matching the search term
        """
        search_term = search_term.lower()
        matching_signals = []
        
        for signal_name, signal_info in self.signals.items():
            # Check signal name
            if search_term in signal_name.lower():
                matching_signals.append(signal_name)
                continue
                
            # Check description if available
            description = signal_info.get("description", "")
            if description and search_term in description.lower():
                matching_signals.append(signal_name)
                continue
        
        return matching_signals
    
    def _update_signal_hierarchy(self, signal_name: str, plugin_name: str, 
                                signal_info: Dict[str, Any]) -> None:
        """
        Update the signal hierarchy with a new signal.
        
        This handles grouping signals by categories, types, etc.
        
        Args:
            signal_name: Name of the signal
            plugin_name: Name of the provider plugin
            signal_info: Signal definition dictionary
        """
        # Initialize hierarchy if needed
        if plugin_name not in self.signal_hierarchy:
            self.signal_hierarchy[plugin_name] = {}
            
        # Add by signal type
        signal_type = signal_info.get("type", "unknown")
        if signal_type not in self.signal_hierarchy[plugin_name]:
            self.signal_hierarchy[plugin_name][signal_type] = []
            
        self.signal_hierarchy[plugin_name][signal_type].append(signal_name)
        
        # Add by category if provided
        category = signal_info.get("category")
        if category:
            if category not in self.signal_hierarchy[plugin_name]:
                self.signal_hierarchy[plugin_name][category] = []
                
            self.signal_hierarchy[plugin_name][category].append(signal_name)
