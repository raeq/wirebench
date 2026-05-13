from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ATmega32U4')
class ATmega32U4(Chip):
    """Microchip ATmega32U4 — 8-bit AVR microcontroller with USB device, 32 KB flash (TQFP-44).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_QFP:TQFP-44_10x10mm_P0.8mm'

    # Category C — application-firmware-driven (per
    # the behavioural-cell audit policy): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'PE6',          Direction.BIDIR,  Digital),
        (  2, 'UVCC',         Direction.IN,     Analog),
        (  3, 'D_NEG',           Direction.BIDIR,  Analog),
        (  4, 'D_POS',           Direction.BIDIR,  Analog),
        (  5, 'UGND',         Direction.IN,     Analog),
        (  6, 'UCAP',         Direction.IN,     Analog),
        (  7, 'VBUS',         Direction.IN,     Analog),
        (  8, 'PB0',          Direction.BIDIR,  Digital),
        (  9, 'PB1',          Direction.BIDIR,  Digital),
        ( 10, 'PB2',          Direction.BIDIR,  Digital),
        ( 11, 'PB3',          Direction.BIDIR,  Digital),
        ( 12, 'PB7',          Direction.BIDIR,  Digital),
        ( 13, 'RESET',        Direction.IN,     Digital),
        ( 14, 'VCC',        Direction.IN,     Analog),
        ( 15, 'GND',        Direction.IN,     Analog),
        ( 16, 'XTAL2',        Direction.BIDIR,  Analog),
        ( 17, 'XTAL1',        Direction.BIDIR,  Analog),
        ( 18, 'PD0',          Direction.BIDIR,  Digital),
        ( 19, 'PD1',          Direction.BIDIR,  Digital),
        ( 20, 'PD2',          Direction.BIDIR,  Digital),
        ( 21, 'PD3',          Direction.BIDIR,  Digital),
        ( 22, 'PD5',          Direction.BIDIR,  Digital),
        ( 23, 'GND',        Direction.IN,     Analog),
        ( 24, 'VCC',        Direction.IN,     Analog),
        ( 25, 'PD4',          Direction.BIDIR,  Digital),
        ( 26, 'PD6',          Direction.BIDIR,  Digital),
        ( 27, 'PD7',          Direction.BIDIR,  Digital),
        ( 28, 'PB4',          Direction.BIDIR,  Digital),
        ( 29, 'PB5',          Direction.BIDIR,  Digital),
        ( 30, 'PB6',          Direction.BIDIR,  Digital),
        ( 31, 'PC6',          Direction.BIDIR,  Digital),
        ( 32, 'PC7',          Direction.BIDIR,  Digital),
        ( 33, 'PE2',          Direction.BIDIR,  Digital),
        ( 34, 'VCC',        Direction.IN,     Analog),
        ( 35, 'GND',        Direction.IN,     Analog),
        ( 36, 'PF7',          Direction.BIDIR,  Digital),
        ( 37, 'PF6',          Direction.BIDIR,  Digital),
        ( 38, 'PF5',          Direction.BIDIR,  Digital),
        ( 39, 'PF4',          Direction.BIDIR,  Digital),
        ( 40, 'PF1',          Direction.BIDIR,  Digital),
        ( 41, 'PF0',          Direction.BIDIR,  Digital),
        ( 42, 'AREF',         Direction.IN,     Analog),
        ( 43, 'GND',        Direction.IN,     Analog),
        ( 44, 'AVCC',         Direction.IN,     Analog),
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
        observable via `chip.ports['<name>'].value`."""
        return None

    def __repr__(self) -> str:
        return f"ATmega32U4(refdes={self.refdes!r})"
