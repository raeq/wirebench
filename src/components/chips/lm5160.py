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


@register('LM5160')
class LM5160(Chip):
    """Texas Instruments LM5160 — 65-V, 2-A synchronous step-down
    (Fly-Buck capable) converter with integrated high- and low-side
    MOSFETs and constant-on-time control (16-pin HTSSOP, PWP).

    Black-box package model.  In TIDA-03031 the LM5160 is fed by the
    48-V bulk hold-up capacitor (charged by the LM5002 boost) and
    regulates the system bus to 17 V during a power-fail event.  Under
    normal operation the input rail already sits above the regulation
    target so switching is disabled; the constant-on-time loop kicks
    in only after VIN drops below the 19 V buck UVLO threshold.

    The 17-V regulation point and 19-V falling UVLO are selected by
    the FB and EN/UVLO resistor dividers in the reference design.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'RT',     Direction.IN,    Analog),   # frequency-set resistor
        ( 2, 'FB',     Direction.IN,    Analog),   # output-feedback divider
        ( 3, 'SS',     Direction.IN,    Analog),   # soft-start
        ( 4, 'AGND',   Direction.IN,    Analog),
        ( 5, 'NC1',    Direction.IN,    Analog),
        ( 6, 'FPWM',   Direction.IN,    Digital),  # CCM-forced / auto-DCM select
        ( 7, 'UVLO',   Direction.IN,    Analog),   # EN / input-undervoltage adjust
        ( 8, 'VCC',    Direction.OUT,   Analog),   # internal LDO output
        ( 9, 'SW',     Direction.OUT,   Analog),   # switch node (high-side / low-side junction)
        (10, 'SW',     Direction.OUT,   Analog),
        (11, 'PGND',   Direction.IN,    Analog),
        (12, 'PGND',   Direction.IN,    Analog),
        (13, 'BST',    Direction.IN,    Analog),   # bootstrap capacitor
        (14, 'VIN',    Direction.IN,    Analog),
        (15, 'VIN',    Direction.IN,    Analog),
        (16, 'NC2',    Direction.IN,    Analog),
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
        """Black-box package — no behavioural model."""
        return None

    def __repr__(self) -> str:
        return f"LM5160(refdes={self.refdes!r})"
