from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('AMS1117_50')
class AMS1117_50(Chip):
    """AMS1117-5.0 — fixed +5V 1A LDO regulator (SOT-223).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. The tab (pin 4) is electrically
    OUTPUT and exposed here as a distinct port `OUTPUT_TAB` because
    `PinId` requires unique pin numbers but the port name must also be
    unique. For behavioural simulation, supply a generic LDO model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_SMD:SOT-223-3_TabPin2"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'GND',        Direction.IN,  Analog),
        (2, 'OUTPUT',     Direction.OUT, Analog),
        (3, 'INPUT',      Direction.IN,  Analog),
        (4, 'OUTPUT_TAB', Direction.OUT, Analog),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        """Black-box package — no behavioural model. Pin states are
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"AMS1117_50(refdes={self.refdes!r})"
