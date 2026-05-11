from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('MAX232')
class MAX232(Chip):
    """Texas Instruments MAX232 — dual RS-232 driver/receiver with charge-pump (DIP-16).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. Charge-pump capacitor pins (C1+, C1-, C2+, C2-) and rail
    outputs (V+, V-) are analog; TTL-side ports are Digital; RS-232-side
    ports are Analog (±10 V swing).
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1,  'C1_POS',   Direction.IN,  Analog),
        (2,  'V_POS',    Direction.OUT, Analog),
        (3,  'C1_NEG',   Direction.IN,  Analog),
        (4,  'C2_POS',   Direction.IN,  Analog),
        (5,  'C2_NEG',   Direction.IN,  Analog),
        (6,  'V_NEG',    Direction.OUT, Analog),
        (7,  'T2OUT', Direction.OUT, Analog),
        (8,  'R2IN',  Direction.IN,  Analog),
        (9,  'R2OUT', Direction.OUT, Digital),
        (10, 'T2IN',  Direction.IN,  Digital),
        (11, 'T1IN',  Direction.IN,  Digital),
        (12, 'R1OUT', Direction.OUT, Digital),
        (13, 'R1IN',  Direction.IN,  Analog),
        (14, 'T1OUT', Direction.OUT, Analog),
        (15, 'GND',   Direction.IN,  Analog),
        (16, 'VCC',   Direction.IN,  Analog),
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
        return f"MAX232(refdes={self.refdes!r})"
