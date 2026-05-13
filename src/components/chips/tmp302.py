from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from .concepts._helpers import wire_idle_drivers


@register('TMP302')
class TMP302(Chip):
    """Texas Instruments TMP302 — low-power resistor-programmable
    temperature switch in a 6-pin SOT-563 micropackage (DSE).

    Black-box package model; the trip-point behaviour is application-
    level (set by `TripSet0` / `TripSet1` resistor / strap inputs) and
    is modelled at the composite level rather than here.  The `OUT`
    pin is an open-drain active-LOW indicator: pulled LOW above the
    trip temperature, pulled HIGH (via an external pull-up) when in
    spec.

    Supply range is 1.4 V – 3.6 V (per datasheet); use an external
    series resistor and zener if the board rail is higher than 3.6 V.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:SOT-563_1.6x1.6mm_P0.5mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'TripSet0', Direction.IN,  Digital),    # trip-point bit 0
        (2, 'GND',      Direction.IN,  Analog),
        (3, 'OUT',      Direction.OUT, Digital),    # open-drain active LOW
        (4, 'HysSet',   Direction.IN,  Digital),    # hysteresis select
        (5, 'VS',       Direction.IN,  Analog),     # 1.4 – 3.6 V supply
        (6, 'TripSet1', Direction.IN,  Digital),    # trip-point bit 1
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
        drivers = wire_idle_drivers(pins, domain)
        super().__init__(pins=pins, cells=drivers)

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        """Black-box package — no behavioural model."""
        return None

    def __repr__(self) -> str:
        return f"TMP302(refdes={self.refdes!r})"
