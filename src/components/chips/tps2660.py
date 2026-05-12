from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('TPS2660')
class TPS2660(Chip):
    """Texas Instruments TPS2660 — 4.2-to-60-V, 150-mΩ industrial
    eFuse with reverse-polarity protection and a 0.1- to 2.2-A
    programmable current limit (10-pin WSON, DGN).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated.  Behavioural protection
    (overload / overvoltage / undervoltage / reverse polarity) is
    handled at the composite level — for the TIDA-03031 backup-supply
    demo, the BackupSupervisor cell reads VIN and toggles FLT_B
    according to the same fault thresholds.

    Pin 7 (FLT_B) is open-drain active-low; expect a pull-up to the
    monitoring rail in the surrounding design.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SON:WSON-10-1EP_3x3mm_P0.5mm_EP1.6x2.4mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'SETI',   Direction.IN,    Analog),    # current-limit set
        ( 2, 'IMON',   Direction.OUT,   Analog),    # current-monitor output
        ( 3, 'OV',     Direction.IN,    Analog),    # overvoltage adjust
        ( 4, 'UV',     Direction.IN,    Analog),    # undervoltage adjust
        ( 5, 'dVdT',   Direction.IN,    Analog),    # output slew-rate set
        ( 6, 'EN',     Direction.IN,    Digital),   # device enable
        ( 7, 'FLT_B',  Direction.OUT,   Digital),   # active-low fault (open-drain)
        ( 8, 'GND',    Direction.IN,    Analog),
        ( 9, 'OUT',    Direction.OUT,   Analog),    # protected output
        (10, 'IN',     Direction.IN,    Analog),    # supply input
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
        """Black-box package — no behavioural model.  Pin states are
        observable via `chip.ports['<name>'].value`."""
        return None

    def __repr__(self) -> str:
        return f"TPS2660(refdes={self.refdes!r})"
