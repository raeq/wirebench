from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class Inverter(FactorNode):
    """Single-channel logic inverter (NOT gate). Pin A is input, Y is output."""

    __slots__ = ['_ports']

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'a': Port('a', Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'y': Port('y', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        v = self._ports['a'].value
        self._ports['y'].drive(None if v is None else not v)

    def __call__(self, a: bool | None) -> bool | None:
        self._ports['a'].drive(a)
        self._evaluate()
        return self._ports['y'].value

    def __str__(self) -> str:
        return f"NOT({self._ports['a'].value})"

    def __repr__(self) -> str:
        return f"Inverter(y={self._ports['y'].value!r})"
