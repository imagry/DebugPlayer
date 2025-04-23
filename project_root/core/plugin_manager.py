#!/usr/bin/env python3

"""
Plugin Manager for the Debug Player.

This module provides the PluginManager class, which handles plugin discovery,
loading, validation, and management.
"""

import os
import sys
import importlib.util
import inspect
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Type, Set
from pathlib import Path
from packaging import version

from interfaces.PluginBase import PluginBase
from core.signal_registry import SignalRegistry

# Configure logger
logger = logging.getLogger(__name__)

# Constants for plugin validation
REQUIRED_METADATA = ['name', 'version', 'description', 'author']
VALID_PLUGIN_TYPES = ['data_source', 'visualization', 'processor', 'exporter']

# Regex pattern for semantic versioning
SEMVER_PATTERN = r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$'

class PluginValidationError(Exception):
    """Exception raised when a plugin fails validation."""
    pass

class PluginManager:
    """
    Manager for discovering, loading, validating, and managing plugins.
    
    The PluginManager is responsible for:
    1. Discovering plugins from directories and files
    2. Validating plugins against the required interface
    3. Loading plugins into the system
    4. Managing plugin lifecycle and dependencies
    5. Handling plugin versions and compatibility
    
    It provides a central registry of all available plugins and their metadata.
    """
    
    def __init__(self, signal_registry: Optional[SignalRegistry] = None):
        """
        Initialize a new PluginManager instance.
        
        Args:
            signal_registry: Optional SignalRegistry instance for signal handling.
                If None, a new SignalRegistry will be created.
        """
        # Create or store the signal registry
        self.signal_registry = signal_registry or SignalRegistry()
        
        # Dictionary of loaded plugin instances by name
        self.plugins: Dict[str, PluginBase] = {}
        
        # Store plugin metadata for each plugin
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Store plugin classes for lazy loading
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        
        # Track loaded plugin files and directories
        self._loaded_files: Set[str] = set()
        self._loaded_directories: Set[str] = set()
        
        # Track discovery paths for runtime plugin loading
        self.plugin_discovery_paths: List[str] = []
        
        logger.debug("PluginManager initialized")
    
    def discover_plugins(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Discover all plugins in the given directory without loading them.
        
        This method scans the directory for Python files that contain plugin classes,
        validates them, and returns metadata about the discovered plugins.
        
        Args:
            directory_path: Path to the directory to scan for plugins
            
        Returns:
            List of dictionaries containing plugin metadata
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Plugin directory does not exist: {directory_path}")
            return []
        
        # Add to discovery paths if not already there
        if directory_path not in self.plugin_discovery_paths:
            self.plugin_discovery_paths.append(directory_path)
        
        discovered_plugins = []
        
        # Scan for Python files
        for filename in os.listdir(directory_path):
            if not filename.endswith('.py'):
                continue
                
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Extract plugin metadata without fully loading
                metadata = self._extract_plugin_metadata(file_path)
                if metadata:
                    discovered_plugins.append(metadata)
            except Exception as e:
                logger.warning(f"Error discovering plugin in {file_path}: {str(e)}")
        
        logger.info(f"Discovered {len(discovered_plugins)} plugins in {directory_path}")
        return discovered_plugins
    
    def load_plugins_from_directory(self, directory_path: str, plugin_args: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Load all plugins from the given directory.
        
        Args:
            directory_path: Path to the directory containing plugin files
            plugin_args: Optional arguments to pass to plugin constructors
            
        Returns:
            List of names of successfully loaded plugins
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Plugin directory does not exist: {directory_path}")
            return []
        
        # Add to discovery paths if not already there
        if directory_path not in self.plugin_discovery_paths:
            self.plugin_discovery_paths.append(directory_path)
        
        # Add to loaded directories
        self._loaded_directories.add(directory_path)
        
        loaded_plugins = []
        
        # Scan for Python files
        for filename in os.listdir(directory_path):
            if not filename.endswith('.py'):
                continue
                
            file_path = os.path.join(directory_path, filename)
            module_name = os.path.splitext(filename)[0]
            
            try:
                plugin_name = self.load_plugin_from_file(module_name, file_path, plugin_args)
                if plugin_name:
                    loaded_plugins.append(plugin_name)
            except Exception as e:
                logger.error(f"Error loading plugin from {file_path}: {str(e)}")
        
        logger.info(f"Loaded {len(loaded_plugins)} plugins from {directory_path}")
        return loaded_plugins
    
    def load_plugin_from_file(self, module_name: str, file_path: str, plugin_args: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Load a plugin from a specified Python file.
        
        Args:
            module_name: Name to use for the imported module
            file_path: Path to the Python file containing the plugin
            plugin_args: Optional arguments to pass to the plugin constructor
            
        Returns:
            Name of the loaded plugin or None if loading failed
            
        Raises:
            PluginValidationError: If the plugin fails validation
        """
        if file_path in self._loaded_files:
            logger.debug(f"Plugin file already loaded: {file_path}")
            return None
        
        if not os.path.isfile(file_path):
            logger.error(f"Plugin file does not exist: {file_path}")
            return None
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.error(f"Failed to create module spec for {file_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find the plugin class
            if not hasattr(module, 'plugin_class'):
                logger.error(f"Module {module_name} does not define 'plugin_class'")
                return None
                
            plugin_class = module.plugin_class
            
            # Validate the plugin class
            self._validate_plugin_class(plugin_class)
            
            # Extract metadata
            metadata = self._extract_metadata_from_class(plugin_class)
            plugin_name = metadata['name']
            
            # Check if a plugin with this name is already loaded
            if plugin_name in self.plugins:
                # Check versions if the plugin is already registered
                existing_version = self.plugin_metadata[plugin_name]['version']
                new_version = metadata['version']
                
                if version.parse(new_version) <= version.parse(existing_version):
                    logger.info(f"Skipping plugin '{plugin_name}' v{new_version}: already loaded v{existing_version}")
                    return None
                else:
                    logger.info(f"Upgrading plugin '{plugin_name}' from v{existing_version} to v{new_version}")
            
            # Store the metadata
            self.plugin_metadata[plugin_name] = metadata
            
            # Store the plugin class for lazy loading
            self._plugin_classes[plugin_name] = plugin_class
            
            # Instantiate the plugin if args provided
            if plugin_args is not None:
                self._instantiate_plugin(plugin_name, plugin_args)
            
            # Mark file as loaded
            self._loaded_files.add(file_path)
            
            logger.info(f"Successfully loaded plugin '{plugin_name}' v{metadata['version']} from {file_path}")
            return plugin_name
            
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {str(e)}")
            return None
    
    def _instantiate_plugin(self, plugin_name: str, plugin_args: Dict[str, Any]) -> bool:
        """
        Instantiate a plugin by name using the provided arguments.
        
        Args:
            plugin_name: Name of the plugin to instantiate
            plugin_args: Arguments to pass to the plugin constructor
            
        Returns:
            True if instantiation was successful, False otherwise
        """
        if plugin_name not in self._plugin_classes:
            logger.error(f"Cannot instantiate unknown plugin: {plugin_name}")
            return False
        
        try:
            # Create instance of the plugin
            plugin_class = self._plugin_classes[plugin_name]
            plugin_instance = plugin_class(**plugin_args)
            
            # Register the plugin instance
            self.plugins[plugin_name] = plugin_instance
            
            # Register all signals from the plugin
            for signal_name, signal_info in plugin_instance.signals.items():
                self.signal_registry.register_signal(signal_name, signal_info, plugin_name)
            
            return True
        except Exception as e:
            logger.error(f"Error instantiating plugin '{plugin_name}': {str(e)}")
            return False
    
    def _validate_plugin_class(self, plugin_class) -> None:
        """
        Validate that a class fulfills the plugin interface requirements.
        
        Args:
            plugin_class: The class to validate
            
        Raises:
            PluginValidationError: If the class does not meet the requirements
        """
        # Check inheritance
        if not issubclass(plugin_class, PluginBase):
            raise PluginValidationError(f"Plugin class must inherit from PluginBase")
        
        # Check required methods are implemented
        for method_name in ['__init__', 'has_signal', 'get_data_for_timestamp']:
            if not hasattr(plugin_class, method_name):
                raise PluginValidationError(f"Plugin class missing required method: {method_name}")
            method = getattr(plugin_class, method_name)
            if not callable(method):
                raise PluginValidationError(f"Plugin attribute {method_name} must be callable")
        
        # Check metadata
        metadata = self._extract_metadata_from_class(plugin_class)
        for field in REQUIRED_METADATA:
            if field not in metadata:
                raise PluginValidationError(f"Plugin missing required metadata field: {field}")
        
        # Validate version format
        version_str = metadata.get('version', '')
        if not re.match(SEMVER_PATTERN, version_str):
            raise PluginValidationError(f"Plugin version '{version_str}' does not follow semantic versioning")
        
        # Validate plugin type
        plugin_type = metadata.get('type', '')
        if plugin_type and plugin_type not in VALID_PLUGIN_TYPES:
            raise PluginValidationError(f"Invalid plugin type: {plugin_type}. Must be one of {VALID_PLUGIN_TYPES}")
    
    def _extract_metadata_from_class(self, plugin_class) -> Dict[str, Any]:
        """
        Extract metadata from a plugin class.
        
        Args:
            plugin_class: The plugin class to extract metadata from
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = {}
        
        # Get metadata from class docstring
        if plugin_class.__doc__:
            doc = plugin_class.__doc__.strip()
            # Extract name from class name if not specified
            if 'name' not in metadata:
                class_name = plugin_class.__name__
                # Convert CamelCase to title case with spaces
                name = re.sub(r'(?<!^)(?=[A-Z])', ' ', class_name).title()
                # Remove 'Plugin' suffix if present
                name = name.replace(' Plugin', '')
                metadata['name'] = name
        
        # Check for metadata class attribute
        if hasattr(plugin_class, 'METADATA') and isinstance(plugin_class.METADATA, dict):
            metadata.update(plugin_class.METADATA)
        
        return metadata
    
    def _extract_plugin_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a plugin file without fully loading the plugin.
        
        Args:
            file_path: Path to the plugin file
            
        Returns:
            Dictionary of metadata or None if no valid plugin found
        """
        try:
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Use a basic regex approach to find the plugin class and metadata
            # This is not foolproof but should work for simple cases
            plugin_class_match = re.search(r'class\s+(\w+)\s*\(\s*PluginBase\s*\)', content)
            if not plugin_class_match:
                return None
                
            class_name = plugin_class_match.group(1)
            
            # Extract version from METADATA declaration
            metadata_match = re.search(r'METADATA\s*=\s*{([^}]+)}', content)
            metadata = {}
            
            if metadata_match:
                metadata_str = metadata_match.group(1)
                # Extract key-value pairs using regex
                pairs = re.findall(r'[\'"]([\w]+)[\'"]\s*:\s*[\'"]([^\'"]*)[\'"](,|$)', metadata_str)
                for key, value, _ in pairs:
                    metadata[key] = value
            
            # If no name in metadata, use the class name
            if 'name' not in metadata:
                # Convert CamelCase to title case with spaces
                name = re.sub(r'(?<!^)(?=[A-Z])', ' ', class_name).title()
                # Remove 'Plugin' suffix if present
                name = name.replace(' Plugin', '')
                metadata['name'] = name
            
            # Set the file path
            metadata['file_path'] = file_path
            
            return metadata
        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path}: {str(e)}")
            return None
    
    def get_plugin(self, plugin_name: str, instantiate: bool = True, plugin_args: Optional[Dict[str, Any]] = None) -> Optional[PluginBase]:
        """
        Get a plugin instance by name, optionally instantiating it if not already loaded.
        
        Args:
            plugin_name: Name of the plugin to get
            instantiate: Whether to instantiate the plugin if not already loaded
            plugin_args: Arguments to pass to the plugin constructor if instantiating
            
        Returns:
            Plugin instance or None if not found/instantiation failed
        """
        # Return existing instance if available
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
        
        # Instantiate if requested and class is available
        if instantiate and plugin_name in self._plugin_classes:
            args = plugin_args or {}
            if self._instantiate_plugin(plugin_name, args):
                return self.plugins[plugin_name]
        
        return None
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dictionary of metadata or None if plugin not found
        """
        return self.plugin_metadata.get(plugin_name)
    
    def get_available_signals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available signals across all plugins.
        
        Returns:
            Dictionary mapping signal names to their metadata
        """
        return self.signal_registry.get_all_signals()
    
    def reload_plugin(self, plugin_name: str, plugin_args: Optional[Dict[str, Any]] = None) -> bool:
        """
        Reload a plugin by name.
        
        This unloads the plugin and its signals, then reloads it from its file.
        
        Args:
            plugin_name: Name of the plugin to reload
            plugin_args: Arguments to pass to the plugin constructor
            
        Returns:
            True if reload was successful, False otherwise
        """
        # Check if plugin is known
        if plugin_name not in self.plugin_metadata:
            logger.error(f"Cannot reload unknown plugin: {plugin_name}")
            return False
        
        # Get the file path from metadata
        file_path = self.plugin_metadata[plugin_name].get('file_path')
        if not file_path or not os.path.isfile(file_path):
            logger.error(f"Plugin file not found for {plugin_name}")
            return False
        
        # Unload the plugin
        self.unload_plugin(plugin_name)
        
        # Remove file from loaded files so it can be loaded again
        self._loaded_files.discard(file_path)
        
        # Reload the plugin
        module_name = f"plugin_{plugin_name}_{id(file_path)}"
        reloaded_name = self.load_plugin_from_file(module_name, file_path, plugin_args)
        
        return reloaded_name == plugin_name
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin by name.
        
        This removes the plugin and all its signals from the registry.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unload was successful, False otherwise
        """
        # Check if plugin is loaded
        if plugin_name not in self.plugins:
            logger.warning(f"Cannot unload plugin {plugin_name}: not currently loaded")
            return False
        
        try:
            # Remove plugin signals from registry
            plugin_instance = self.plugins[plugin_name]
            for signal_name in plugin_instance.signals.keys():
                self.signal_registry.unregister_signal(signal_name)
            
            # Remove plugin instance
            del self.plugins[plugin_name]
            
            # Metadata and class info are kept for potential reloading
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {str(e)}")
            return False
    
    def get_plugin_versions(self) -> Dict[str, str]:
        """
        Get the versions of all known plugins.
        
        Returns:
            Dictionary mapping plugin names to their versions
        """
        return {name: meta.get('version', 'unknown') for name, meta in self.plugin_metadata.items()}
    
    def check_update_available(self, plugin_name: str, new_version: str) -> bool:
        """
        Check if a plugin update is available.
        
        Args:
            plugin_name: Name of the plugin to check
            new_version: Version string to compare against
            
        Returns:
            True if the new version is greater than the current version
        """
        if plugin_name not in self.plugin_metadata:
            return False
        
        current_version = self.plugin_metadata[plugin_name].get('version', '0.0.0')
        
        try:
            # Parse versions and compare
            return version.parse(new_version) > version.parse(current_version)
        except Exception:
            # If version parsing fails, assume no update is available
            return False
