from string import Template

class CodeGen(dict):
    def __getattr__(self, name):
        if name in self.keys(): return self[name].substitute

Subtable = CodeGen({

    # ONCE
    "imports": Template(
        "from ca import *\n"
        "from random import random\n"
        "from collections import Counter"
    ),

    # ONCE
    "namesetup": Template(
        "class $name(CA):\n"
        "\tdef rule(self, x, y):\n"
        "\t\ts = self[x, y]\n"
        "\t\tn = neighbors8(self, x, y)\n"
        "\t\tnhood = Counter(n)"
    ),

    # For every different node
    "node": Template("\t\tif s == $src:"),

    # For every node's edge
    "edge": Template("\t\t\tif $conditions:\n\t\t\t\treturn $dst"),

    # For every edge's condition
    "condition": Template("(nhood[$state] $op $amnt)"),

    # ONCE
    "end": Template("\t\treturn s"),
    "instantiate": Template("c = $name(30, values=range($statecount))"),
    "plot": Template("plot(c, N=50, colors=$colors, out='$name.pdf', graphic=True)"),

    # CONDITIONAL
    "initialCondition": Template("initial_condition = $list"),
    "instantiateInitialCondition": Template("c = $name(30, random_values=False, values=initial_condition[::-1])")

})