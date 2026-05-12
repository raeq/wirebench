from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('DRV8313')
class DRV8313(Chip):
    """Texas Instruments DRV8313 — three-channel brushless-DC pre-driver
    with integrated half-bridge power stages (HTSSOP-28, PWP package).

    Three independent half-bridges (phase A / B / C) share a common
    motor supply (VM) and charge-pump-derived gate-drive rail.  Each
    half-bridge accepts two logic inputs (INx_1 = low-side, INx_2 =
    high-side) plus a per-phase ENable that idles the bridge when low.
    Six-step BLDC commutation lives entirely in the controlling MCU's
    firmware: it reads the Hall pattern, looks up which two phases to
    drive, and asserts the corresponding three IN-pins + enables.

    The chip is modelled as a black box: protection (overcurrent,
    thermal, undervoltage) is on-die behaviour with no useful steady-
    state surface in a voltage-only graph, and the gate-drive bootstrap
    capacitors at BST1..BST3 are charge-pumped without an external
    Vcc-to-gate supply rail.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'GND',      Direction.IN,  Analog),
        ( 2, 'VM',       Direction.IN,  Analog),    # motor supply
        ( 3, 'CP1',      Direction.IN,  Analog),    # charge-pump flying cap
        ( 4, 'CP2',      Direction.IN,  Analog),
        ( 5, 'VCP',      Direction.OUT, Analog),    # charge-pump output
        ( 6, 'GVDD',     Direction.OUT, Analog),    # gate-drive supply
        ( 7, 'V3P3OUT',  Direction.OUT, Analog),    # 3.3 V LDO out
        ( 8, 'nSLEEP',   Direction.IN,  Digital),   # device sleep (active LOW)
        ( 9, 'nRESET',   Direction.IN,  Digital),   # reset (active LOW)
        (10, 'nFAULT',   Direction.OUT, Digital),   # fault flag (open-drain)
        (11, 'EN1',      Direction.IN,  Digital),   # phase-A enable
        (12, 'IN1',      Direction.IN,  Digital),   # phase-A low-side input
        (13, 'IN2',      Direction.IN,  Digital),   # phase-A high-side input
        (14, 'EN2',      Direction.IN,  Digital),   # phase-B enable
        (15, 'IN3',      Direction.IN,  Digital),   # phase-B low-side input
        (16, 'IN4',      Direction.IN,  Digital),   # phase-B high-side input
        (17, 'EN3',      Direction.IN,  Digital),   # phase-C enable
        (18, 'IN5',      Direction.IN,  Digital),   # phase-C low-side input
        (19, 'IN6',      Direction.IN,  Digital),   # phase-C high-side input
        (20, 'BST1',     Direction.IN,  Analog),    # phase-A bootstrap cap
        (21, 'OUT1',     Direction.OUT, Analog),    # phase-A motor output
        (22, 'BST2',     Direction.IN,  Analog),    # phase-B bootstrap cap
        (23, 'OUT2',     Direction.OUT, Analog),
        (24, 'BST3',     Direction.IN,  Analog),    # phase-C bootstrap cap
        (25, 'OUT3',     Direction.OUT, Analog),
        (26, 'PGND',     Direction.IN,  Analog),    # power ground
        (27, 'PGND',     Direction.IN,  Analog),
        (28, 'PPAD',     Direction.IN,  Analog),    # thermal pad / GND
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
        """Black-box package — no behavioural model.  The surrounding
        BLDCControllerBoard exposes the commutation logic separately."""
        return None

    def __repr__(self) -> str:
        return f"DRV8313(refdes={self.refdes!r})"
