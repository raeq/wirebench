from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('MAX7219')
class MAX7219(Chip):
    """Analog Devices (Maxim) MAX7219 — serial-input 8-digit common-cathode
    LED display driver (DIP-24 wide).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. Peak segment current set by R_SET between ISET and V+.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-24_W15.24mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'DIN',    Direction.IN,  Digital),
        ( 2, 'DIG_0',  Direction.OUT, Digital),
        ( 3, 'DIG_4',  Direction.OUT, Digital),
        ( 4, 'GND',    Direction.IN,  Analog),
        ( 5, 'DIG_6',  Direction.OUT, Digital),
        ( 6, 'DIG_2',  Direction.OUT, Digital),
        ( 7, 'DIG_3',  Direction.OUT, Digital),
        ( 8, 'DIG_7',  Direction.OUT, Digital),
        ( 9, 'GND',    Direction.IN,  Analog),
        (10, 'DIG_5',  Direction.OUT, Digital),
        (11, 'DIG_1',  Direction.OUT, Digital),
        (12, 'LOAD',   Direction.IN,  Digital),
        (13, 'CLK',    Direction.IN,  Digital),
        (14, 'SEG_A',  Direction.OUT, Digital),
        (15, 'SEG_F',  Direction.OUT, Digital),
        (16, 'SEG_B',  Direction.OUT, Digital),
        (17, 'SEG_G',  Direction.OUT, Digital),
        (18, 'ISET',   Direction.IN,  Analog),
        (19, 'V_POS',     Direction.IN,  Analog),
        (20, 'SEG_C',  Direction.OUT, Digital),
        (21, 'SEG_E',  Direction.OUT, Digital),
        (22, 'SEG_DP', Direction.OUT, Digital),
        (23, 'SEG_D',  Direction.OUT, Digital),
        (24, 'DOUT',   Direction.OUT, Digital),
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
        return f"MAX7219(refdes={self.refdes!r})"
