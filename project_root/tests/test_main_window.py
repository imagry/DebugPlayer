import os
import sys
from PySide6.QtWidgets import QDockWidget


base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from gui.main_window import create_main_window
from core.plot_manager import PlotManager

def test_main_window_setup(qtbot):
    plot_manager = PlotManager()
    main_window, plot_manager = create_main_window(plot_manager)
    
    # Check if the main window and plot manager are created
    assert main_window is not None
    assert plot_manager is not None
    
    # Verify that plot docks are created
    dock_widgets = main_window.findChildren(QDockWidget)
    assert len(dock_widgets) >= 2

