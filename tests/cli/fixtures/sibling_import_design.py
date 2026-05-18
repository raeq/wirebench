"""A valid design that imports a sibling helper from the same folder.

If the validator hasn't put this file's directory on `sys.path`, the
import below fails with `ModuleNotFoundError: No module named
'sibling_helper'`."""
from sibling_helper import helper_value

from components.passives.rail import Rail
from components.passives.resistor import Resistor
from framework import Circuit, wire


class SiblingDesign(Circuit):
    def __init__(self) -> None:
        assert helper_value() == 42
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(330, refdes_number=1)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.gnd.out)
        super().__init__()
