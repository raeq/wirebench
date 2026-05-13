from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ESP8266_12F')
class ESP8266_12F(Chip):
    """Ai-Thinker ESP-12F — Wi-Fi SMD module with ESP8266EX, 4 MB flash (22-pad).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'RF_Module:ESP-12E'

    # Category C — application-firmware-driven (per
    # the behavioural-cell audit policy): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'RST',          Direction.IN,     Digital),
        (  2, 'ADC',          Direction.IN,     Analog),
        (  3, 'EN',           Direction.IN,     Digital),
        (  4, 'GPIO16',       Direction.BIDIR,  Digital),
        (  5, 'GPIO14',       Direction.BIDIR,  Digital),
        (  6, 'GPIO12',       Direction.BIDIR,  Digital),
        (  7, 'GPIO13',       Direction.BIDIR,  Digital),
        (  8, 'VCC',          Direction.IN,     Analog),
        (  9, 'CS0',          Direction.BIDIR,  Digital),
        ( 10, 'MISO',         Direction.BIDIR,  Digital),
        ( 11, 'GPIO0',        Direction.BIDIR,  Digital),
        ( 12, 'MOSI',         Direction.BIDIR,  Digital),
        ( 13, 'SCLK',         Direction.BIDIR,  Digital),
        ( 14, 'GND',          Direction.IN,     Analog),
        ( 15, 'GPIO10',       Direction.BIDIR,  Digital),
        ( 16, 'GPIO9',        Direction.BIDIR,  Digital),
        ( 17, 'GPIO11',       Direction.BIDIR,  Digital),
        ( 18, 'GPIO6',        Direction.BIDIR,  Digital),
        ( 19, 'GPIO7',        Direction.BIDIR,  Digital),
        ( 20, 'GPIO8',        Direction.BIDIR,  Digital),
        ( 21, 'RXD',          Direction.BIDIR,  Digital),
        ( 22, 'TXD',          Direction.BIDIR,  Digital),
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
        return f"ESP8266_12F(refdes={self.refdes!r})"
