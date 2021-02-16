"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QRect, QRectF, Qt

# Data
from data import Graph, Node, Edge, Condition

# ------------------------------------------------------------------------------
"""
Program Class
"""

class SimulationFrame(QLabel):

    def __init__(self, graph, width=600, height=600, dimension=30, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.graph = graph

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
        
        painter.setPen(Qt.darkGray)
        pw = w / self._dimension
        ph = h / self._dimension

        for y in range(self._dimension):
            for x in range(self._dimension):

                _x = x*pw
                _y = y*ph

                rect = QRectF(_x, _y, _x + pw, _y + ph)
                el = self.initial[x][y]

                painter.setBrush(QColor(self.graph.nodes[el].color))
                painter.drawRect(rect)

        painter.end()


    def resizeEvent(self, e):

        width = e.size().width()
        height = e.size().height()
        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.redraw()
        self.parent().update()

    
    
    def getDimension(self):
        return self._dimension

    def setDimention(self, dimension):
        self._dimension = dimension
        # TODO: Redraw here

    dimension = property(getDimension, setDimention)

# ------------------------------------------------------------------------------

class SimulationDistribution(QWidget):

    def __init__(self, names):
        
        super(type(self), self).__init__()
        self.names = names
        self.sliders = []

        # --------------------------------------

        self.initWidgets()


    def initWidgets(self):

        main_layout = QVBoxLayout()

        for name in self.names:
            
            vlay = QVBoxLayout()
            vwid = QWidget()

            vlay.addWidget(QLabel(name))

            lay = QHBoxLayout()
            wid = QWidget()

            sl = QSlider(Qt.Horizontal)
            sl.valueChanged.connect(self.updateSliders)
            lay.addWidget(sl)

            lab = QLabel("0")
            lay.addWidget(lab)

            self.sliders.append((sl, lab))

            wid.setLayout(lay)
            vlay.addWidget(wid)

            vwid.setLayout(vlay)
            main_layout.addWidget(vwid)

        self.setLayout(main_layout)


    def updateSliders(self, *args):

        total = sum(sl.value() for sl, _ in self.sliders)

        if total > 0:
            for sl, lab in self.sliders:
                lab.setText(f"{sl.value() / total * 100:.1f}%")

        else:
            for _, lab in self.sliders:
                lab.setText("0.0%")

        self.parent().update()



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

        wid.setMinimumWidth(250)
        wid.setMaximumWidth(250)

        # Buttons, sliders, etc...
        lay.addWidget(SimulationDistribution(
            node.name for node in self.graph.nodes
        ))

        wid.setLayout(lay)
        main_layout.addWidget(wid)

        self.canvas = SimulationFrame(self.graph)

        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

        self.canvas.redraw()
        self.update()