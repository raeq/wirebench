from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('SN74AHC1G14')
class SN74AHC1G14(Chip):
    """Texas Instruments SN74AHC1G14 — single Schmitt-trigger inverter
    in SOT-23-5 (DBV package).

    Black-box package model.  Where a behavioural inverter is needed,
    a parent circuit can wire a `components.chips.concepts.inverter.Inverter`
    cell in parallel with this chip on the same net (same trick the
    dice demo uses for the wired-OR diode matrix).
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_SMD:SOT-23-5"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'A',   Direction.IN,    Digital),
        (2, 'GND', Direction.IN,    Analog),
        (3, 'Y',   Direction.OUT,   Digital),
        (4, 'NC',  Direction.IN,    Digital),
        (5, 'VCC', Direction.IN,    Analog),
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
        """Black-box package — no behavioural model."""
        return None

    def __repr__(self) -> str:
        return f"SN74AHC1G14(refdes={self.refdes!r})"
