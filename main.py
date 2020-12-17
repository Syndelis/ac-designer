"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon

from gui import Canvas, EventHandler

# Data
from vector import vec, Vector
from data import Node, Edge

# ------------------------------------------------------------------------------
"""
Globals
"""

MOUSE_DIFF = 30
DATA_INDEX = 3

# ------------------------------------------------------------------------------
"""
Program Classes
"""

class Move(EventHandler):

    selection = None

    @staticmethod
    def getName(): return "Move"

    @staticmethod
    def getIcon(): return QIcon.fromTheme("edit-redo")

    @staticmethod
    def mousePressEvent(ctx, e):
        Move.selection = ctx.canvas.getAt(ctx.transformCoords(e.x(), e.y()))

        if Move.selection:
            Node.unhighlight()
            Move.selection.setHighlight(True)


    @staticmethod
    def mouseReleaseEvent(ctx, e):
        Move.selection = None
        Node.unhighlight()


    @staticmethod
    def mouseMoveEvent(ctx, e):
        if Move.selection:
            Move.selection.pos = ctx.transformCoords(e.x(), e.y())

# ------------------------------------

class AddNode(EventHandler):

    @staticmethod
    def getName(): return "Add Node"

    @staticmethod
    def getIcon(): return QIcon.fromTheme("list-add")

    @staticmethod
    def mousePressEvent(ctx, e):
        ctx.canvas.addNode(*ctx.transformCoords(e.x(), e.y()))

    @staticmethod
    def mouseReleaseEvent(ctx, e): pass

    @staticmethod
    def mouseMoveEvent(ctx, e): pass

# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self):

        super(type(self), self).__init__()

        self.setWindowTitle("AC Designer")
        self.setMouseTracking(True)
        self.initWidgets()

    # ------------------------------------

    def initWidgets(self):

        main_layout = QHBoxLayout()
        main_widget = QWidget()

        self.listbox = QListWidget()

        for i, _class in enumerate(EventHandler.__subclasses__()):

            w = QListWidgetItem()
            w.setData(0, _class.getName())
            w.setData(DATA_INDEX, _class)
            w.setIcon(_class.getIcon())

            self.listbox.insertItem(i, w)

        main_layout.addWidget(self.listbox)

        self.canvas = Canvas(width=800, height=600)
        main_layout.addWidget(self.canvas)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # ------------------------------------

    def getSelection(self):
        return self.listbox.currentItem().data(DATA_INDEX)

    # ------------------------------------

    def mousePressEvent(self, e):
        
        handler = self.getSelection()
        handler.mousePressEvent(self, e)

        self.canvas.redraw()
        self.update()


    def mouseReleaseEvent(self, e):

        handler = self.getSelection()
        handler.mouseReleaseEvent(self, e)

        self.canvas.redraw()
        self.update()


    def mouseMoveEvent(self, e):

        handler = self.getSelection()
        handler.mouseMoveEvent(self, e)

        self.canvas.redraw()
        self.update()

    # ------------------------------------

    def transformCoords(self, x, y) -> Vector:

        rec = self.canvas.geometry()
        r = vec(0, 0) + Node.radius 

        return vec(
            x - self.listbox.geometry().width() - MOUSE_DIFF, y - MOUSE_DIFF
        ).clip(r/2, vec(rec.width(), rec.height()) - r)


# ------------------------------------------------------------------------------
"""
Main Code
"""

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()