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
from .concepts.analog_temp_sensor import AnalogTempSensor


@register('TMP36')
class TMP36(Chip):
    """Analog Devices TMP36 — low-voltage analog temperature sensor (TO-92).

    Composes one private `AnalogTempSensor` cell that drives `VOUT`
    from a user-prescribed temperature (10 mV/°C + 0.5 V offset).
    Set `chip.temperature_c = T` (passed through to the cell) before
    `evaluate()` to read the resulting VOUT in scenarios; default
    25 °C.
    """

    __slots__ = ('_refdes_number', '_sensor')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'Vs_plus', Direction.IN,  Analog),
        (2, 'VOUT',    Direction.OUT, Analog),
        (3, 'GND',     Direction.IN,  Analog),
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
        self._sensor = AnalogTempSensor(domain=domain)
        by_name = {pin.id.name: pin for pin in pins}
        wire(self._sensor.ports['v_out'], by_name['VOUT'].internal)
        super().__init__(pins=pins, cells=[self._sensor])

    @property
    def temperature_c(self) -> float:
        return self._sensor.temperature_c

    @temperature_c.setter
    def temperature_c(self, value: float) -> None:
        self._sensor.temperature_c = value

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
        return f"TMP36(refdes={self.refdes!r})"
