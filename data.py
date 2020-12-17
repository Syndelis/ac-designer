"""
Imports
"""

# Data
from vector import vec
from enum import Enum
import abc
import xml.dom.minidom as xml

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

# Classes that inherit from XMLable should be able to create 
class XMLable(abc.ABC):

    @abc.abstractmethod
    def toXML(self, doc: xml.Document) -> xml.Element: pass

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

    def __init__(self, target: int, op: Op, amnt: int):
        
        self.target = target # Node ID
        self.op = op
        self.amnt = amnt

    # ------------------------------------

    def toXML(self, doc: xml.Document) -> xml.Element:

        el = doc.createElement("condition")
        el.setAttribute("target", f"{self.target}")
        el.setAttribute("op", self.op.value)
        el.setAttribute("amnt", f"{self.amnt}")

        return el

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
    
    lit = []

    def __init__(self, x, y, name='', radius=40, highlight=True):

        self.incoming: list[Edge] = []
        self.outgoing: list[Edge] = []

        self.name = name
        self.id = -1 # Adjusted by Graph

        self.pos = vec(x, y)
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

        return el


# ------------------------------------------------------------------------------

class Edge(Base, XMLable):

    lit = []

    def __init__(self, node0: Node, node1: Node, highlit=True):

        self.nodes = node0, node1
        node0.outgoing.append(self)
        node1.incoming.append(self)

        self.name = ''

        self.conditions: list[Condition] = []

        type(self).unhighlight()
        self.setHighlight(highlit)

    # ------------------------------------

    def addCondition(self, *args, **kwargs):
        self.conditions.append(Condition(*args, **kwargs))

    # ------------------------------------

    def toXML(self, doc: xml.Document) -> xml.Element:

        el = doc.createElement("edge")
        el.setAttribute("name", f"{self.name}")
        el.setAttribute("src", f"{self.nodes[0].id}")
        el.setAttribute("dst", f"{self.nodes[1].id}")

        conds = doc.createElement("conditions")
        for condition in self.conditions:
            conds.appendChild(condition.toXML(doc))

        el.appendChild(conds)
        return el

# -----------------------------------------------------------------------------

# Holds all nodes and is responsible for generating code
class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.creation_time = time()

    # ------------------------------------

    def addNode(self, node: Node=None, x=-1, y=-1, newid=True):

        if node is None: node = Node(x, y)

        if newid: node.id = int(time() - self.creation_time)
        self.nodes.append(node)

    # ------------------------------------

    def addEdge(self, node0: Node, node1: Node):
        self.edges.append(node0.addEdge(node1))
        return self.edges[-1]


    # ------------------------------------

    # TODO
    def toCode(self) -> str:

        # for node in self.nodes:
        #   for edge in node.edges:
        #       if not edge.processed:

        pass

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

            g.addNode(n, newid=False)

        
        for edge in doc.documentElement.getElementsByTagName("edge"):

            attr = edge.attributes
            nodes = (
                find(g.nodes, lambda i: i.id == int(attr['src'].value)),
                find(g.nodes, lambda i: i.id == int(attr['dst'].value))
            )

            e = g.addEdge(*nodes)
            
            for condition in edge.getElementsByTagName("condition"):
                
                attr = condition.attributes
                e.addCondition(
                    attr['target'].value,
                    Op(attr['op'].value),
                    attr['amnt'].value
                )

        return g


# ------------------------------------------------------------------------------
"""
Auxiliary functions
"""

def find(iter, cond):

    for i in iter:
        if cond(i): return i

    return None