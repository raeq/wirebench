from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('SN74HC541')
class SN74HC541(Chip):
    """Texas Instruments SN74HC541 — octal buffer/line driver with 3-state outputs (DIP-20).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. All unused CMOS inputs must always be tied to VCC or GND.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-20_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'OE1', Direction.IN , Digital),
        ( 2, 'A1' , Direction.IN , Digital),
        ( 3, 'A2' , Direction.IN , Digital),
        ( 4, 'A3' , Direction.IN , Digital),
        ( 5, 'A4' , Direction.IN , Digital),
        ( 6, 'A5' , Direction.IN , Digital),
        ( 7, 'A6' , Direction.IN , Digital),
        ( 8, 'A7' , Direction.IN , Digital),
        ( 9, 'A8' , Direction.IN , Digital),
        (10, 'GND', Direction.IN , Analog),
        (11, 'Y8' , Direction.OUT, Digital),
        (12, 'Y7' , Direction.OUT, Digital),
        (13, 'Y6' , Direction.OUT, Digital),
        (14, 'Y5' , Direction.OUT, Digital),
        (15, 'Y4' , Direction.OUT, Digital),
        (16, 'Y3' , Direction.OUT, Digital),
        (17, 'Y2' , Direction.OUT, Digital),
        (18, 'Y1' , Direction.OUT, Digital),
        (19, 'OE2', Direction.IN , Digital),
        (20, 'VCC', Direction.IN , Analog),
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
        return f"SN74HC541(refdes={self.refdes!r})"
