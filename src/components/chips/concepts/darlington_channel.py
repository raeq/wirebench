from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class DarlingtonChannel(FactorNode):
    """One channel of a high-current open-collector Darlington driver.

    The cell that the ULN2003A and ULN2803 are built from.  A Darlington
    pair (two cascaded NPN transistors) is fed by a series base resistor
    and drives an open-collector output that sinks current to ground
    when the base voltage is above the turn-on threshold.

    Pins
    ----
    b   (IN, Analog)  — base voltage of the input transistor
    out (OUT, Digital) — open-collector output

    Behaviour:
      b ≤ V_THRESHOLD → transistor off → out pin HIGH
      b  > V_THRESHOLD → transistor on  → out pin LOW (sinking)

    Note that this inverts the input level, but the cell takes an analog
    voltage rather than a logic level, so it is not a logic inverter
    proper — it is a voltage-threshold open-collector buffer that
    happens to be inverting.
    """

    __slots__ = ('_ports',)

    V_THRESHOLD: float = 1.0   # V — base turn-on voltage

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'b':   Port('b',   Direction.IN,  domain, mandatory=False, signal_type=Analog),
            'out': Port('out', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def evaluate(self) -> None:
        v = self._ports['b'].value
        if v is None:
            self._ports['out'].drive(None)
            return
        # open-collector: conducting → LOW, off → HIGH
        self._ports['out'].drive(float(Analog(v)) <= self.V_THRESHOLD)

    def __call__(self, b: float | None) -> bool | None:
        self._ports['b'].drive(b)
        self.evaluate()
        return self._ports['out'].value

    def __repr__(self) -> str:
        return f"DarlingtonChannel(out={self._ports['out'].value!r})"
