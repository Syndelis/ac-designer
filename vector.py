"""
Imports
"""

# Numpy's efficient array
from numpy import array, ndarray

# Enumerator for x,y,z/r,g,b,a ops
from enum import Enum

# ------------------------------------------------------------------------------
"""
Class definition
"""

# Enumerator for x,y,z/r,g,b,a ops
class PosEnum(Enum):
    x=r=0
    y=g=1
    z=b=2
    a=3

# ------------------------------------------------------------------------------

def vec(*args, **kwargs):
    return array(args, **kwargs).view(Vector)

class Vector(ndarray):

    def apply(self, func):

        for i in range(len(self)):
            self[i] = func(self[i])

        return self

    def __getattr__(self, attr):

        try:

            if len(attr) == 1: return self[PosEnum[attr].value]

            else: return vec([
                self[PosEnum[letter].value] for letter in attr
            ])

        except KeyError:
            raise ValueError(f"{attr} not in {list(PosEnum.__members__)}")

        except IndexError:
            raise ValueError(f"Index out of bounds")