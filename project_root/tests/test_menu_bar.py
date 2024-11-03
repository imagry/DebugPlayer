import os
import sys

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from unittest.mock import MagicMock
from PySide6.QtWidgets import QMenu


from PySide6.QtWidgets import QMainWindow
from gui.main_window import setup_menu_bar

def test_menu_creation(qtbot):
    main_window = QMainWindow()
    plot_manager = MagicMock()  # mock PlotManager for testing
    setup_menu_bar(main_window, plot_manager, plots=[], current_timestamp=0)
    
    # Check that the View menu was created
    menu = main_window.menuBar().findChild(QMenu, "View")
    assert menu is not None
    assert menu.title() == "View"
