from string import Template

class CodeGen(dict):
    def __getattr__(self, name):
        if name in self.keys(): return self[name].substitute

Subtable = CodeGen({

    # ONCE
    "imports": Template(
        "from ca import *\n"
        "from random import random\n"
        "from collections import Counter\n"
    ),

    # ONCE
    "namesetup": Template(
        "class $name(CA):\n\n"
        "\tdef rule(self, x, y):\n"
        "\t\ts = self[x, y]\n"
        "\t\tn = neighbors8(self, x, y)\n"
        "\t\tnhood = Counter(n)\n"
    ),

    # For every different node
    "node": Template("\t\t# State $name\n\t\tif s == $src:$code\n\n\t\t\tpass\n"),

    # For every node's edge
    "edge": Template(
        "\t\t\t# Edge $name\n\t\t\tif ($conditions)$prob:\n\t\t\t\treturn $dst"),

    # For every edge's condition
    "condition": Template("(nhood[$state] $op $amnt)"),

    # ONCE
    "end": Template("\t\treturn s\n\n"),
    "instantiate": Template("c = $name(30, values=range($statecount), max=$statecount -1)"),
    "plot": Template("plot(c, N=50, colors=$colors, names=$names, out='$name.pdf', graphic=True)"),

    # CONDITIONAL
    "initialCondition": Template("initial_condition = $list\n"),
    "instantiateInitialCondition": Template(
        "c = $name(30, random_values=False, values=initial_condition[::-1], max=$statecount -1)"
    ),
    
    "inconditionalEdge": Template("\t\t\treturn $dst"),
    "prob": Template("random() < $percentage")

})