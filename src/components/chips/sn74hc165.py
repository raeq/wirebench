from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('SN74HC165')
class SN74HC165(Chip):
    """Texas Instruments SN74HC165 — 8-bit parallel-load shift register (parallel-to-serial) (DIP-16).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. All unused CMOS inputs must always be tied to VCC or GND.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'SH_LD'  , Direction.IN , Digital),
        ( 2, 'CLK'    , Direction.IN , Digital),
        ( 3, 'E'      , Direction.IN , Digital),
        ( 4, 'F'      , Direction.IN , Digital),
        ( 5, 'G'      , Direction.IN , Digital),
        ( 6, 'H'      , Direction.IN , Digital),
        ( 7, 'QH_BAR' , Direction.OUT, Digital),
        ( 8, 'GND'    , Direction.IN , Analog),
        ( 9, 'QH'     , Direction.OUT, Digital),
        (10, 'SER'    , Direction.IN , Digital),
        (11, 'A'      , Direction.IN , Digital),
        (12, 'B'      , Direction.IN , Digital),
        (13, 'C'      , Direction.IN , Digital),
        (14, 'D'      , Direction.IN , Digital),
        (15, 'CLK_INH', Direction.IN , Digital),
        (16, 'VCC'    , Direction.IN , Analog),
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
        return f"SN74HC165(refdes={self.refdes!r})"
