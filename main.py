"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon, QPainter, QPen

from gui import Canvas, EventHandler

# Data
from vector import vec, Vector
from data import Graph, Node, Edge, Op

# Math
from numpy import arctan
from math import sin, cos, atan2

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

    @classmethod
    def getName(cls): return "Move"

    @classmethod
    def getIcon(cls): return QIcon.fromTheme("edit-redo")

    @classmethod
    def mousePressEvent(cls, ctx, e):
        cls.selection = ctx.canvas.getAt(ctx.transformCoords(e.x(), e.y()))

        if type(cls.selection) is Node:
            Node.unhighlight()
            cls.selection.setHighlight(True)


    @classmethod
    def mouseReleaseEvent(cls, ctx, e):
        cls.selection = None
        Node.unhighlight()
        ctx.canvas.unhighlight()


    @classmethod
    def mouseMoveEvent(cls, ctx, e):
        if cls.selection:
            cls.selection.pos = ctx.transformCoords(e.x(), e.y())

# ------------------------------------

class AddNode(EventHandler):

    @classmethod
    def getName(cls): return "Add Node"

    @classmethod
    def getIcon(cls): return QIcon.fromTheme("list-add")

    @classmethod
    def mousePressEvent(cls, ctx, e):

        selection = ctx.canvas.getAt(ctx.transformCoords(e.x(), e.y()))

        if selection is None:
            ctx.canvas.addNode(*ctx.transformCoords(e.x(), e.y()))

    @classmethod
    def mouseReleaseEvent(cls, ctx, e): pass

    @classmethod
    def mouseMoveEvent(cls, ctx, e): pass

# ------------------------------------

class AddEdge(EventHandler):

    edge = [None, None]
    window = None

    @classmethod
    def getName(cls): return "Add Edge"

    @classmethod
    def getIcon(cls): return QIcon.fromTheme("edit-select-all")

    @classmethod
    def mousePressEvent(cls, ctx, e):
        selection = ctx.canvas.getAt(ctx.transformCoords(e.x(), e.y()))

        if type(selection) is Node:
            ctx.canvas.unhighlight()
            selection.highlit = True

            cls.edge[0] = selection


    @classmethod
    def mouseReleaseEvent(cls, ctx, e):

        if all(cls.edge) and cls.edge[0] != cls.edge[1]:
            cls.window = EditEdgeWindow(
                            Edge(*cls.edge, register=False),
                            ctx
                        )
            cls.window.show()
        
        ctx.canvas.unhighlight()
        cls.edge[:] = None, None


    @classmethod
    def mouseMoveEvent(cls, ctx, e):

        if cls.edge[0]:
        
            mouse = ctx.transformCoords(e.x(), e.y())
            selection = ctx.canvas.getAt(mouse)

            painter = QPainter(ctx.canvas.pixmap())
            pen = QPen()
            pen.setColor(QColor('blue'))
            pen.setWidth(3)
            painter.setPen(pen)

            ctx.canvas.unhighlight()
            cls.edge[1] = selection

            x0, y0 = cls.edge[0].pos.astype(int)
            r0 = cls.edge[0].radius//2

            if type(selection) is Node:

                x1, y1 = selection.pos.astype(int)
                r1 = selection.radius // 2
                selection.highlit = True

            else:

                x1, y1 = mouse.astype(int)
                r1 = r0


            angle = atan2(y0 - y1, x0 - x1)
            x0 -= round(cos(angle) * r0)
            y0 -= round(sin(angle) * r0)
            x1 += round(cos(angle) * r1)
            y1 += round(sin(angle) * r1)

            painter.drawLine(x0 + r0, y0 + r0, x1 + r1, y1 + r1)

            cls.edge[0].highlit = True
            painter.end()

# ------------------------------------------------------------------------------

class MainWindow(QMainWindow):

    node_editor = None
    edge_editor = None

    def __init__(self):

        super(type(self), self).__init__()

        self.setWindowTitle("AC Designer")
        self.setMouseTracking(True)

        save_act = QAction('Save', self)
        save_act.triggered.connect(self.saveXML)

        load_act = QAction('Load', self)
        load_act.triggered.connect(self.loadXML)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(save_act)
        file_menu.addAction(load_act)

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
        
        self.canvas.redraw()
        handler = self.getSelection()
        handler.mousePressEvent(self, e)

        self.update()


    def mouseReleaseEvent(self, e):

        self.canvas.redraw()
        handler = self.getSelection()
        handler.mouseReleaseEvent(self, e)

        self.update()


    def mouseMoveEvent(self, e):

        self.canvas.redraw()
        handler = self.getSelection()
        handler.mouseMoveEvent(self, e)

        self.update()


    def mouseDoubleClickEvent(self, e):
        
        at = self.canvas.getAt(self.transformCoords(e.x(), e.y()))

        if type(at) is Edge:
            self.edge_editor = EditEdgeWindow(at, self)
            self.edge_editor.show()

        
        elif type(at) is Node:
            self.node_editor = EditNodeWindow(at, self)
            self.node_editor.show()

    # ------------------------------------

    def transformCoords(self, x, y) -> Vector:

        rec = self.canvas.geometry()
        r = vec(0, 0) + Node.radius 

        return vec(
            x - self.listbox.geometry().width() - MOUSE_DIFF, y - MOUSE_DIFF
        ).clip(r/2, vec(rec.width(), rec.height()) - r)


    def saveXML(self):

        filename = QFileDialog.getSaveFileName(
            self, "Save Model", ".", "Graph (*.xml)")
        
        self.canvas.graph.saveXML(filename[0])


    def loadXML(self):

        filename = QFileDialog.getOpenFileName(
            self, "Load Model", ".", "Graph (*.xml)")

        self.canvas.graph = Graph.loadXML(filename[0])
        self.canvas.redraw()
        self.update()


# ------------------------------------------------------------------------------

class EditNodeWindow(QWidget):

    def __init__(self, target: Node, ctx):

        super(type(self), self).__init__()
        self.target = target
        self.ctx = ctx
        self.initWidgets()


    def initWidgets(self):
        
        main_layout = QVBoxLayout()

        # ----------------------------------------
        # Name

        lay = QHBoxLayout()
        wid = QWidget()

        lay.addWidget(QLabel("Name"))

        self.namebox = QLineEdit()
        self.namebox.setText(self.target.name)
        self.namebox.returnPressed.connect(self.okBtn)

        lay.addWidget(self.namebox)

        wid.setLayout(lay)
        main_layout.addWidget(wid)

        # ----------------------------------------
        # Buttons
        lay = QHBoxLayout()
        wid = QWidget()

        ok = QPushButton('Ok')
        ok.clicked.connect(self.okBtn)

        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancelBtn)

        lay.addWidget(ok)
        lay.addWidget(cancel)
        
        wid.setLayout(lay)
        main_layout.addWidget(wid)

        self.setLayout(main_layout)


    def okBtn(self):

        self.target.name = self.namebox.text()

        self.ctx.canvas.redraw()
        self.ctx.update()

        self.close()

    def cancelBtn(self):
        self.close()

# ------------------------------------------------------------------------------

class ConditionOp(QWidget):

    def __init__(self, ctx, state: int=None, op: str=None, amnt: int=None):

        super(type(self), self).__init__()
        self.ctx = ctx

        lay = QHBoxLayout()

        # ------------------------------------
        # State

        l = QVBoxLayout()
        w = QWidget()

        l.addWidget(QLabel("Target State"))
        self._state = QComboBox()

        for node in ctx.canvas.graph.nodes:
            self._state.addItem(node.name, userData=node.id)


        if state is not None:

            for ind, node in enumerate(ctx.canvas.graph.nodes):
                if node.id == state: break

            self._state.setCurrentIndex(ind)


        l.addWidget(self._state)

        w.setLayout(l)
        lay.addWidget(w)

        # ------------------------------------
        # Operator

        l = QVBoxLayout()
        w = QWidget()

        l.addWidget(QLabel("Operator"))
        self._op = QComboBox()

        for i in Op.__members__:
            self._op.addItem(Op[i].value)


        if op is not None:

            self._op.setCurrentIndex(
                list(Op.__members__.values()).index(Op(op))
            )

        l.addWidget(self._op)

        w.setLayout(l)
        lay.addWidget(w)

        # ------------------------------------
        # Amount

        l = QVBoxLayout()
        w = QWidget()

        l.addWidget(QLabel("Amount"))
        self._amnt = QSpinBox()

        if amnt is not None:
            self._amnt.setValue(amnt)

        l.addWidget(self._amnt)

        w.setLayout(l)
        lay.addWidget(w)

        # ------------------------------------

        self.setLayout(lay)


    # ------------------------------------

    def getState(self) -> Node:
        return self._state.currentData()

    def getOp(self) -> str:
        return self._op.currentText()

    def getAmnt(self) -> int:
        return self._amnt.value()

    state = property(getState)
    op = property(getOp)
    amnt = property(getAmnt)

# ------------------------------------------------------------------------------

class EditEdgeWindow(QWidget):

    def __init__(self, target: Edge, ctx):

        super(type(self), self).__init__()
        self.target = target
        self.ctx = ctx
        self.initWidgets()


    def initWidgets(self):
        
        main_layout = QVBoxLayout()

        # ------------------------------------
        # Name

        lay = QHBoxLayout()
        wid = QWidget()

        namelabel = QLabel("Name:")
        self.namebox = QLineEdit()
        self.namebox.setText(self.target.name)
        self.namebox.returnPressed.connect(self.okBtn)

        lay.addWidget(namelabel)
        lay.addWidget(self.namebox)
        wid.setLayout(lay)
        main_layout.addWidget(wid)

        # ------------------------------------
        # Conditions

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        main_layout.addWidget(line)
        main_layout.addWidget(QLabel("Conditions"))

        self.condition_lay = QVBoxLayout()
        self.condition_wid = QWidget()

        self.conditionOps = []

        for condition in self.target.conditions:
            self.plusBtn(
                False, state=condition.state,
                op=condition.op, amnt=condition.amnt
            )

        self.condition_wid.setLayout(self.condition_lay)
        main_layout.addWidget(self.condition_wid)

        # ------------------------------------
        # Plus button

        plus = QPushButton('+')
        plus.clicked.connect(self.plusBtn)
        main_layout.addWidget(plus)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # ------------------------------------
        # Ok/Cancel

        lay = QHBoxLayout()
        wid = QWidget()

        ok = QPushButton('Ok')
        ok.clicked.connect(self.okBtn)

        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancelBtn)

        lay.addWidget(ok)
        lay.addWidget(cancel)
        
        wid.setLayout(lay)
        main_layout.addWidget(wid)

        # ------------------------------------

        self.setLayout(main_layout)

    # ------------------------------------

    def plusBtn(self, update=True,state: int=None,op: str=None,amnt: int=None):

        w = ConditionOp(self.ctx, state, op, amnt)
        self.condition_lay.addWidget(w)
        self.conditionOps.append(w)

        if update: self.update()


    def okBtn(self):

        self.target.name = self.namebox.text()

        for cond in self.conditionOps:

            self.target.addCondition(
                cond.state, Op(cond.op),
                cond.amnt
            )


        self.target.register()
        self.ctx.canvas.graph.addEdge(self.target)

        self.ctx.canvas.redraw()
        self.ctx.update()

        self.close()


    def cancelBtn(self):

        # TODO: What happens when deleting a registered edge?
        del self.target
        # Needs an 'unregister' command in order to actually remove it
        # Better done in a menu context rather than on the editor itself
        self.close()


# ------------------------------------------------------------------------------
"""
Main Code
"""

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()