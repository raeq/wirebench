"""Two passive resistors meeting with no driver → FloatingNetError at
Circuit construction time."""
from components.passives.resistor import Resistor
from framework import Circuit, wire


class FloatingPair(Circuit):
    def __init__(self) -> None:
        self.r1 = Resistor(1000, refdes_number=1)
        self.r2 = Resistor(1000, refdes_number=2)
        wire(self.r1.t1, self.r2.t1)
        super().__init__()
