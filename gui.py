"""
Imports
"""

# Gui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
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

    # TODO
    # Draggable edge
    #def addEdge

    # ------------------------------------

    def redraw(self):

        self.pixmap().fill(self.color)
        painter = QPainter(self.pixmap())

        for node in self.graph.nodes:
            self.drawNode(painter, node)

        # TODO: Add the drawEdge method
        # for edge in graph.edges:
        #     self.drawEdge(painter, edge)

        painter.end()


    def getAt(self, pos, y=None):

        if y is not None: pos = vec(pos, y)
        if type(pos) is not Vector:
            raise TypeError(f"Expected int or Vector, not {type(pos)}")

        for node in self.graph.nodes:

            if  (pos > node.pos - node.radius).all() and\
                (pos < node.pos + node.radius).all():

                return node

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