import sys
import math
import networkx as nx
import pandas as pd
from PySide6.QtCore import (QEasingCurve, QParallelAnimationGroup, QPointF, QPropertyAnimation, Qt)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsItem, QGraphicsObject,
                               QGraphicsScene, QGraphicsView, QStyleOptionGraphicsItem,
                               QVBoxLayout, QWidget, QLabel, QSlider)

from PySide6.QtCore import QRectF, Qt, QPointF, QLineF


class Node(QGraphicsObject):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self._name = name
        self._edges = []
        self._color = "#5AD469"
        self._radius = 30
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self):
        return self._rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(self._color).darker(), 2))
        painter.setBrush(QBrush(QColor(self._color)))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(QPen(QColor("white")))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self._name)

    def add_edge(self, edge):
        self._edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self._edges:
                edge.adjust()
        return super().itemChange(change, value)

class Edge(QGraphicsItem):
    def __init__(self, source: Node, dest: Node, label: str = "", parent=None):
        super().__init__(parent)
        self._source = source
        self._dest = dest
        self._label = label
        self._color = "#2BB53C"
        self._arrow_size = 10
        self._source.add_edge(self)
        self._dest.add_edge(self)
        self._line = QLineF()
        self.setZValue(-1)
        self.adjust()

    def boundingRect(self):
        return QRectF(self._line.p1(), self._line.p2()).normalized().adjusted(-20, -20, 20, 20)

    def adjust(self):
        self.prepareGeometryChange()
        self._line = QLineF(
            self._source.pos() + self._source.boundingRect().center(),
            self._dest.pos() + self._dest.boundingRect().center()
        )

    def paint(self, painter: QPainter, option, widget=None):
        if self._source and self._dest:
            painter.setPen(QPen(QColor(self._color), 2))
            painter.drawLine(self._line)
            painter.setBrush(QBrush(self._color))

            # Draw arrow head
            angle = math.atan2(-self._line.dy(), self._line.dx())
            arrow_p1 = self._line.p1() + QPointF(
                math.sin(angle + math.pi / 3) * self._arrow_size,
                math.cos(angle + math.pi / 3) * self._arrow_size,
            )
            arrow_p2 = self._line.p1() + QPointF(
                math.sin(angle + math.pi - math.pi / 3) * self._arrow_size,
                math.cos(angle + math.pi - math.pi / 3) * self._arrow_size,
            )
            arrow_head = QPolygonF([self._line.p1(), arrow_p1, arrow_p2])
            painter.drawPolygon(arrow_head)

            # Draw edge label
            painter.setPen(QPen(Qt.black))
            mid_point = (self._line.p1() + self._line.p2()) / 2
            painter.drawText(mid_point, self._label)

class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, parent=None):
        super().__init__()
        self._graph = graph
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self._nodes_map = {}
        self._graph_scale = 200
        self._load_graph()
        self.set_nx_layout("circular")

    def _load_graph(self):
        self.scene().clear()
        self._nodes_map.clear()

        # Add nodes
        for node in self._graph:
            item = Node(node)
            self.scene().addItem(item)
            self._nodes_map[node] = item

        # Add edges
        for a, b in self._graph.edges:
            label = self._graph.edges[a, b].get('label', '')
            source = self._nodes_map[a]
            dest = self._nodes_map[b]
            self.scene().addItem(Edge(source, dest, label=label))

    def set_nx_layout(self, name: str):
        pos = nx.circular_layout(self._graph)
        self.animations = QParallelAnimationGroup()
        for node, (x, y) in pos.items():
            x *= self._graph_scale
            y *= self._graph_scale
            item = self._nodes_map[node]
            animation = QPropertyAnimation(item, b"pos")
            animation.setDuration(1000)
            animation.setEndValue(QPointF(x, y))
            animation.setEasingCurve(QEasingCurve.OutExpo)
            self.animations.addAnimation(animation)
        self.animations.start()

class FSMPlotWidget(QWidget):
    def __init__(self, data, transitions):
        super().__init__()
        self.data = data
        self.graph = nx.DiGraph()
        for state, edges in transitions.items():
            for target, label in edges.items():
                self.graph.add_edge(state, target, label=label)
        
        layout = QVBoxLayout()
        self.view = GraphView(self.graph)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(data) - 1)
        self.slider.valueChanged.connect(self.update_visualization)

        layout.addWidget(self.view)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_visualization(self, timestamp):
        state = self.data.iloc[timestamp]['state']
        print(f"Current State: {state}")

class MainWindow(QWidget):
    def __init__(self, transitions, data):
        super().__init__()
        self.fsm_widget = FSMPlotWidget(data, transitions)
        layout = QVBoxLayout()
        layout.addWidget(self.fsm_widget)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sample Data
    data = pd.DataFrame({'timestamp': range(10), 'state': ['ID', 'Approaching LI', 'Forward LI', 'Approaching Waiting Box', 
                                                           'Waiting on the Waiting Box', 'Left After WB LI', 'Left LI', 
                                                           'Wait on Stop Line', 'Exit Stop Line', 'ID']})
    transitions = {
        'ID': {'Approaching LI': 'Phi(D->LI)=1//SNLI=1'},
        'Approaching LI': {'Turning Right LI': 'Intent=R, ENLI=1', 'Forward LI': 'Intent=F, ENLI=1'},
        'Wait on Stop Line': {'Exit Stop Line': 'ENLI=1'}
    }

    main_window = MainWindow(transitions, data)
    main_window.show()
    sys.exit(app.exec())
