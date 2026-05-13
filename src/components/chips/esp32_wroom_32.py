from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ESP32_WROOM_32')
class ESP32_WROOM_32(Chip):
    """Espressif ESP32-WROOM-32 — Wi-Fi + Bluetooth SMD module with ESP32-D0WDQ6, 4 MB flash (38-pad).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'RF_Module:ESP32-WROOM-32'

    # Category C — application-firmware-driven (per
    # docs/behavioural-cell-audit-spec.md §7.3): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'GND',        Direction.IN,     Analog),
        (  2, '3V3',          Direction.IN,     Analog),
        (  3, 'EN',           Direction.IN,     Digital),
        (  4, 'SENSOR_VP',    Direction.IN,     Analog),
        (  5, 'SENSOR_VN',    Direction.IN,     Analog),
        (  6, 'GPIO34',       Direction.IN,     Digital),
        (  7, 'GPIO35',       Direction.IN,     Digital),
        (  8, 'GPIO32',       Direction.BIDIR,  Digital),
        (  9, 'GPIO33',       Direction.BIDIR,  Digital),
        ( 10, 'GPIO25',       Direction.BIDIR,  Analog),
        ( 11, 'GPIO26',       Direction.BIDIR,  Analog),
        ( 12, 'GPIO27',       Direction.BIDIR,  Digital),
        ( 13, 'GPIO14',       Direction.BIDIR,  Digital),
        ( 14, 'GPIO12',       Direction.BIDIR,  Digital),
        ( 15, 'GND',        Direction.IN,     Analog),
        ( 16, 'GPIO13',       Direction.BIDIR,  Digital),
        ( 17, 'SD2',          Direction.BIDIR,  Digital),
        ( 18, 'SD3',          Direction.BIDIR,  Digital),
        ( 19, 'CMD',          Direction.BIDIR,  Digital),
        ( 20, 'CLK',          Direction.BIDIR,  Digital),
        ( 21, 'SD0',          Direction.BIDIR,  Digital),
        ( 22, 'SD1',          Direction.BIDIR,  Digital),
        ( 23, 'GPIO15',       Direction.BIDIR,  Digital),
        ( 24, 'GPIO2',        Direction.BIDIR,  Digital),
        ( 25, 'GPIO0',        Direction.BIDIR,  Digital),
        ( 26, 'GPIO4',        Direction.BIDIR,  Digital),
        ( 27, 'GPIO16',       Direction.BIDIR,  Digital),
        ( 28, 'GPIO17',       Direction.BIDIR,  Digital),
        ( 29, 'GPIO5',        Direction.BIDIR,  Digital),
        ( 30, 'GPIO18',       Direction.BIDIR,  Digital),
        ( 31, 'GPIO19',       Direction.BIDIR,  Digital),
        ( 33, 'GPIO21',       Direction.BIDIR,  Digital),
        ( 34, 'RXD0',         Direction.BIDIR,  Digital),
        ( 35, 'TXD0',         Direction.BIDIR,  Digital),
        ( 36, 'GPIO22',       Direction.BIDIR,  Digital),
        ( 37, 'GPIO23',       Direction.BIDIR,  Digital),
        ( 38, 'GND',        Direction.IN,     Analog),
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
        return f"ESP32_WROOM_32(refdes={self.refdes!r})"
