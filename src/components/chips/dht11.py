from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('DHT11')
class DHT11(Chip):
    """Aosong DHT11 — single-bus humidity and temperature sensor (4-pin
    plastic housing).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. DATA is a proprietary single-bus
    protocol (40-bit serial frames at ~1 ms granularity) that is not
    simulable in a voltage-only steady-state graph. For behavioural
    simulation, substitute a vendor model. DATA needs an external
    pull-up (typically 5 kΩ to VDD) in real circuits.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:DHT11"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Don't poll faster than once per second.** The DHT11's "
        "internal sample rate is ~1 Hz; reading more often returns "
        "stale data and stresses the sensor's self-heating budget "
        "(which already biases the temperature reading by ~1°C). "
        "Schedule reads on a 1-second timer, not in your main loop.",
        "**Accuracy is mediocre by design.** ±2°C and ±5% RH are typical; "
        "the chip is a teaching-grade humidity sensor, not an "
        "instrument. For real measurement use a SHT3x / BME280 — "
        "double the cost, ten times the accuracy.",
        "**One-wire protocol is bit-banged with tight timing.** Many "
        "Arduino libraries disable interrupts during reads (~25 ms). "
        "If you're running PWM, software-serial, or an OS, the DHT11 "
        "read can corrupt other timing-sensitive operations.",
        "**4-pin TO-92-ish package: V+, DATA, NC, GND** from the screen "
        "side (the side with the metal grille). The NC pin really is "
        "no-connect; some tutorials show a pull-up resistor on it — "
        "that's wrong, the pull-up goes on DATA.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'VDD',  Direction.IN,    Analog),
        (2, 'DATA', Direction.BIDIR, Digital),
        (3, 'NC',   Direction.IN,    Digital),
        (4, 'GND',  Direction.IN,    Analog),
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
        observable via `chip.ports['<name>'].value`. The single-bus
        protocol on DATA is out of scope for a voltage-only graph."""
        return None

    def __repr__(self) -> str:
        return f"DHT11(refdes={self.refdes!r})"
