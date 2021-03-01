"""
Imports
"""

# Gui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QLineF, QRectF
from PyQt5.QtGui import *

# Misc
from math import sin, cos, atan2, pi, hypot, acos
from numpy import matrix, linalg
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

    metric_line_size = 5
    text_offset = 5

    def __init__(self, main, *args, graph: Graph=None,
                 width=800, height=600, **kwargs):

        super().__init__(*args, **kwargs)

        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        canvas = QPixmap(width, height)
        self.setPixmap(canvas)
        self.color = QColor('white')
        self.setColor(self.color)

        self.main = main

        if graph is None:   self.graph = Graph()
        else:               self.graph = graph

        self._selection = None

        self.cam = vec(0, 0)

        # ------------------------------------
        # Right-Click menu stuff

        self.edit = QAction(QIcon.fromTheme('document-open-recent'), 'Edit', self)
        self.edit.triggered.connect(self.editObject)

        self.remove = QAction(QIcon.fromTheme('edit-delete'), 'Remove', self)
        self.remove.triggered.connect(self.removeObject)

        self.menu = QMenu(self)
        self.menu.addAction(self.edit)
        self.menu.addAction(self.remove)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.menu_selection = None

    # ------------------------------------

    def contextMenu(self, e):

        x, y = e.x(), e.y()

        self.menu_selection = self.getAt(x, y)

        Node.unhighlight()
        Edge.unhighlight()
        if self.menu_selection is not None:

            self.edit.setEnabled(True)
            self.remove.setEnabled(True)
            self.menu_selection.highlit = True

        else:
            self.edit.setEnabled(False)
            self.remove.setEnabled(False)

        self.redraw()
        self.parent().update()
        self.menu.exec_(self.mapToGlobal(e))


    def editObject(self):

        self.main.launchEditor(self.menu_selection)


    def removeObject(self):

        self.graph.remove(self.menu_selection)
        self.redraw()
        self.parent().update()

    # ------------------------------------

    def setColor(self, color):
        self.pixmap().fill(color)
        self.color = color

    # ------------------------------------

    def addNode(self, x, y):
        self.graph.addNode(x=x + self.cam.x, y=y + self.cam.y)


    def drawNode(self, painter, node: Node):

        pen = QPen()
        pen.setColor(QColor('blue') if node.highlit else QColor('black'))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.setBrush(QColor(node.color))

        painter.drawEllipse(*(node.pos - self.cam), node.radius, node.radius)
        painter.setBrush(Qt.NoBrush)

        painter.drawText(*(node.pos - self.cam), node.name)

    # ------------------------------------

    def drawEdge(self, painter: QPainter, edge: Edge):

        pen = QPen()
        pen.setColor(QColor('blue') if edge.highlit else QColor('black'))
        pen.setWidth(2)
        painter.setPen(pen)

        # ------------------------------------

        nodes = edge.nodes

        x0, y0 = (nodes[0].pos).astype(int)
        x1, y1 = (nodes[1].pos).astype(int)

        r0 = nodes[0].radius//2
        r1 = nodes[1].radius//2

        angle = atan2(y0 - y1, x0 - x1)

        # ------------------------------------
        # Calculating the name holder

        painter.setBrush(Qt.white)

        # Finding the point in the middle
        edge.calculated = (nodes[0].pos + nodes[1].pos + Node.radius) / 2

        dir = vec(cos(angle), sin(angle)) # Direction vector node0 -> node1

        # Perpendicular vector to edge
        edge.perp = vec(dir @ matrix(((0, 1), (-1, 0))))[0][0]

        x, y = edge.final = edge.calculated + edge.perp * edge.offset

        # ------------------------------------
        # Calculate the lines

        d = edge.final + vec(Node.radius, Node.radius/2)

        angle0 = atan2(y0 - y, x0 - x)
        angle1 = atan2(y - y1, x - x1)

        x0 -= round(cos(angle0) * r0)
        y0 -= round(sin(angle0) * r0)
        x1 += round(cos(angle1) * r1)
        y1 += round(sin(angle1) * r1)

        # ------------------------------------
        # Calculate arrow point

        p = vec(x1, y1) + r1

        dir = vec(cos(angle1), sin(angle1))

        v = p + dir * Edge.arrow_height
        u = vec(dir @ matrix(((0, 1), (-1, 0))))[0][0]

        left = v + u * Edge.arrow_width
        right = v - u * Edge.arrow_width

        # ------------------------------------
        # Now, draw everything

        mx, my = self.cam
        # Lines
        painter.drawLine(x0 + r0 - mx, y0 + r0 - my, x - mx, y - my)
        painter.drawLine(x1 + r1 - mx, y1 + r1 - my, x - mx, y - my)

        # Arrow Point
        painter.setBrush(QColor('blue') if edge.highlit else QColor('black'))
        painter.drawPolygon(
            QPoint(*(p - self.cam)),
            QPoint(*(left - self.cam)),
            QPoint(*(right - self.cam))
        )

        # Name holder & Name
        rect = painter.fontMetrics().boundingRect(edge.name)

        w = rect.width() * Edge.size_multiplier
        h = rect.height() * Edge.size_multiplier
        rect = QRectF(x - w/2 - mx, y - h/2 - my, w, h)

        painter.setBrush(QBrush(QColor('white')))
        painter.drawRoundedRect(rect, Edge.box_angle, Edge.box_angle)
        painter.setBrush(Qt.NoBrush)
        painter.drawText(rect, Qt.AlignCenter, edge.name)


    # ------------------------------------

    def redraw(self):

        self.pixmap().fill(self.color)
        painter = QPainter(self.pixmap())
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.setPen(Qt.black)

        old = painter.font()
        new = QFont(old)
        new.setPointSize(6)
        painter.setFont(new)

        it = [
            x - self.cam.x
            for x in range(self.cam.x, self.cam.x + self.width())
            if x % 10 == 0
        ]

        for x in it:

            long = (x + self.cam.x) % 100 == 0
            if long:
                painter.drawText(
                    x, self.metric_line_size * 2 + self.text_offset,
                    f"{x + self.cam.x}"
                )

            painter.drawLine(x, 0, x, self.metric_line_size * (long+1))

        it = [
            y - self.cam.y
            for y in range(self.cam.y, self.cam.y + self.height())
            if y % 10 == 0
        ]

        for y in it:

            long = (y + self.cam.y) % 100 == 0
            if long:
                painter.drawText(
                    self.metric_line_size * 2,
                    y + self.text_offset, f"{y + self.cam.y}"
                )

            painter.drawLine(0, y, self.metric_line_size * (long+1), y)

        # ------------------------------------

        painter.setFont(old)

        for node in self.graph.nodes:
            self.drawNode(painter, node)

        for edge in self.graph.edges:
            self.drawEdge(painter, edge)

        painter.end()


    def getAt(self, pos, y=None):

        if y is not None: pos = vec(pos, y)
        if type(pos) is not Vector:
            raise TypeError(f"Expected int or Vector, not {type(pos)}")

        pos += self.cam

        for node in self.graph.nodes:

            if  (pos > node.pos - node.radius).all() and\
                (pos < node.pos + node.radius).all():

                return node


        v = vec(2, 1) * Node.radius
        for edge in self.graph.edges:

            if (pos > edge.final - v).all() and\
               (pos < edge.final + v).all():

               return edge

        return None

    # ------------------------------------

    def resizeEvent(self, e):

        width = e.size().width()
        height = e.size().height()
        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.redraw()
        self.parent().update()

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