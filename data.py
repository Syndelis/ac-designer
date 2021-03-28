"""
Imports
"""

# Data
from vector import vec
from enum import Enum
from typing import Union
import abc
import xml.dom.minidom as xml
from codeGenerator import Subtable

# Misc
from time import time

# ------------------------------------------------------------------------------
"""
Globals
"""

DOM = xml.getDOMImplementation()

# ------------------------------------------------------------------------------
"""
Invisible classes
"""

# Classes that inherit from XMLable should be able to create XML elements
class XMLable(abc.ABC):

    @abc.abstractmethod
    def toXML(self, doc: xml.Document) -> xml.Element: pass

    @abc.abstractmethod
    def toCode(self) -> str: pass

# ------------------------------------------------------------------------------

# For operator representation
class Op(Enum):

    GT='>'
    GE='>='
    EQ='=='
    LT='<'
    LE='<='
    NE='!='

# ------------------------------------------------------------------------------
"""
Drawable classes
"""

class Condition(XMLable):

    def __init__(self, state: int, op: Op, amnt: int):

        self.state = state # Node ID
        self.op = op
        self.amnt = amnt

    # ------------------------------------

    def toXML(self, doc: xml.Document) -> xml.Element:

        el = doc.createElement("condition")
        el.setAttribute("state", f"{self.state}")
        el.setAttribute("op", self.op.value)
        el.setAttribute("amnt", f"{self.amnt}")

        return el

    # ------------------------------------

    def toCode(self) -> str:
        return Subtable.condition(
            state=self.state, op=self.op.value, amnt=self.amnt)

# ------------------------------------------------------------------------------

# The base class for both Nodes and Edges.
# This class implements some common QWidget stuff
class Base:

    def __init__(self):
        self._highlit = False

    # ------------------------------------

    def getHighlight(self):
        return self._highlit

    def setHighlight(self, state: bool):

        self._highlit = state
        cls = type(self)

        if state:               cls.lit.append(self)
        elif self in cls.lit:   cls.lit.remove(self)

    # ------------------------------------

    @classmethod
    def unhighlight(cls):

        for i in cls.lit: i.highlit = False
        cls.lit.clear()

    # ------------------------------------

    highlit = property(getHighlight, setHighlight)

# ------------------------------------------------------------------------------

class Node(Base, XMLable):

    edgeReorder = lambda e: e.priority

    lit = []
    radius = 40

    def __init__(self, x, y, name='', radius=-1, highlight=True):

        self.incoming: list[Edge] = []
        self.outgoing: list[Edge] = []

        self.name = name
        self.id = -1 # Adjusted by Graph

        self.color = '#ffffff'

        self.pos = vec(x, y)

        if radius < 0: radius = type(self).radius
        self.radius = radius

        type(self).unhighlight()
        self.setHighlight(highlight)

    # ------------------------------------

    def move(self, x, y):

        self.pos = vec(x, y)
        return self # For convenience

    # ------------------------------------

    def addEdge(self, target):
        return Edge(self, target)

    # ------------------------------------

    def toXML(self, doc: xml.Document) -> xml.Element:

        el = doc.createElement("node")
        el.setAttribute("id", f"{self.id}")
        el.setAttribute("name", f"{self.name}")
        el.setAttribute("x", f"{self.pos.x}")
        el.setAttribute("y", f"{self.pos.y}")
        el.setAttribute("color", f"{self.color}")

        return el

    # ------------------------------------

    def toCode(self) -> str:

        return Subtable.node(name=self.name, src=self.id, code="\n" +\
                "\n\n".join(edge.toCode() for edge in self.outgoing))


# ------------------------------------------------------------------------------

class Edge(Base, XMLable):

    lit = []
    arrow_width = 5
    arrow_height = 8
    size_multiplier = 1.5
    box_angle = 15

    def __init__(self, node0: Node, node1: Node, highlit=True, register=True):

        self.nodes = node0, node1
        self.priority = len(node0.outgoing)

        if register: self.register()

        self.name = ''
        self.conditions: list[Condition] = []
        self.probability = 100

        self.offset = 30 # Drawing-related
        self.registered = False

        type(self).unhighlight()
        self.setHighlight(highlit)

    # ------------------------------------

    def addCondition(self, *args, condition: Condition=None, **kwargs):

        if condition is None:
            self.conditions.append(Condition(*args, **kwargs))

        elif type(condition) is Condition: self.conditions.append(condition)

        else: raise TypeError()

    # ------------------------------------

    def register(self):
        self.nodes[0].outgoing.append(self)
        self.nodes[1].incoming.append(self)
        self.registered = True


    def unregister(self):
        self.nodes[0].outgoing.remove(self)
        self.nodes[1].incoming.remove(self)
        self.registered = False

    # ------------------------------------

    def toXML(self, doc: xml.Document) -> xml.Element:

        el = doc.createElement("edge")
        el.setAttribute("name", f"{self.name}")
        el.setAttribute("src", f"{self.nodes[0].id}")
        el.setAttribute("dst", f"{self.nodes[1].id}")
        el.setAttribute("probability", f"{self.probability}")
        el.setAttribute("offset", f"{self.offset}")
        el.setAttribute("priority", f"{self.priority}")

        conds = doc.createElement("conditions")
        for condition in self.conditions:
            conds.appendChild(condition.toXML(doc))

        el.appendChild(conds)
        return el

    # ------------------------------------

    def toCode(self) -> str:

        p = Subtable.prob(percentage=self.probability/100)\
            if self.probability < 100 else ''

        if len(self.conditions):
            return Subtable.edge(
                name=self.name,
                conditions=" or ".join(cond.toCode() for cond in self.conditions),
                prob=(" and " + p) if p else '',
                dst=self.nodes[1].id
            )

        elif p: return Subtable.edge(
            name=self.name,
            conditions=p,
            prob='',
            dst=self.nodes[1].id
        )

        else: return Subtable.inconditionalEdge(dst=self.nodes[1].id, prob=p)

# -----------------------------------------------------------------------------

# Holds all nodes and is responsible for generating code
class Graph:

    def __init__(self):
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self.next_id = 0
        self.creation_time = time()

    # ------------------------------------

    def addNode(self, node: Node=None, x=-1, y=-1, newid=True):

        if node is None:
            node = Node(x, y, name=f'Node {self.next_id}')

        if newid:
            node.id = self.next_id
            self.next_id += 1

        self.nodes.append(node)


    def removeNode(self, node: Node):

        for edge in (node.outgoing + node.incoming):
            self.removeEdge(edge)

        self.nodes.remove(node)

    # ------------------------------------

    def addEdge(self, node0, node1: Node=None):

        if type(node0) is Node and type(node1) is Node:
            self.edges.append(node0.addEdge(node1))

        elif type(node0) is Edge:
            self.edges.append(node0)

        else: raise TypeError()

        return self.edges[-1]


    def removeEdge(self, edge: Edge):

        edge.unregister()
        self.edges.remove(edge)

    # ------------------------------------

    def remove(self, obj: Union[Node, Edge]):

        t = type(obj)
        if   t is Node: self.removeNode(obj)
        elif t is Edge: self.removeEdge(obj)

    # ------------------------------------

    def saveXML(self, filename="test.xml"):

        doc = DOM.createDocument(None, "AC", None)
        nodes = doc.createElement("nodes")

        for node in self.nodes:
            nodes.appendChild(node.toXML(doc))

        doc.documentElement.appendChild(nodes)

        edges = doc.createElement("edges")
        for edge in self.edges:
            edges.appendChild(edge.toXML(doc))

        doc.documentElement.appendChild(edges)

        with open(filename, "w") as f:
            doc.writexml(f, addindent='\t', newl='\n')

    # ------------------------------------

    @classmethod
    def loadXML(cls, filename="test.xml"):

        g = cls()
        doc = xml.parse(filename)

        for node in doc.documentElement.getElementsByTagName("node"):

            attr = node.attributes
            n = Node(
                float(attr['x'].value),
                float(attr['y'].value),
                attr['name'].value
            )

            n.id = int(attr['id'].value)
            n.color = attr['color'].value
            g.next_id = max(n.id + 1, g.next_id)

            g.addNode(n, newid=False)


        for edge in doc.documentElement.getElementsByTagName("edge"):

            attr = edge.attributes
            nodes = (
                find(g.nodes, lambda i: i.id == int(attr['src'].value)),
                find(g.nodes, lambda i: i.id == int(attr['dst'].value))
            )

            e = g.addEdge(*nodes)
            e.name = attr['name'].value
            e.probability = int(attr['probability'].value)
            e.offset = float(attr['offset'].value)
            e.priority = int(attr['priority'].value)

            e.registered = True

            for condition in edge.getElementsByTagName("condition"):

                attr = condition.attributes
                e.addCondition(
                    int(attr['state'].value),
                    Op(attr['op'].value),
                    int(attr['amnt'].value)
                )

        g.edges.sort(key=Node.edgeReorder)
        for node in g.nodes:
            node.outgoing.sort(key=Node.edgeReorder)

        Node.unhighlight()
        Edge.unhighlight()
        return g

    # ------------------------------------

    def _codeClass(self, name) -> str:

        return "\n".join((

            Subtable.namesetup(name=name),
            "\n".join(node.toCode() for node in self.nodes),
            Subtable.end()

        ))

    def generateCode(self, name="Test", cond=None) -> str:

        if cond:

            return "\n".join((
                Subtable.imports(),

                self._codeClass(name),

                Subtable.initialCondition(list=str(cond)),
                Subtable.instantiateInitialCondition(name=name),
                Subtable.plot(
                    name=name,
                    colors=str([node.color for node in self.nodes])
                )
            ))

        else:

            return "\n".join((
                Subtable.imports(),

                self._codeClass(name),

                Subtable.instantiate(name=name, statecount=len(self.nodes)),
                Subtable.plot(
                    name=name,
                    colors=str([node.color for node in self.nodes])
                )
            ))


# ------------------------------------------------------------------------------
"""
Auxiliary functions
"""

def find(iter, cond):

    for i in iter:
        if cond(i): return i

    return None