"""Two outputs wired together → ShortCircuitError at wire() time."""
from components.chips.sn74hc04 import SN74HC04
from framework import Circuit, wire


class ShortedInverters(Circuit):
    def __init__(self) -> None:
        self.u1 = SN74HC04(refdes_number=1)
        wire(self.u1.y_1, self.u1.y_2)
        super().__init__()
