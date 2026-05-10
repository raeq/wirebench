from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class TriStateBuffer(FactorNode):
    """Single-bit tri-state buffer: a controllable disconnect.

    Pins:
      a   (IN)  — data input
      oe  (IN)  — output enable, active HIGH
      y   (OUT) — pin: a when oe=1, high-impedance (None) when oe=0

    "High-impedance" is modelled as None on the output port — downstream
    components see no driven signal and treat it as undriven.  This is
    how a real chip frees a shared bus when its OE is asserted low.
    """

    __slots__ = ['_ports']

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'a':  Port('a',  Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'oe': Port('oe', Direction.IN,  domain, mandatory=False, signal_type=Digital),
            'y':  Port('y',  Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def evaluate(self) -> None:
        oe_val = self._ports['oe'].value
        if oe_val is None or not bool(Digital(oe_val)):
            self._ports['y'].drive(None)
            return
        a_val = self._ports['a'].value
        self._ports['y'].drive(None if a_val is None else bool(Digital(a_val)))

    def __call__(self, a: bool | None, oe: bool) -> bool | None:
        self._ports['a'].drive(a)
        self._ports['oe'].drive(oe)
        self.evaluate()
        return self._ports['y'].value

    def __repr__(self) -> str:
        return f"TriStateBuffer(y={self._ports['y'].value!r})"
