from PySide6.QtCore import (
    QEasingCurve, QLineF, QParallelAnimationGroup, QPointF,
    QPropertyAnimation, QRectF, Qt
)
import math
import random
from datetime import datetime, timedelta

from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication, QComboBox, QGraphicsItem, QGraphicsObject,
    QGraphicsScene, QGraphicsView, QStyleOptionGraphicsItem,
    QVBoxLayout, QWidget, QSlider, QLabel
)
import pandas as pd
import networkx as nx

class FSM:
    """Finite State Machine Data Class"""

    def __init__(self, fsm_file_path = None):
        self.states = set() # Set of unique states
        self.transitions = {} # Dictionary of transitions
        self.dataframe = None # DataFrame to store the FSM data
        self.time_stamps= None
        self.path_time_stamps= None
        if fsm_file_path:
            self.load_data_from_file(fsm_file_path)
        else:
            self.load_mock_data(k=8, m=3, n=20, self_loops=False)

    def extract_signals_and_signals_data(self):
        """
        Input: DataFrame with signals and their data. Columns are arranged such
        that each signal has prefix 'sig_' followed by the signal_name and each signal 
        data has the prefix 'data_' + signal_name + '_' + data_value_name. 
        For example: sig_RWB_1, data_RWB_1_reached_waiting_box, data_RWB_1_hit_point_x_ego_frame.
        
        Output: Dictionary of signals and their data such that each signal has a dictionary of 
        its data and we can later easily retrieve for each signal its data.
        """
        signals_data = {}
        for column in self.dataframe.columns:
            if column.startswith("sig_"):
                signal_name = column[4:] # remove the prefix 'sig_'
                if signal_name not in signals_data: # add the signal if it is not already in the dictionary
                    signals_data[signal_name] = {"signal": self.dataframe[column].tolist(), "data": {}}
                else:
                    signals_data[signal_name]["signal"] = self.dataframe[column].tolist()
            elif column.startswith("data_"):
                signal_name = column[5:].split('_')[0]                
                data_value_name = column[len("data_" + signal_name + "_"):]
                if signal_name not in signals_data:
                    signals_data[signal_name] = {"signal": [], "data": {}}
                signals_data[signal_name]["data"][data_value_name] = self.dataframe[column].tolist()
        
        self.signals_data = signals_data
        self.signals_list = list(signals_data.keys())
        
        return 
    
    
    def load_data_from_file(self, file_path):
        """Load FSM data from a CSV file."""
        # Header: time_stamp,li_state,path_ts,map_obj_ts,
        self.dataframe = pd.read_csv(file_path)
        first_signal_col_ind = 4
        signals_inds = range(first_signal_col_ind, len(self.dataframe.columns))
        # change column name from "li_state" to "Current State"
        # df_signals_and_data = self.dataframe.drop(columns=["fsm_execution_ts_sec", "current_state", "path_ts_sec", "map_obj_ts_sec"])
        self.dataframe.rename(columns={"current_state": "Current State"}, inplace=True)
        self.states.update(self.dataframe["Current State"].unique())
        self.dataframe.rename(columns={"fsm_execution_ts_sec": "time_stamp"}, inplace=True)
        self.time_stamps=self.dataframe["time_stamp"]
        self.path_time_stamps=self.dataframe["path_ts_sec"]
        
        # Extract signals and their data
        self.extract_signals_and_signals_data()
        
        for ind, row in self.dataframe.iterrows():
            if ind == len(self.dataframe) - 1:
                break
            next_state = self.dataframe.loc[ind + 1, "Current State"]
            transition = (row["Current State"], next_state)
            # signals = df_signals.loc[ind]
            # find which signals have numeric values (not '-')
            signals = {signal: self.signals_data[signal]["signal"][ind] for signal in self.signals_list}            
            # active_signals = {signal: value for signal, value in signals.items() if isinstance(value, (int, float)) and value != '-'}
            active_signals_values = {signal: self.signals_data[signal]["signal"][ind] for signal in self.signals_list if self.signals_data[signal]["signal"][ind] != '-'}
            self.transitions[transition] = active_signals_values
        return
            
            
            
    def load_mock_data(self, k=4, m=3, n=10, self_loops=False):
        """Generate mock FSM data with continuous transitions.

        Args:
            k (int): Number of unique states.
            m (int): Number of unique signals.
            n (int): Number of rows (transitions).
            self_loops (bool): Allow or disallow self-loops.
        """
        # Generate states and signals
        states = [f"S{i+1}" for i in range(k)]
        signals = [f"Signal{j+1}" for j in range(m)]
        data = []
        start_time = datetime.now()

        # Initialize the first state randomly
        Previous_state = random.choice(states)

        for i in range(n):
            # Choose a next state
            current_state = random.choice(states)
            # Ensure no self-loops if they are not allowed
            if not self_loops:
                while current_state == Previous_state:
                    current_state = random.choice(states)

            # Randomly select 'm' signals for this transition
            selected_signals = {f"signal{j+1}": random.choice(signals) for j in range(m)}

            # Record the transition with timestamp, state, and signals
            timestamp = start_time + timedelta(seconds=i * 10)
            data.append([timestamp, current_state, *selected_signals.values()])

            # Update transitions dictionary for each transition
            self.transitions[(Previous_state, current_state)] = selected_signals
            
            # Move to the next state
            Previous_state = current_state

        # Track all unique states
        self.states.update(states)

        # Define column names dynamically for the DataFrame
        column_names = ["Timestamp", "Current State"] + [f"Signal{j+1}" for j in range(m)]

        # Create DataFrame from the generated data
        self.dataframe = pd.DataFrame(data, columns=column_names)

        print(self.dataframe)
        
    def get_states(self):
        return list(self.states)

    def get_transitions(self):
        return list(self.transitions.keys())


class Node(QGraphicsObject):
    """A QGraphicsItem representing a node in the graph"""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.edges = []
        self.default_color = QColor("#5AD469")
        self.highlight_color = QColor("#FFD700")
        self.color = self.default_color
        self.radius = 40
        self.rect = QRectF(-self.radius * 2, -self.radius, self.radius * 4, self.radius * 2)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.color.darker(), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(QPen(QColor("black")))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.name)

    def add_edge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.adjust()
        return super().itemChange(change, value)

    def set_highlight(self, highlight: bool):
        self.color = self.highlight_color if highlight else self.default_color
        self.update()


class Edge(QGraphicsItem):
    """A QGraphicsItem representing an edge in the graph"""

    def __init__(self, source: Node, dest: Node, signals: dict, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.source = source
        self.dest = dest
        self.signals = signals

        # Edge properties
        self.line_width = 2
        self.default_color = QColor("#2BB53C")  # Default color for the edge
        self.highlight_color = QColor("red")    # Color to use when highlighted
        self.color = self.default_color         # Initial color
        
        # New attribute for glow effect
        self.glow = False
        
        
        # Arrow size and line for edge
        self.arrow_size = 10
        self.line = QLineF()
        self.setZValue(-1)
        self.adjust()
                  
        self.source.add_edge(self)
        self.dest.add_edge(self)


    def boundingRect(self) -> QRectF:
        extra = self.line_width + self.arrow_size
        return QRectF(self.line.p1(), self.line.p2()).normalized().adjusted(-extra, -extra, extra, extra)

    def adjust(self):
        self.prepareGeometryChange()
        self.line = QLineF(
            self.source.pos(),
            self.dest.pos(),
        )

    def _draw_arrow(self, painter: QPainter):
        painter.setBrush(QBrush(self.color))
        line = self.line
        angle = math.atan2(-line.dy(), line.dx())

        arrow_p1 = line.p2() - QPointF(
            math.sin(angle + math.pi / 3) * self.arrow_size,
            math.cos(angle + math.pi / 3) * self.arrow_size,
        )
        arrow_p2 = line.p2() - QPointF(
            math.sin(angle - math.pi / 3) * self.arrow_size,
            math.cos(angle - math.pi / 3) * self.arrow_size,
        )
        arrow_head = QPolygonF([line.p2(), arrow_p1, arrow_p2])
        painter.drawPolygon(arrow_head)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Draw the edge with optional glow effect when highlighted."""
        if self.source and self.dest:
            # Set up the painter for antialiasing
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)
            
            # Draw the glow effect if the edge is highlighted
            if self.glow:
                alpha = 255*self.glow
                glow_pen = QPen(QColor(255, 215, 0, alpha))  # A semi-transparent yellow glow
                glow_pen.setWidth(self.line_width + 10)  # Make the glow thicker than the edge
                painter.setPen(glow_pen)
                painter.drawLine(self.line)

            # Draw the main line with the current color
            main_pen = QPen(self.color, self.line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(main_pen)
            painter.drawLine(self.line)

            # Draw the arrow with the main color
            painter.setBrush(QBrush(self.color))
            self._draw_arrow(painter)

            # Draw the signals or other information if needed
            mid_point = (self.line.p1() + self.line.p2()) / 2
            painter.setPen(QPen(QColor("black")))
            signals_text = ", ".join([v for v in self.signals.values()])
            signals_text = None
            # TODO: plot only relevant signals, the ones that changed on this tranisiton compared to the previous meaningful transition

            painter.drawText(mid_point, signals_text)
            

    def set_highlight(self, highlight: bool, glow_level=0.5):
        """Toggle the highlight effect by setting the glow flag and updating the item."""
        self.glow = highlight * glow_level  # Set a flag to indicate whether the glow should be drawn
        self.update()  # Force a repaint to reflect the glow effect


