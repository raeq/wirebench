from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class Inverter(FactorNode):
    """A single NOT gate cell. Pin a is input, pin y is output: y = NOT(a).

    This is a logic-level building block — chips like the SN74HC04 (hex
    buffered inverter) and CD4069UB (hex unbuffered inverter) are
    packages of these cells.  The cell itself doesn't model buffered
    vs. unbuffered behaviour; that's a chip-level concern.
    """

    __slots__ = ('_ports',)

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'a': Port('a', Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'y': Port('y', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        v = self._ports['a'].value
        self._ports['y'].drive(None if v is None else not v)

    def __call__(self, a: bool | None) -> bool | None:
        self._assert_no_inputs_wired()
        self._ports['a'].drive(a)
        self.evaluate()
        result: bool | None = self._ports['y'].value
        return result

    def __repr__(self) -> str:
        return f"Inverter(y={self._ports['y'].value!r})"
