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


@register('TLC5940')
class TLC5940(Chip):
    """Texas Instruments TLC5940 — 16-channel constant-current sink LED driver (DIP-28).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-28_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1,  'OUT1',  Direction.OUT, Digital),
        (2,  'OUT0',  Direction.OUT, Digital),
        (3,  'VPRG',  Direction.IN,  Digital),
        (4,  'SIN',   Direction.IN,  Digital),
        (5,  'SCLK',  Direction.IN,  Digital),
        (6,  'XLAT',  Direction.IN,  Digital),
        (7,  'BLANK', Direction.IN,  Digital),
        (8,  'GND',   Direction.IN,  Analog),
        (9,  'VCC',   Direction.IN,  Analog),
        (10, 'IREF',  Direction.IN,  Analog),
        (11, 'DCPRG', Direction.IN,  Digital),
        (12, 'GSCLK', Direction.IN,  Digital),
        (13, 'SOUT',  Direction.OUT, Digital),
        (14, 'XERR',  Direction.OUT, Digital),
        (15, 'OUT15', Direction.OUT, Digital),
        (16, 'OUT14', Direction.OUT, Digital),
        (17, 'OUT13', Direction.OUT, Digital),
        (18, 'OUT12', Direction.OUT, Digital),
        (19, 'OUT11', Direction.OUT, Digital),
        (20, 'OUT10', Direction.OUT, Digital),
        (21, 'OUT9',  Direction.OUT, Digital),
        (22, 'OUT8',  Direction.OUT, Digital),
        (23, 'OUT7',  Direction.OUT, Digital),
        (24, 'OUT6',  Direction.OUT, Digital),
        (25, 'OUT5',  Direction.OUT, Digital),
        (26, 'OUT4',  Direction.OUT, Digital),
        (27, 'OUT3',  Direction.OUT, Digital),
        (28, 'OUT2',  Direction.OUT, Digital),
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
        return f"TLC5940(refdes={self.refdes!r})"
