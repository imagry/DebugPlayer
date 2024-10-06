from PySide6.QtWidgets import QMenuBar, QFileDialog, QMessageBox
from PySide6.QtGui import QAction  # Import QAction from PySide6.QtGui

def setup_menu_bar(win):
    """Sets up the menu bar and adds it to the given main window."""
    menubar = QMenuBar(win)
    win.setMenuBar(menubar)

    # File Menu
    file_menu = menubar.addMenu("File")
    
    open_action = QAction("Open", win)
    open_action.triggered.connect(open_file)
    file_menu.addAction(open_action)

    save_action = QAction("Save", win)
    save_action.triggered.connect(save_file)
    file_menu.addAction(save_action)

    exit_action = QAction("Exit", win)
    exit_action.triggered.connect(win.close)
    file_menu.addAction(exit_action)

    # View Menu
    view_menu = menubar.addMenu("View")
    toggle_controls_action = QAction("Toggle Control Panel", win)
    toggle_controls_action.triggered.connect(win.toggle_control_panel)
    view_menu.addAction(toggle_controls_action)

    # Restore default layout
    restore_action = QAction("Restore Default Layout", win)
    restore_action.triggered.connect(win.restore_layout)  # Connect to method
    view_menu.addAction(restore_action)
    
    # Help Menu
    help_menu = menubar.addMenu("Help")
    about_action = QAction("About", win)
    about_action.triggered.connect(lambda: show_about(win))
    help_menu.addAction(about_action)
    
def open_file():
    file_name, _ = QFileDialog.getOpenFileName(None, "Open File", "", "All Files (*)")
    if file_name:
        # Add your file loading logic here
        # TODO: Add file loading logic
        pass
    
def save_file():
    file_name, _ = QFileDialog.getSaveFileName(None, "Save File", "", "All Files (*)")
    if file_name:
        # TODO: Add your save logic here        
        pass

def show_about(parent):
    QMessageBox.about(parent, "About", "Motion Planning Playback Debug Tool v1.0")
    # TODO: Add your about logic here
    