from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('LM339')
class LM339(Chip):
    """Texas Instruments LM339 — quad open-collector differential comparator (PDIP-14).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. Open-collector outputs require an external pull-up.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-14_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1,  'OUT2', Direction.OUT, Analog),
        (2,  'OUT1', Direction.OUT, Analog),
        (3,  'VCC',  Direction.IN,  Analog),
        (4,  'IN1_NEG', Direction.IN,  Analog),
        (5,  'IN1_POS', Direction.IN,  Analog),
        (6,  'IN2_NEG', Direction.IN,  Analog),
        (7,  'IN2_POS', Direction.IN,  Analog),
        (8,  'IN3_NEG', Direction.IN,  Analog),
        (9,  'IN3_POS', Direction.IN,  Analog),
        (10, 'IN4_NEG', Direction.IN,  Analog),
        (11, 'IN4_POS', Direction.IN,  Analog),
        (12, 'GND',  Direction.IN,  Analog),
        (13, 'OUT4', Direction.OUT, Analog),
        (14, 'OUT3', Direction.OUT, Analog),
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
        return f"LM339(refdes={self.refdes!r})"
