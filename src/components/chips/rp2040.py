from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('RP2040')
class RP2040(Chip):
    """Raspberry Pi RP2040 — dual ARM Cortex-M0+ microcontroller, 264 KB SRAM (QFN-56).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'

    # Category C — application-firmware-driven (per
    # the behavioural-cell audit policy): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'IOVDD',      Direction.IN,     Analog),
        (  2, 'GP0',          Direction.BIDIR,  Digital),
        (  3, 'GP1',          Direction.BIDIR,  Digital),
        (  4, 'GP2',          Direction.BIDIR,  Digital),
        (  5, 'GP3',          Direction.BIDIR,  Digital),
        (  6, 'GP4',          Direction.BIDIR,  Digital),
        (  7, 'GP5',          Direction.BIDIR,  Digital),
        (  8, 'GP6',          Direction.BIDIR,  Digital),
        (  9, 'GP7',          Direction.BIDIR,  Digital),
        ( 10, 'IOVDD',      Direction.IN,     Analog),
        ( 11, 'GP8',          Direction.BIDIR,  Digital),
        ( 12, 'GP9',          Direction.BIDIR,  Digital),
        ( 13, 'GP10',         Direction.BIDIR,  Digital),
        ( 14, 'GP11',         Direction.BIDIR,  Digital),
        ( 15, 'GP12',         Direction.BIDIR,  Digital),
        ( 16, 'GP13',         Direction.BIDIR,  Digital),
        ( 17, 'GP14',         Direction.BIDIR,  Digital),
        ( 18, 'GP15',         Direction.BIDIR,  Digital),
        ( 19, 'TESTEN',       Direction.IN,     Digital),
        ( 20, 'XIN',          Direction.BIDIR,  Analog),
        ( 21, 'XOUT',         Direction.BIDIR,  Analog),
        ( 22, 'IOVDD',      Direction.IN,     Analog),
        ( 23, 'DVDD',       Direction.IN,     Analog),
        ( 24, 'SWCLK',        Direction.BIDIR,  Digital),
        ( 25, 'SWDIO',        Direction.BIDIR,  Digital),
        ( 26, 'RUN',          Direction.IN,     Digital),
        ( 27, 'GP16',         Direction.BIDIR,  Digital),
        ( 28, 'GP17',         Direction.BIDIR,  Digital),
        ( 29, 'GP18',         Direction.BIDIR,  Digital),
        ( 30, 'GP19',         Direction.BIDIR,  Digital),
        ( 31, 'GP20',         Direction.BIDIR,  Digital),
        ( 32, 'GP21',         Direction.BIDIR,  Digital),
        ( 33, 'IOVDD',      Direction.IN,     Analog),
        ( 34, 'GP22',         Direction.BIDIR,  Digital),
        ( 35, 'GP23',         Direction.BIDIR,  Digital),
        ( 36, 'GP24',         Direction.BIDIR,  Digital),
        ( 37, 'GP25',         Direction.BIDIR,  Digital),
        ( 38, 'GP26',         Direction.BIDIR,  Digital),
        ( 39, 'GP27',         Direction.BIDIR,  Digital),
        ( 40, 'GP28',         Direction.BIDIR,  Digital),
        ( 41, 'GP29',         Direction.BIDIR,  Digital),
        ( 42, 'IOVDD',      Direction.IN,     Analog),
        ( 43, 'ADC_AVDD',     Direction.IN,     Analog),
        ( 44, 'VREG_VIN',     Direction.IN,     Analog),
        ( 45, 'VREG_VOUT',    Direction.OUT,    Analog),
        ( 46, 'USB_DM',       Direction.BIDIR,  Analog),
        ( 47, 'USB_DP',       Direction.BIDIR,  Analog),
        ( 48, 'USB_VDD',      Direction.IN,     Analog),
        ( 49, 'IOVDD',      Direction.IN,     Analog),
        ( 50, 'DVDD',       Direction.IN,     Analog),
        ( 51, 'QSPI_SD3',     Direction.BIDIR,  Digital),
        ( 52, 'QSPI_SCLK',    Direction.BIDIR,  Digital),
        ( 53, 'QSPI_SD0',     Direction.BIDIR,  Digital),
        ( 54, 'QSPI_SD2',     Direction.BIDIR,  Digital),
        ( 55, 'QSPI_SD1',     Direction.BIDIR,  Digital),
        ( 56, 'QSPI_SS_N',    Direction.BIDIR,  Digital),
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
        return f"RP2040(refdes={self.refdes!r})"
