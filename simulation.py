"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QRect, QRectF, Qt

# Data
from data import Graph, Node, Edge, Condition

# Math
from math import floor
from random import choices

# ------------------------------------------------------------------------------
"""
Auxiliary Functions
"""

MAXIMUM_STRING_LENGTH = 8
def formattedLabel(text: str) -> QLabel:

    if len(text) > MAXIMUM_STRING_LENGTH:
        s = text[:MAXIMUM_STRING_LENGTH] + '…'

    else: s = text

    return QLabel(s)

# ------------------------------------------------------------------------------
"""
Auxiliary Classes
"""

class ColorButton(QPushButton):

    def __init__(self, *args, color='white', **kwargs):

        super().__init__(*args, **kwargs)
        self._color = color
        self.setColor(self._color)


    def getColor(self):
        return self._color


    def setColor(self, color):

        self._color = color

        pal = self.palette()
        pal.setColor(QPalette.Button, QColor(color))

        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.update()


    color = property(getColor, setColor)

# ------------------------------------------------------------------------------
"""
Program Classes
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
        self.pw = w / self._dimension
        self.ph = h / self._dimension

        for y in range(self._dimension):
            for x in range(self._dimension):

                _x = x*self.pw
                _y = y*self.ph

                rect = QRectF(_x, _y, _x + self.pw, _y + self.ph)
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


    def randomize(self, weights):

        c = list(range(len(self.graph.nodes)))

        self.initial = [
            choices(c, weights, k=self._dimension)
            for _ in range(self._dimension)
        ]

        self.redraw()
        self.parent().update()


    def updateCell(self, point, ind: int):

        p = self.mapFromParent(point)
        x, y = p.x(), p.y()

        if x >= 0 and x <= self.width() and y >= 0 and y <= self.height():
            i, j = floor(x / self.pw), floor(y / self.ph)

            self.initial[i][j] = ind

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

    def __init__(self, names_colors, _parent):

        super(type(self), self).__init__()

        self.names_colors = names_colors
        self.sliders = []
        self.buttons = []

        self.old_check = None
        self._parent = _parent

        # --------------------------------------

        self.initWidgets()


    def initWidgets(self):

        # main_layout = QVBoxLayout()
        main_layout = QGridLayout()
        main_layout.setVerticalSpacing(1)

        s = f"{100 / len(self.names_colors):.1f}%"

        for i, name_color in enumerate(self.names_colors):

            name, color = name_color

            lab = QLabel(s)

            sl = QSlider(Qt.Horizontal)
            sl.setValue(100)
            sl.valueChanged.connect(self.updateSliders)

            row = i*2
            main_layout.addWidget(formattedLabel(name), row, 0)

            btn = ColorButton(color=color)
            btn.setCheckable(True)
            btn.clicked.connect(self.updateButtons(len(self.buttons)))

            self.buttons.append(btn)

            main_layout.addWidget(btn, row, 1)
            main_layout.addWidget(sl, row+1, 0)
            main_layout.addWidget(lab, row+1, 1)

            self.sliders.append((sl, lab))

        self.setLayout(main_layout)


    def updateSliders(self, *args):

        total = sum(sl.value() for sl, _ in self.sliders)

        if total > 0:
            for sl, lab in self.sliders:
                lab.setText(f"{sl.value() / total * 100:.1f}%")

        else:
            for _, lab in self.sliders:
                lab.setText("0.0%")

        self._parent.randomize()


    def updateButtons(self, ind):

        def inner():

            if self.old_check is not None:

                self.buttons[self.old_check].setIcon(QIcon())

                if self.old_check is not ind:
                    self.buttons[self.old_check].setChecked(False)

                else: self.old_check = None


            if self.buttons[ind].isChecked():

                self.old_check = ind
                self.buttons[self.old_check]\
                    .setIcon(QIcon.fromTheme("media-record"))

        return inner


    def getWeights(self):

        total = sum(sl.value() for sl, _ in self.sliders)
        return [sl.value() / total for sl, _ in self.sliders]

# ------------------------------------------------------------------------------

class SimulationWindow(QWidget):

    def __init__(self, graph: Graph):

        super(type(self), self).__init__()
        self.graph = graph

        self.button = 0

        self.setMouseTracking(True)

        self.initWidgets()

    # --------------------------------------

    def initWidgets(self):

        main_layout = QHBoxLayout()

        lay = QVBoxLayout()
        wid = QWidget()

        wid.setMinimumWidth(250)
        wid.setMaximumWidth(250)

        # Buttons, sliders, etc...

        self.dist = SimulationDistribution(
            [(node.name, node.color) for node in self.graph.nodes],
            self
        )
        lay.addWidget(self.dist)

        btn = QPushButton("Generate")
        btn.clicked.connect(self.randomize)
        lay.addWidget(btn)

        wid.setLayout(lay)
        main_layout.addWidget(wid)

        self.canvas = SimulationFrame(self.graph)

        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

        self.randomize()

    # ------------------------------------

    def randomize(self):
        self.canvas.randomize(self.dist.getWeights())

    # ------------------------------------

    def mousePressEvent(self, e):
        self.button = e.button()
        self.mouseMoveEvent(e)


    def mouseMoveEvent(self, e):

        if self.button and self.dist.old_check is not None:
            self.canvas.updateCell(e.pos(), self.dist.old_check)


    def mouseReleaseEvent(self, e):
        self.button = 0