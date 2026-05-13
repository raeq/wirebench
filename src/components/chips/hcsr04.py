from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.idle_driver import IdleDriver


@register('HCSR04')
class HCSR04(Chip):
    """HC-SR04 — ultrasonic ranging breakout module (4-pin SIP, 2.54 mm).

    ECHO is the chip's response to a trigger pulse — its width
    encodes the distance.  The framework can't model that pulse-
    width-encoded timing, so the OUT pin is driven by an
    `IdleDriver` (LOW idle).  Demos that need echo behaviour
    prescribe the value via Python state before evaluation, or run
    SPICE for accurate timing.  5 V part — divide ECHO for 3.3 V
    MCUs.  Min trigger pulse 10 µs; ≥60 ms between measurements.
    """

    __slots__ = ('_refdes_number', '_echo_drv')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'VCC',  Direction.IN,  Analog),
        (2, 'TRIG', Direction.IN,  Digital),
        (3, 'ECHO', Direction.OUT, Digital),
        (4, 'GND',  Direction.IN,  Analog),
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
        self._echo_drv = IdleDriver(Digital, idle_value=False, domain=domain)
        by_name = {pin.id.name: pin for pin in pins}
        wire(self._echo_drv.ports['out'], by_name['ECHO'].internal)
        super().__init__(pins=pins, cells=[self._echo_drv])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        """Black-box package — no behavioural model. Pin states are
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"HCSR04(refdes={self.refdes!r})"
