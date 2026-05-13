from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ATmega2560')
class ATmega2560(Chip):
    """Microchip ATmega2560 — 8-bit AVR microcontroller, 256 KB flash (TQFP-100).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_QFP:TQFP-100_14x14mm_P0.5mm'

    # Category C — application-firmware-driven (per
    # docs/behavioural-cell-audit-spec.md §7.3): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'PG5',          Direction.BIDIR,  Digital),
        (  2, 'PE0',          Direction.BIDIR,  Digital),
        (  3, 'PE1',          Direction.BIDIR,  Digital),
        (  4, 'PE2',          Direction.BIDIR,  Digital),
        (  5, 'PE3',          Direction.BIDIR,  Digital),
        (  6, 'PE4',          Direction.BIDIR,  Digital),
        (  7, 'PE5',          Direction.BIDIR,  Digital),
        (  8, 'PE6',          Direction.BIDIR,  Digital),
        (  9, 'PE7',          Direction.BIDIR,  Digital),
        ( 10, 'VCC',        Direction.IN,     Analog),
        ( 11, 'GND',        Direction.IN,     Analog),
        ( 12, 'PH0',          Direction.BIDIR,  Digital),
        ( 13, 'PH1',          Direction.BIDIR,  Digital),
        ( 14, 'PH2',          Direction.BIDIR,  Digital),
        ( 15, 'PH3',          Direction.BIDIR,  Digital),
        ( 16, 'PH4',          Direction.BIDIR,  Digital),
        ( 17, 'PH5',          Direction.BIDIR,  Digital),
        ( 18, 'PH6',          Direction.BIDIR,  Digital),
        ( 19, 'PB0',          Direction.BIDIR,  Digital),
        ( 20, 'PB1',          Direction.BIDIR,  Digital),
        ( 21, 'PB2',          Direction.BIDIR,  Digital),
        ( 22, 'PB3',          Direction.BIDIR,  Digital),
        ( 23, 'PB4',          Direction.BIDIR,  Digital),
        ( 24, 'PB5',          Direction.BIDIR,  Digital),
        ( 25, 'PB6',          Direction.BIDIR,  Digital),
        ( 26, 'PB7',          Direction.BIDIR,  Digital),
        ( 27, 'PH7',          Direction.BIDIR,  Digital),
        ( 28, 'PG3',          Direction.BIDIR,  Digital),
        ( 29, 'PG4',          Direction.BIDIR,  Digital),
        ( 30, 'RESET',        Direction.IN,     Digital),
        ( 31, 'VCC',        Direction.IN,     Analog),
        ( 32, 'GND',        Direction.IN,     Analog),
        ( 33, 'XTAL2',        Direction.BIDIR,  Analog),
        ( 34, 'XTAL1',        Direction.BIDIR,  Analog),
        ( 35, 'PL0',          Direction.BIDIR,  Digital),
        ( 36, 'PL1',          Direction.BIDIR,  Digital),
        ( 37, 'PL2',          Direction.BIDIR,  Digital),
        ( 38, 'PL3',          Direction.BIDIR,  Digital),
        ( 39, 'PL4',          Direction.BIDIR,  Digital),
        ( 40, 'PL5',          Direction.BIDIR,  Digital),
        ( 41, 'PL6',          Direction.BIDIR,  Digital),
        ( 42, 'PL7',          Direction.BIDIR,  Digital),
        ( 43, 'PD0',          Direction.BIDIR,  Digital),
        ( 44, 'PD1',          Direction.BIDIR,  Digital),
        ( 45, 'PD2',          Direction.BIDIR,  Digital),
        ( 46, 'PD3',          Direction.BIDIR,  Digital),
        ( 47, 'PD4',          Direction.BIDIR,  Digital),
        ( 48, 'PD5',          Direction.BIDIR,  Digital),
        ( 49, 'PD6',          Direction.BIDIR,  Digital),
        ( 50, 'PD7',          Direction.BIDIR,  Digital),
        ( 51, 'PG0',          Direction.BIDIR,  Digital),
        ( 52, 'PG1',          Direction.BIDIR,  Digital),
        ( 53, 'PC0',          Direction.BIDIR,  Digital),
        ( 54, 'PC1',          Direction.BIDIR,  Digital),
        ( 55, 'PC2',          Direction.BIDIR,  Digital),
        ( 56, 'PC3',          Direction.BIDIR,  Digital),
        ( 57, 'PC4',          Direction.BIDIR,  Digital),
        ( 58, 'PC5',          Direction.BIDIR,  Digital),
        ( 59, 'PC6',          Direction.BIDIR,  Digital),
        ( 60, 'PC7',          Direction.BIDIR,  Digital),
        ( 61, 'VCC',        Direction.IN,     Analog),
        ( 62, 'GND',        Direction.IN,     Analog),
        ( 63, 'PJ0',          Direction.BIDIR,  Digital),
        ( 64, 'PJ1',          Direction.BIDIR,  Digital),
        ( 65, 'PJ2',          Direction.BIDIR,  Digital),
        ( 66, 'PJ3',          Direction.BIDIR,  Digital),
        ( 67, 'PJ4',          Direction.BIDIR,  Digital),
        ( 68, 'PJ5',          Direction.BIDIR,  Digital),
        ( 69, 'PJ6',          Direction.BIDIR,  Digital),
        ( 70, 'PG2',          Direction.BIDIR,  Digital),
        ( 71, 'PA7',          Direction.BIDIR,  Digital),
        ( 72, 'PA6',          Direction.BIDIR,  Digital),
        ( 73, 'PA5',          Direction.BIDIR,  Digital),
        ( 74, 'PA4',          Direction.BIDIR,  Digital),
        ( 75, 'PA3',          Direction.BIDIR,  Digital),
        ( 76, 'PA2',          Direction.BIDIR,  Digital),
        ( 77, 'PA1',          Direction.BIDIR,  Digital),
        ( 78, 'PA0',          Direction.BIDIR,  Digital),
        ( 79, 'PJ7',          Direction.BIDIR,  Digital),
        ( 80, 'VCC',        Direction.IN,     Analog),
        ( 81, 'GND',        Direction.IN,     Analog),
        ( 82, 'PK7',          Direction.BIDIR,  Digital),
        ( 83, 'PK6',          Direction.BIDIR,  Digital),
        ( 84, 'PK5',          Direction.BIDIR,  Digital),
        ( 85, 'PK4',          Direction.BIDIR,  Digital),
        ( 86, 'PK3',          Direction.BIDIR,  Digital),
        ( 87, 'PK2',          Direction.BIDIR,  Digital),
        ( 88, 'PK1',          Direction.BIDIR,  Digital),
        ( 89, 'PK0',          Direction.BIDIR,  Digital),
        ( 90, 'PF7',          Direction.BIDIR,  Digital),
        ( 91, 'PF6',          Direction.BIDIR,  Digital),
        ( 92, 'PF5',          Direction.BIDIR,  Digital),
        ( 93, 'PF4',          Direction.BIDIR,  Digital),
        ( 94, 'PF3',          Direction.BIDIR,  Digital),
        ( 95, 'PF2',          Direction.BIDIR,  Digital),
        ( 96, 'PF1',          Direction.BIDIR,  Digital),
        ( 97, 'PF0',          Direction.BIDIR,  Digital),
        ( 98, 'AREF',         Direction.IN,     Analog),
        ( 99, 'GND',        Direction.IN,     Analog),
        (100, 'AVCC',         Direction.IN,     Analog),
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
        return f"ATmega2560(refdes={self.refdes!r})"
