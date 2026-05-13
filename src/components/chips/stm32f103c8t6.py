from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('STM32F103C8T6')
class STM32F103C8T6(Chip):
    """STMicroelectronics STM32F103C8T6 — ARM Cortex-M3 microcontroller, 64 KB flash (LQFP-48).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_QFP:LQFP-48_7x7mm_P0.5mm'

    # Category C — application-firmware-driven (per
    # docs/behavioural-cell-audit-spec.md §7.3): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'VBAT',         Direction.IN,     Analog),
        (  2, 'PC13',         Direction.BIDIR,  Digital),
        (  3, 'PC14',         Direction.BIDIR,  Digital),
        (  4, 'PC15',         Direction.BIDIR,  Digital),
        (  5, 'PD0',          Direction.BIDIR,  Digital),
        (  6, 'PD1',          Direction.BIDIR,  Digital),
        (  7, 'NRST',         Direction.IN,     Digital),
        (  8, 'VSSA',         Direction.IN,     Analog),
        (  9, 'VDDA',         Direction.IN,     Analog),
        ( 10, 'PA0',          Direction.BIDIR,  Digital),
        ( 11, 'PA1',          Direction.BIDIR,  Digital),
        ( 12, 'PA2',          Direction.BIDIR,  Digital),
        ( 13, 'PA3',          Direction.BIDIR,  Digital),
        ( 14, 'PA4',          Direction.BIDIR,  Digital),
        ( 15, 'PA5',          Direction.BIDIR,  Digital),
        ( 16, 'PA6',          Direction.BIDIR,  Digital),
        ( 17, 'PA7',          Direction.BIDIR,  Digital),
        ( 18, 'PB0',          Direction.BIDIR,  Digital),
        ( 19, 'PB1',          Direction.BIDIR,  Digital),
        ( 20, 'VSS',        Direction.IN,     Analog),
        ( 21, 'VDD',        Direction.IN,     Analog),
        ( 22, 'PB2',          Direction.BIDIR,  Digital),
        ( 23, 'PB10',         Direction.BIDIR,  Digital),
        ( 24, 'PB11',         Direction.BIDIR,  Digital),
        ( 25, 'VSS',        Direction.IN,     Analog),
        ( 26, 'VDD',        Direction.IN,     Analog),
        ( 27, 'PB12',         Direction.BIDIR,  Digital),
        ( 28, 'PB13',         Direction.BIDIR,  Digital),
        ( 29, 'PB14',         Direction.BIDIR,  Digital),
        ( 30, 'PB15',         Direction.BIDIR,  Digital),
        ( 31, 'PA8',          Direction.BIDIR,  Digital),
        ( 32, 'PA9',          Direction.BIDIR,  Digital),
        ( 33, 'PA10',         Direction.BIDIR,  Digital),
        ( 34, 'PA11',         Direction.BIDIR,  Analog),
        ( 35, 'PA12',         Direction.BIDIR,  Analog),
        ( 36, 'PA13',         Direction.BIDIR,  Digital),
        ( 37, 'VSS',        Direction.IN,     Analog),
        ( 38, 'VDD',        Direction.IN,     Analog),
        ( 39, 'PA14',         Direction.BIDIR,  Digital),
        ( 40, 'PA15',         Direction.BIDIR,  Digital),
        ( 41, 'PB3',          Direction.BIDIR,  Digital),
        ( 42, 'PB4',          Direction.BIDIR,  Digital),
        ( 43, 'PB5',          Direction.BIDIR,  Digital),
        ( 44, 'PB6',          Direction.BIDIR,  Digital),
        ( 45, 'PB7',          Direction.BIDIR,  Digital),
        ( 46, 'BOOT0',        Direction.IN,     Digital),
        ( 47, 'PB8',          Direction.BIDIR,  Digital),
        ( 48, 'PB9',          Direction.BIDIR,  Digital),
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
        return f"STM32F103C8T6(refdes={self.refdes!r})"
