"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon

from gui import Canvas, EventHandler

# Data
from vector import vec

# ------------------------------------------------------------------------------
"""
Program Classes
"""

# class Move(EventHandler):

#     def getName(self):
#         return "Move"

#     # ------------------------------------

#     def mousePressEvent(self, e):
#         pass

class AddNode(EventHandler):

    @staticmethod
    def getName(): return "Add Node"

    @staticmethod
    def getIcon(): return QIcon.fromTheme("list-add")

    @staticmethod
    def mousePressEvent(ctx, e):
        ctx.canvas.addNode(*ctx.transformCoords(e.x(), e.y()))

    @staticmethod
    def mouseReleaseEvent(ctx, e):
        return super.mouseReleaseEvent(ctx, e)

    @staticmethod
    def mouseMoveEvent(ctx, e):
        return super.mouseMoveEvent(ctx, e)

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
            w.setData(3, _class)
            w.setIcon(_class.getIcon())
            self.listbox.insertItem(i, w)

        main_layout.addWidget(self.listbox)

        self.canvas = Canvas(width=800, height=600)
        main_layout.addWidget(self.canvas)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # ------------------------------------

    def getSelection(self):
        return self.listbox.currentItem()

    # ------------------------------------

    def mousePressEvent(self, e):
        
        handler = self.getSelection().data(3)
        handler.mousePressEvent(self, e)

        self.canvas.redraw()
        self.update()

    # ------------------------------------

    def transformCoords(self, x, y):

        return (
            x - self.listbox.geometry().width(), y
        )

# ------------------------------------------------------------------------------
"""
Main Code
"""

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()