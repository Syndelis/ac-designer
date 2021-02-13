"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *

# Data
from data import Graph, Node, Edge, Condition

# ------------------------------------------------------------------------------
"""
Program Class
"""

class SimulationFrame(QLabel):

    def __init__(self, width=600, height=600, dimension=30, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        # TODO:
        # - NxM rather than NxN
        # - Initial condition based on randomness
        self._dimension = dimension
        self.initial = [
            [0] * self._dimension
            for _ in range(self._dimension)
        ]


    def redraw(self):

        w, h = self.width(), self.height()

        self.pixmap().fill(QColor('white'))
        painter = QPainter(self.pixmap())
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        
        painter.setPen(None)

        for y in range(0, h, self._dimension):
            for x in range(0, w, self._dimension):

                rect = QRect(x, y, x+self._dimension, y+self._dimension)
                el = self.initial[x//self._dimension][y//self._dimension]
                painter.setBrush(self.graph.nodes[el].color)

                painter.drawRect(rect)

        painter.end()
    
    
    def getDimension(self):
        return self._dimension

    def setDimention(self, dimension):
        self._dimension = dimension
        # TODO: Redraw here

    dimension = property(getDimension, setDimention)

# ------------------------------------------------------------------------------

class SimulationWindow(QWidget):
    
    def __init__(self, graph: Graph):
        
        super(type(self), self).__init__()
        self.graph = graph

        self.initWidgets()

    # --------------------------------------

    def initWidgets(self):
        
        main_layout = QHBoxLayout()

        lay = QVBoxLayout()
        wid = QWidget()

        # Buttons, sliders, etc...

        wid.setLayout(lay)
        main_layout.addWidget(wid)

        self.canvas = SimulationFrame()

        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)