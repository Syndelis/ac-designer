"""
Imports
"""

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon, QPainter, QPen

from gui import Canvas, EventHandler
from simulation import SimulationWindow

# Data
from vector import vec, Vector
from data import Graph, Node, Edge, Op, Condition

# Math
from numpy import arctan, linalg, sign
from math import sin, cos, atan2

# Good practices
from typing import Union

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
    def getIcon(cls):
        return QIcon("icons/move.png")

    @classmethod
    def mousePressEvent(cls, ctx, e):

        cls.selection = ctx.canvas.getAt(ctx.transformCoords(e.x(), e.y()))
        t = type(cls.selection)

        if t in (Node, Edge):
            t.unhighlight()
            cls.selection.setHighlight(True)


    @classmethod
    def mouseReleaseEvent(cls, ctx, e):
        cls.selection = None
        Node.unhighlight()
        Edge.unhighlight()


    @classmethod
    def mouseMoveEvent(cls, ctx, e):

        t = type(cls.selection)
        mouse = ctx.transformCoords(e.x(), e.y())

        if t is Node:
            cls.selection.pos = mouse + ctx.canvas.cam

        elif t is Edge:

            # Get vector from the middle point of the edge to the mouse
            mouse_vec = mouse + ctx.canvas.cam - cls.selection.calculated

            # Now project that into the actual perpendicular vector of the edge
            perp = cls.selection.perp
            proj = mouse_vec.dot(perp) / linalg.norm(perp)**2 * perp

            """
            Two vectors form an obtuse angle if their dot product is negative
            """

            # Finally, get the projection's, length
            cls.selection.offset = linalg.norm(proj) * sign(perp.dot(proj))


# ------------------------------------

class AddNode(EventHandler):

    @classmethod
    def getName(cls): return "Add Node"

    @classmethod
    def getIcon(cls):
        return QIcon("icons/add-node.png")

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
    def getIcon(cls):
        return QIcon("icons/add-edge.png")

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

            x0, y0 = (cls.edge[0].pos - ctx.canvas.cam).astype(int)
            r0 = cls.edge[0].radius//2

            if type(selection) is Node:

                x1, y1 = (selection.pos - ctx.canvas.cam).astype(int)
                r1 = selection.radius // 2
                selection.highlit = True

            else:

                x1, y1 = (mouse - ctx.canvas.cam).astype(int)
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

    old_mouse = None
    old_cam = None
    button = 0

    def __init__(self):

        super(type(self), self).__init__()

        self.setWindowTitle("AC Designer")
        self.setMouseTracking(True)

        menubar = self.menuBar()
        # File Menu ------------------------

        save_act = QAction('Save', self)
        save_act.triggered.connect(self.saveXML)

        load_act = QAction('Load', self)
        load_act.triggered.connect(self.loadXML)

        file_menu = menubar.addMenu('File')
        file_menu.addAction(save_act)
        file_menu.addAction(load_act)

        # Simulation Menu ------------------

        run_act = QAction('Run', self)
        run_act.triggered.connect(self.runAction)

        simulation_menu = menubar.addMenu('Simulation')
        simulation_menu.addAction(run_act)

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

        self.listbox.setMinimumWidth(150)
        self.listbox.setMaximumWidth(150)
        main_layout.addWidget(self.listbox)

        self.canvas = Canvas(main=self, width=800, height=600)
        main_layout.addWidget(self.canvas)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.canvas.redraw()
        self.update()

    # ------------------------------------

    def getSelection(self):
        return self.listbox.currentItem().data(DATA_INDEX)

    # ------------------------------------

    def mousePressEvent(self, e):

        self.button = e.button()

        if e.button() & Qt.LeftButton:

            handler = self.getSelection()
            handler.mousePressEvent(self, e)
            self.canvas.redraw()

            self.update()

        elif e.button() & Qt.MiddleButton:
            self.old_mouse = vec(e.x(), e.y())
            self.old_cam = self.canvas.cam


    def mouseReleaseEvent(self, e):

        self.button = 0

        if e.button() & Qt.LeftButton:

            handler = self.getSelection()
            handler.mouseReleaseEvent(self, e)
            self.canvas.redraw()

            self.update()

        elif e.button() & Qt.MiddleButton:
            self.canvas.cam = self.old_cam +\
                (self.old_mouse - vec(e.x(), e.y())).astype(int)

            self.canvas.cam.apply(lambda i: max(0, i))

            self.old_mouse = None
            self.old_cam = None


    def mouseMoveEvent(self, e):

        if self.button & Qt.LeftButton:
            self.canvas.redraw()
            handler = self.getSelection()
            handler.mouseMoveEvent(self, e)

            self.update()

        elif self.button & Qt.MiddleButton:
            self.canvas.cam = self.old_cam +\
                (self.old_mouse - vec(e.x(), e.y())).astype(int)

            self.canvas.cam.apply(lambda i: max(0, i))

            self.canvas.redraw()
            self.update()


    def mouseDoubleClickEvent(self, e):

        if e.button() > 1: return

        at = self.canvas.getAt(self.transformCoords(e.x(), e.y()))
        self.launchEditor(at)


    def launchEditor(self, obj: Union[Node, Edge]):

        if type(obj) is Edge:
            self.edge_editor = EditEdgeWindow(obj, self)
            self.edge_editor.show()


        elif type(obj) is Node:
            self.node_editor = EditNodeWindow(obj, self)
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

        if filename:
            self.canvas.graph.saveXML(filename[0])


    def loadXML(self):

        filename = QFileDialog.getOpenFileName(
            self, "Load Model", ".", "Graph (*.xml)")

        if filename:
            self.canvas.graph = Graph.loadXML(filename[0])
            self.canvas.redraw()
            self.update()

    # ------------------------------------

    def runAction(self):

        # TODO

        if len(self.canvas.graph.nodes) > 1:

            self.simulation_window = SimulationWindow(self.canvas.graph)
            self.simulation_window.show()

        
        else:

            msg = QMessageBox()
            msg.setText(
                "You need at least 2 nodes in order to simulate something.")

            msg.exec()

# ------------------------------------------------------------------------------

class ColorPicker(QPushButton):

    def __init__(self, *args, color='white', **kwargs):

        super(type(self), self).__init__(*args, **kwargs)
        self._color = color

        self.clicked.connect(self.colorPicker)
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


    def colorPicker(self):

        picker = QColorDialog(self)
        picker.setCurrentColor(QColor(self.color))

        if picker.exec_():
            self.color = picker.currentColor().name()


    color = property(getColor, setColor)

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

        # ------------------------------------
        # Color picker
        lay = QHBoxLayout()
        wid = QWidget()

        lay.addWidget(QLabel("Color"))
        self.colorbox = ColorPicker(color=self.target.color)

        lay.addWidget(self.colorbox)

        wid.setLayout(lay)
        main_layout.addWidget(wid)

        # ------------------------------------
        # Edge order

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        main_layout.addWidget(line)

        lay = QVBoxLayout()
        wid = QWidget()

        lay.addWidget(QLabel("Outgoing edge execution order"))

        self.list = QListWidget()
        for edge in self.target.outgoing:
            e = QListWidgetItem()
            e.setText(edge.name)
            e.setIcon(QIcon.fromTheme('format-justify-fill'))
            e.setData(DATA_INDEX, edge)
            self.list.addItem(e)

        self.list.setDragDropMode(QAbstractItemView.InternalMove)

        self.list.setToolTip(
            "Here you can rearrange the order of edge execution.")

        lay.addWidget(self.list)

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
        self.target.color = self.colorbox.color

        self.ctx.canvas.redraw()
        self.ctx.update()

        edges = [
            self.list.item(i).data(DATA_INDEX)
            for i in range(self.list.count())
        ]

        for edge in edges: self.ctx.canvas.graph.edges.remove(edge)
        self.ctx.canvas.graph.edges.extend(edges)

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

        self._state = QComboBox()

        for node in ctx.canvas.graph.nodes:
            self._state.addItem(node.name, userData=node.id)


        if state is not None:

            for ind, node in enumerate(ctx.canvas.graph.nodes):
                if node.id == state: break

            self._state.setCurrentIndex(ind)


        lay.addWidget(self._state)

        # ------------------------------------
        # Operator

        self._op = QComboBox()

        for i in Op.__members__:
            self._op.addItem(Op[i].value)


        if op is not None:

            self._op.setCurrentIndex(
                list(Op.__members__.values()).index(Op(op))
            )

        lay.addWidget(self._op)

        # ------------------------------------
        # Amount

        self._amnt = QSpinBox()

        if amnt is not None:
            self._amnt.setValue(amnt)

        lay.addWidget(self._amnt)

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

        if not self.target.name:
            self.target.name = f'New Edge'

        self.target_conditions = self.target.conditions.copy()
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
        # Probability

        lay = QHBoxLayout()
        wid = QWidget()

        problabel = QLabel("Probability (%):")
        self.probbox = QSpinBox(self)
        self.probbox.setMaximum(100)
        self.probbox.setValue(self.target.probability)

        lay.addWidget(problabel)
        lay.addWidget(self.probbox)
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

        self.populateConditions()

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


    def populateConditions(self):

        l = QHBoxLayout()
        w = QWidget()

        l.addWidget(QLabel("Target State"))
        l.addWidget(QLabel("Operator"))
        l.addWidget(QLabel("Amount"))
        l.addWidget(QLabel(""))

        w.setLayout(l)
        self.condition_lay.addWidget(w)

        self.conditionOps = []

        for condition in self.target_conditions:
            self.plusBtn(
                False, state=condition.state,
                op=condition.op, amnt=condition.amnt, newcond=False
            )

    # ------------------------------------

    def plusBtn(self, update=True, state: int=None,
                op: str=None,amnt: int=None, newcond: bool=True):

        l = QHBoxLayout()
        w = QWidget()

        cond = ConditionOp(self.ctx, state, op, amnt)
        l.addWidget(cond)

        remove = QPushButton()
        remove.setIcon(QIcon.fromTheme('list-remove'))
        remove.clicked.connect(self.removeBtn(len(self.conditionOps)))

        l.addWidget(remove)
        w.setLayout(l)

        self.condition_lay.addWidget(w)
        self.conditionOps.append(cond)

        # This is to prevent recreating the same conditions when one is deleted
        if newcond:
            self.target_conditions.append(Condition(state, op, amnt))

        if update: self.update()


    def okBtn(self):

        self.target.name = self.namebox.text()
        self.target.probability = self.probbox.value()
        self.target.conditions.clear()

        for cond in self.conditionOps:

            self.target.addCondition(
                cond.state, Op(cond.op),
                cond.amnt
            )

        if not self.target.registered: self.target.register()

        if not self.target in self.ctx.canvas.graph.edges:
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


    def removeBtn(self, ind: int):

        def removeInd():

            # if len(self.target_conditions) > ind:
            self.target_conditions.pop(ind)
            self.conditionOps.pop(ind)

            for tar, op in zip(self.target_conditions, self.conditionOps):
                tar.state = op.state
                tar.op = op.op
                tar.amnt = op.amnt

            for i in reversed(range(self.condition_lay.count())):
                self.condition_lay.itemAt(i).widget().setParent(None)

            self.populateConditions()
            self.update()

        return removeInd


# ------------------------------------------------------------------------------
"""
Main Code
"""

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
