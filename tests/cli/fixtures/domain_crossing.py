"""wire() across two distinct ground domains → DomainCrossingError."""
from framework import Circuit, wire
from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction, Port
from framework.signals import Digital

ISOLATED_A = GroundDomain('ISOLATED_A')


class CrossDomainDesign(Circuit):
    def __init__(self) -> None:
        self.host = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
        self.iso  = Port('b', Direction.IN,  ISOLATED_A, signal_type=Digital)
        wire(self.host, self.iso)
        super().__init__()
