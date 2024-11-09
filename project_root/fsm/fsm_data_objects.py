from fsm.fsm_data_interface import DataInterface
from PySide6.QtCore import QPointF, QRectF, Qt, QLineF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem, QStyleOptionGraphicsItem
import math

class FSM:
    """Finite State Machine Model using an external data interface for data loading."""

    def __init__(self, data_interface: DataInterface):
        self.data_interface = data_interface
        self.states = self.data_interface.get_states()
        self.transitions = self.data_interface.get_transitions()

        # Debug: Print structure of transitions after assignment
        # print("FSM Transitions (initial):", self.transitions)
        
        self.dataframe = self.data_interface.get_dataframe()

    def get_states(self):
        """Return list of states in the FSM."""
        return self.states

    def get_transitions(self):
        """Return list of transitions between states."""
        return self.transitions

    def get_dataframe(self):
        """Return the FSM data as a DataFrame for analysis and updates."""
        return self.dataframe

class Node(QGraphicsObject):
    """Represents a state in the FSM graph, displayed as a circular node."""

    def __init__(self, name: str, parent=None):
        """Initialize the Node with a name, radius, and default color."""
        super().__init__(parent)
        self.name = name
        self.edges = []

        self.radius = 30
        self.color = QColor("#5AD469")  # Default node color
        self.highlight_color = QColor("#FFD700")  # Color when highlighted
        self.rect = QRectF(0, 0, self.radius * 2, self.radius * 2)
        self.is_highlighted = False

        # Set node flags for interactivity
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self) -> QRectF:
        """Returns the bounding rectangle for the node."""
        return self.rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Draw the node with the appropriate color and label."""
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        # Set pen and brush for drawing the circle
        pen = QPen(self.highlight_color if self.is_highlighted else self.color, 1)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.highlight_color if self.is_highlighted else self.color))

        # Draw the node as a circle
        painter.drawEllipse(self.boundingRect())

        # Draw the node label
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(QPen(QColor("white")))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.name)


    def add_edge(self, edge):
        """Add an edge to the list of edges connected to this node."""            
        self.edges.append(edge)
        
            
    def highlight(self, highlight: bool):
        """Toggle the highlight state of the node."""
        self.is_highlighted = highlight
        self.update()


class Edge(QGraphicsItem):
    """Represents a transition in the FSM graph, displayed as an edge with an optional glow when highlighted."""

    def __init__(self, source: Node, dest: Node, signals, parent=None):
        """Initialize the Edge with source and destination nodes, and associated signals."""
        super().__init__(parent)
        self.source = source
        self.dest = dest
        self.signals = signals
        self.line_width = 2
        self.default_color = QColor("#2BB53C")  # Default edge color
        self.highlight_color = QColor("yellow")  # Glow color when highlighted
        self.color = self.default_color
        self.glow = False  # Track whether glow is active for this edge

        # Arrow and line setup
        self.arrow_size = 10
        self.line = QLineF()
        self.setZValue(-1)
        self.adjust()
        
        # self.source.add_edge(self)
        # self.dest.add_edge(self)


    # def adjust(self):
    #     """Update the position of the edge to connect source and destination nodes."""
    #     self.prepareGeometryChange()
    #     self.line = QLineF(
    #         self.source.pos() + self.source.boundingRect().center(),
    #         self.dest.pos() + self.dest.boundingRect().center(),
    #     )
    def adjust(self):
            self.prepareGeometryChange()
            self.line = QLineF(
                self.source.pos(),
                self.dest.pos(),
            )

    def boundingRect(self) -> QRectF:
        extra = self.line_width + self.arrow_size
        return QRectF(self.line.p1(), self.line.p2()).normalized().adjusted(-extra, -extra, extra, extra)

    def set_highlight(self, highlight: bool):
        """Toggle the glow effect on the edge by changing the glow flag and triggering a repaint."""
        self.glow = highlight
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Draw the edge with optional glow effect when highlighted."""
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        # Draw glow effect if the edge is highlighted
        if self.glow:
            glow_pen = QPen(self.highlight_color, self.line_width + 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            glow_pen.setColor(QColor(255, 215, 0, 100))  # Semi-transparent glow
            painter.setPen(glow_pen)
            painter.drawLine(self.line)

        # Draw the main line with the current color
        main_pen = QPen(self.color, self.line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(main_pen)
        painter.drawLine(self.line)

        # Draw the arrowhead
        painter.setBrush(QBrush(self.color))
        self._draw_arrow(painter)

        # Draw signal information (if applicable) at the midpoint
        mid_point = (self.line.p1() + self.line.p2()) / 2
        painter.setPen(QPen(QColor("black")))
        signals_text = ", ".join([str(v) for v in self.signals.values()])
        painter.drawText(mid_point, signals_text)

    def _draw_arrow(self, painter: QPainter):
        """Helper function to draw an arrow from source to destination."""
        angle = math.atan2(-self.line.dy(), self.line.dx())
        arrow_p1 = self.line.p1() + QPointF(math.sin(angle + math.pi / 3) * self.arrow_size,
                                            math.cos(angle + math.pi / 3) * self.arrow_size)
        arrow_p2 = self.line.p1() + QPointF(math.sin(angle - math.pi / 3) * self.arrow_size,
                                            math.cos(angle - math.pi / 3) * self.arrow_size)

        arrow_head = QPolygonF([self.line.p1(), arrow_p1, arrow_p2])
        painter.drawPolygon(arrow_head)
