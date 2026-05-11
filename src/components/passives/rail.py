from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital
from framework.registry import register


@register('Rail')
class Rail(FactorNode):
    """Constant logic rail.  Drives `out` to a fixed level (HIGH or LOW).

    Use to tie unused CMOS inputs to Vcc or GND — leaving them floating
    is forbidden in real hardware.

        gnd = Rail(False)            # GND tie
        vcc = Rail(True)             # Vcc tie
        wire(gnd.ports['out'], chip.ports['unused_in'])
    """

    __slots__ = ('_level', '_ports')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, level: bool, domain: GroundDomain = ELECTRICAL) -> None:
        self._level = bool(level)
        self._ports = {
            'out': Port('out', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        self._ports['out'].drive(self._level)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> bool:
        self.evaluate()
        return self._level

    def __repr__(self) -> str:
        return f"Rail({'HIGH' if self._level else 'LOW'})"
