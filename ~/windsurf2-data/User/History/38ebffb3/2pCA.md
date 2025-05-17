---
trigger: model_decision
description: Apply when developing new visualization widgets using PySide6 and Matplotlib
---

# Cursor Context Rules: PySide6 Widget Development

## Goal
Guide the development of modular, efficient, and maintainable PySide6 widgets for the Autonomous Driving Debug Data Player, adhering to the `BaseDebugWidget` interface and best practices for integrating with Matplotlib.

## `BaseDebugWidget` Adherence
- All custom data display widgets **must** inherit from `BaseDebugWidget`.
- **Key methods to implement:**
    - `get_widget_name() -> str`: Return a user-friendly name for menu display.
    - `create_ui() -> QWidget`:
        - This method must return a `PySide6.QtWidgets.QWidget` instance (or a subclass like `QFrame`).
        - This `QWidget` is the root UI element for the widget.
        - If using Matplotlib, this is where the Matplotlib FigureCanvas will be created and embedded into a Qt layout within the returned `QWidget`.
    - `update_display(self, current_timestamp: float, current_data_snapshot: dict)`:
        - This method is called by the framework when the playback time changes.
        - It receives the current synchronized data snapshot.
        - Logic here should update the Matplotlib plot (clear old artists, draw new ones) or other Qt elements within the widget's UI.
        - **Avoid complex data fetching here if possible; rely on the snapshot. If more data is needed (e.g., a window for plotting), it should have been designed into the snapshot or the widget should have a way to query `DataManager` efficiently.**

## Matplotlib Integration with PySide6
- **Standard Pattern:**
    1. Import `FigureCanvasQTAgg` from `matplotlib.backends.backend_qt5agg` (or equivalent for Qt6 if backend name changes, often it's `backend_qtagg`). *AI should verify correct backend for PySide6.*
    2. Import `Figure` from `matplotlib.figure`.
    3. In `create_ui()`:
        ```python
        # Conceptual snippet for AI guidance
        # from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        # from matplotlib.figure import Figure

        # class MyCustomWidget(BaseDebugWidget):
        #     def create_ui(self):
        #         container_widget = QWidget() # The widget to be returned
        #         layout = QVBoxLayout(container_widget)
        #
        #         self.figure = Figure(figsize=(5, 3), dpi=100) # Store figure for later updates
        #         self.canvas = FigureCanvasQTAgg(self.figure)
        #         layout.addWidget(self.canvas)
        #
        #         # Example: Add an axes
        #         self.ax = self.figure.add_subplot(111)
        #
        #         container_widget.setLayout(layout)
        #         return container_widget
        #
        #     def update_display(self, current_timestamp, current_data_snapshot):
        #         # Example: Access data and plot on self.ax
        #         # self.ax.clear()
        #         # self.ax.plot(...)
        #         # self.canvas.draw()
        #         pass
        ```
- **Updating Plots:** In `update_display()`, clear previous artists (e.g., `self.ax.clear()` or remove specific lines `line.remove()`) and draw new ones. Call `self.canvas.draw()` to refresh the display.
- **Efficiency:** For frequently updated plots, consider updating `Line2D` data (`line.set_data()`) instead of clearing and replotting for better performance.

## Widget Communication
- Widgets should primarily be driven by data passed to `update_display()`.
- If a widget needs to communicate back to the system (rare for display widgets), it should do so via well-defined Qt signals.
- Widgets have access to `DataManager` and `PlaybackController` instances if complex queries or interactions are absolutely necessary, but this should be minimized to keep widgets focused on display.

## Points to Consider for AI
- When asked to create a new widget, always start with the `BaseDebugWidget` template.
- Emphasize embedding Matplotlib correctly within a `QWidget`.
- Ensure `update_display` logic is efficient for smooth playback.
- Promote clear separation between UI creation (`create_ui`) and data update logic (`update_display`).