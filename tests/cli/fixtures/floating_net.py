"""Two passive resistors meeting with no driver → FloatingNetError at
Circuit construction time."""
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from framework import Circuit, wire


class FloatingPair(Circuit):
    def __init__(self) -> None:
        self.r1 = Resistor(1000, refdes_number=1)
        self.r2 = Resistor(1000, refdes_number=2)
        self.rail = Rail(True)
        # Single floating net: both resistors' t1 ends meet with no
        # driver. The t2 ends are wired to the rail so the mandatory-
        # pin check passes — that net has a driver, so only the t1
        # net trips FloatingNetError, which is what this CLI test
        # pins down.
        wire(self.r1.t1, self.r2.t1)
        wire(self.rail.out, self.r1.t2, self.r2.t2)
        super().__init__()
