from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class LM393(FactorNode):
    """Single-channel voltage comparator (TI LM393).

    Output is HIGH when V+ exceeds V−.  The chip itself has no notion of
    "reference" or polarity — those are properties of the surrounding
    circuit, decided by which input the reference voltage is wired to.
    """

    __slots__ = ['_ports']

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'v_plus':  Port('v_plus',  Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'v_minus': Port('v_minus', Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'out':     Port('out',     Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        vp = self._ports['v_plus'].value
        vm = self._ports['v_minus'].value
        if vp is None or vm is None:
            self._ports['out'].drive(None)
        else:
            self._ports['out'].drive(vp > vm)

    def __call__(self, v_plus, v_minus):
        self._ports['v_plus'].drive(v_plus)
        self._ports['v_minus'].drive(v_minus)
        self._evaluate()
        return self._ports['out'].value

    def __str__(self) -> str:
        return f"LM393({self._ports['v_plus'].value} > {self._ports['v_minus'].value})"

    def __repr__(self) -> str:
        return "LM393()"
