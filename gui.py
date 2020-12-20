"""
Imports
"""

# Gui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QColor, QFont, QPainter, QPixmap, QPen, QBrush

# Misc
from math import sin, cos, atan2
import abc

# Data
from data import Graph, Node, Edge, find
from vector import vec, Vector

# ------------------------------------------------------------------------------
"""
Base classes
"""

# A basic color widget. It's just a background color, really
class Color(QWidget):

    def __init__(self, color, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

# ------------------------------------------------------------------------------

# The main drawing frame
class Canvas(QLabel):

    def __init__(self, *args, graph: Graph=None, width=400,height=300,**kwargs):

        super().__init__(*args, **kwargs)

        canvas = QPixmap(width, height)
        self.setPixmap(canvas)
        self.color = QColor('white')
        self.setColor(self.color)

        if graph is None:   self.graph = Graph()
        else:               self.graph = graph

        self._selection = None

    # ------------------------------------

    def setColor(self, color):
        self.pixmap().fill(color)
        self.color = color

    # ------------------------------------

    def addNode(self, x, y):
        self.graph.addNode(x=x, y=y)

    
    def drawNode(self, painter, node: Node):

        pen = QPen()
        pen.setColor(QColor('blue') if node.highlit else QColor('black'))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawEllipse(*node.pos, node.radius, node.radius)

    # ------------------------------------

    def drawEdge(self, painter: QPainter, edge: Edge):

        pen = QPen()
        pen.setColor(QColor('black'))
        pen.setWidth(2)
        painter.setPen(pen)

        nodes = edge.nodes

        x0, y0 = nodes[0].pos.astype(int)
        x1, y1 = nodes[1].pos.astype(int)

        r0 = nodes[0].radius//2
        r1 = nodes[1].radius//2

        angle = atan2(y0 - y1, x0 - x1)
        x0 -= round(cos(angle) * r0)
        y0 -= round(sin(angle) * r0)
        x1 += round(cos(angle) * r1)
        y1 += round(sin(angle) * r1)

        painter.drawLine(x0 + r0, y0 + r0, x1 + r1, y1 + r1)

        painter.setBrush(Qt.white)

        edge.calculated = (nodes[0].pos + nodes[1].pos - Node.radius) / 2
        x, y = edge.calculated

        painter.drawRoundedRect(x, y, Node.radius*2, Node.radius, 15, 15)
        
        painter.setBrush(Qt.black)

        p = vec(x1, y1) + r1
        dir = vec(cos(angle), sin(angle))

        v = p + dir * Edge.arrow_height
        left = v + vec(-sin(angle), cos(angle)) * Edge.arrow_width
        right = v + vec(sin(angle), -cos(angle)) * Edge.arrow_width

        painter.drawPolygon(QPoint(*p), QPoint(*left), QPoint(*right))

    # ------------------------------------

    def redraw(self):

        self.pixmap().fill(self.color)
        painter = QPainter(self.pixmap())

        for node in self.graph.nodes:
            self.drawNode(painter, node)

        for edge in self.graph.edges:
            self.drawEdge(painter, edge)

        painter.end()


    def getAt(self, pos, y=None):

        if y is not None: pos = vec(pos, y)
        if type(pos) is not Vector:
            raise TypeError(f"Expected int or Vector, not {type(pos)}")

        for node in self.graph.nodes:

            if  (pos > node.pos - node.radius).all() and\
                (pos < node.pos + node.radius).all():

                return node


        v = vec(2, 1) * Node.radius
        for edge in self.graph.edges:

            if (pos > edge.calculated - v).all() and\
               (pos < edge.calculated + v).all():

               return edge

        return None

    # ------------------------------------

    def unhighlight(self):

        for node in self.graph.nodes:
            node.setHighlight(False)

        for edge in self.graph.edges:
            edge.setHighlight(False)

    # ------------------------------------

    def __getattr__(self, attr):
        # For graph operations, deal directly with the graph

        return self.graph.__getattr__(attr)

# ------------------------------------------------------------------------------

class EventHandler(abc.ABC):

    @abc.abstractclassmethod
    def getName(cls): pass

    @abc.abstractclassmethod
    def getIcon(cls): pass

    @abc.abstractclassmethod
    def mousePressEvent(cls, ctx, e): pass

    @abc.abstractclassmethod
    def mouseReleaseEvent(cls, ctx, e): pass

    @abc.abstractclassmethod
    def mouseMoveEvent(cls, ctx, e): pass