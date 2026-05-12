from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('LM5002')
class LM5002(Chip):
    """Texas Instruments LM5002 — 3.1- to 75-V wide-Vin, 0.5-A
    current-mode boost / SEPIC / flyback / forward switching regulator
    with an integrated 75-V N-channel MOSFET (8-pin VSSOP, DGK).

    Black-box package model.  In TIDA-03031 the LM5002 is wired as a
    discontinuous-mode (DCM) boost converter that charges the bulk
    holdup capacitor to 48 V; the TPS2660 FLT_B signal disables it
    during a brown-out.  Time-domain switching is not simulable in a
    voltage-only graph, so the surrounding BackupSupervisor cell
    models the charge dynamics instead.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:VSSOP-8_3.0x3.0mm_P0.65mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'VCC',  Direction.IN,  Analog),   # supply / bias
        (2, 'RT',   Direction.IN,  Analog),   # switching-frequency programming
        (3, 'SS',   Direction.IN,  Analog),   # soft-start
        (4, 'FB',   Direction.IN,  Analog),   # feedback comparator input
        (5, 'COMP', Direction.IN,  Analog),   # loop-compensation node
        (6, 'ISEN', Direction.IN,  Analog),   # current-sense input
        (7, 'GND',  Direction.IN,  Analog),
        (8, 'SW',   Direction.OUT, Analog),   # integrated FET switching node
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
        return f"LM5002(refdes={self.refdes!r})"
