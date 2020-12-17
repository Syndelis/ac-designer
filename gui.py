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
from vector import vec

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

    # ------------------------------------

    def __getattr__(self, attr):
        # For graph operations, deal directly with the graph

        return self.graph.__getattr__(attr)

# ------------------------------------------------------------------------------

class EventHandler(abc.ABC):

    @abc.abstractstaticmethod
    def getName(): pass

    @abc.abstractstaticmethod
    def getIcon(): pass

    @abc.abstractstaticmethod
    def mousePressEvent(ctx, e): pass

    @abc.abstractstaticmethod
    def mouseReleaseEvent(ctx, e): pass

    @abc.abstractstaticmethod
    def mouseMoveEvent(ctx, e): pass