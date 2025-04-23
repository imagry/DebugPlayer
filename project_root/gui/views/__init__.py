#!/usr/bin/env python3

"""
Views package for the Debug Player.

This package contains various view implementations for displaying different
types of signal data in the Debug Player application.
"""

from typing import Dict, Any
from core.view_manager import ViewManager

# Import view classes
from gui.views.table_view import TableView
from gui.views.text_view import TextView
from gui.views.metrics_view import MetricsView

def register_views(view_manager: ViewManager) -> None:
    """
    Register all view types with the ViewManager.
    
    Args:
        view_manager: The ViewManager instance to register views with
    """
    # Register view classes
    view_manager.register_view_class('table', TableView)
    view_manager.register_view_class('text', TextView)
    view_manager.register_view_class('metrics', MetricsView)
    
    # Register view templates
    _register_view_templates(view_manager)
    
def _register_view_templates(view_manager: ViewManager) -> None:
    """
    Register standard view templates with the ViewManager.
    
    Args:
        view_manager: The ViewManager instance to register templates with
    """
    # Table view templates
    view_manager.register_template('data_table', {
        'type': 'table',
        'config': {
            'title': 'Data Table',
            'signals': []  # Will be populated when used
        }
    })
    
    # Text view templates
    view_manager.register_template('log_viewer', {
        'type': 'text',
        'config': {
            'title': 'Log Viewer',
            'signals': [],  # Will be populated when used
            'auto_scroll': True,
            'show_timestamps': True
        }
    })
    
    # Metrics view templates
    view_manager.register_template('dashboard', {
        'type': 'metrics',
        'config': {
            'title': 'Metrics Dashboard',
            'signals': [],  # Will be populated when used
            'layout_columns': 3
        }
    })

