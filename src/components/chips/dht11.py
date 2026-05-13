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
        "**Read the DHT11 at most once per second.** The sensor only "
        "updates its internal reading about that often; polling faster "
        "just gives you the same number back, while heating the chip "
        "and shifting its temperature reading by ~1°C. Put the read in "
        "a one-second timer, not in your main loop.",
        "**This is a teaching-grade sensor, not an instrument.** "
        "Expect ±2°C and ±5% relative humidity error — fine for "
        "'is the room hot or humid?' projects, useless for anything "
        "that needs real accuracy. If your build cares about precision "
        "(a weather station, an HVAC monitor), swap in a BME280 or "
        "SHT31; both cost about twice as much and are ten times more "
        "accurate.",
        "**The pin labelled NC really has nothing inside.** Looking at "
        "the side with the grille, the pins are V+, DATA, NC, GND. "
        "Some online tutorials show a pull-up resistor going to NC — "
        "that's wrong; the pull-up belongs on DATA. The NC pin should "
        "stay completely unconnected.",
        "**The DHT11's protocol is timing-sensitive, and the standard "
        "library reads disable interrupts for ~25 ms.** If your sketch "
        "also runs PWM, software-serial, or an interrupt-driven task, "
        "the DHT11 read can disrupt those. On RTOS-class boards "
        "(ESP32, RP2040 under MicroPython) prefer the BME280 — its "
        "I²C protocol is interrupt-friendly.",
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
