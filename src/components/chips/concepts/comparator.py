from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class Comparator(FactorNode):
    """A single voltage comparator cell.

    Output is HIGH when V+ exceeds V−, LOW when V+ ≤ V−, and undefined
    (None) when either input is undriven. The cell has no notion of
    "reference" or polarity — that is decided by the surrounding circuit.

    This is the unit-of-design building block; physical chips like the
    LM393 (dual) and LM339 (quad) are packages of these cells.
    """

    __slots__ = ('_ports',)

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'v_plus':  Port('v_plus',  Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'v_minus': Port('v_minus', Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'out':     Port('out',     Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def evaluate(self) -> None:
        vp = self._ports['v_plus'].value
        vm = self._ports['v_minus'].value
        if vp is None or vm is None:
            self._ports['out'].drive(None)
        else:
            self._ports['out'].drive(vp > vm)

    def __call__(self, v_plus, v_minus):
        self._assert_no_inputs_wired()
        self._ports['v_plus'].drive(v_plus)
        self._ports['v_minus'].drive(v_minus)
        self.evaluate()
        return self._ports['out'].value

    def __str__(self) -> str:
        return f"Comparator({self._ports['v_plus'].value} > {self._ports['v_minus'].value})"

    def __repr__(self) -> str:
        return "Comparator()"
