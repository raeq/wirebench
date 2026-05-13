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


@register('SN74HC595')
class SN74HC595(Chip):
    """Texas Instruments SN74HC595 — 8-bit serial-in/parallel-out shift register with output latch (DIP-16).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. All unused CMOS inputs must always be tied to VCC or GND.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'QB'      , Direction.OUT, Digital),
        ( 2, 'QC'      , Direction.OUT, Digital),
        ( 3, 'QD'      , Direction.OUT, Digital),
        ( 4, 'QE'      , Direction.OUT, Digital),
        ( 5, 'QF'      , Direction.OUT, Digital),
        ( 6, 'QG'      , Direction.OUT, Digital),
        ( 7, 'QH'      , Direction.OUT, Digital),
        ( 8, 'GND'     , Direction.IN , Analog),
        ( 9, 'QH_PRIME', Direction.OUT, Digital),
        (10, 'SRCLR'   , Direction.IN , Digital),
        (11, 'SRCLK'   , Direction.IN , Digital),
        (12, 'RCLK'    , Direction.IN , Digital),
        (13, 'OE'      , Direction.IN , Digital),
        (14, 'SER'     , Direction.IN , Digital),
        (15, 'QA'      , Direction.OUT, Digital),
        (16, 'VCC'     , Direction.IN , Analog),
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
        # Behavioural placeholder: every OUT pin gets an `IdleDriver`
        # so the framework's logical-net walker sees a real driver on
        # each output net. Demos that need protocol-accurate behaviour
        # substitute a SPICE .SUBCKT or cycle-accurate emulator.
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
        """Black-box package — no behavioural model. Pin states are
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"SN74HC595(refdes={self.refdes!r})"
