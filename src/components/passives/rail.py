from typing import ClassVar

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital
from framework.registry import register


@register('Rail')
class Rail(Part):
    """Constant logic rail.  Drives `out` to a fixed level (HIGH or LOW).

    Use to tie unused CMOS inputs to Vcc or GND — leaving them floating
    is forbidden in real hardware.

        gnd = Rail(False)                       # GND tie (Digital pins)
        vcc = Rail(True)                        # Vcc tie (Digital pins)
        avcc = Rail(True, signal_type=Analog)   # supply for Analog pins
        wire(gnd.ports['out'], chip.ports['unused_in'])

    The default `signal_type=Digital` matches how rails are used in
    pure-logic designs (CMOS tie-offs, sense inputs).  Some chips
    declare their power pins as `Analog` (sensors, op-amps); to wire
    those, instantiate with `signal_type=Analog`.  Physically there's
    one breadboard rail per polarity — the framework distinction is
    only for the simulator's port-type compatibility check.
    """

    __slots__ = ('_level', '_ports')

    # Rail isn't a placeable part — it's a logical marker that tells
    # exporters this net is power/ground. No footprint; not on the BOM.
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'out': 1}

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, level: bool, domain: GroundDomain = ELECTRICAL,
                 *, signal_type: type = Digital) -> None:
        self._level = bool(level)
        self._ports = {
            'out': Port('out', Direction.OUT, domain,
                        mandatory=False, signal_type=signal_type),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def level(self) -> bool:
        return self._level

    def evaluate(self) -> None:
        self._ports['out'].drive(self._level)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> bool:
        self.evaluate()
        return self._level

    def __repr__(self) -> str:
        return f"Rail({'HIGH' if self._level else 'LOW'})"
