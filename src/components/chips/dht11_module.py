from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('DHT11_Module')
class DHT11_Module(Chip):
    """Aosong DHT11 breakout module — small PCB carrying a bare DHT11
    sensor plus a fitted pull-up resistor, exposed as a 3-pin header.

    Common silkscreen variants label the pins `+ / S / -`, `VCC / DAT
    / GND`, or `VCC / OUT / GND`; the underlying signal mapping is the
    same.  We use VCC / DATA / GND as the framework names.

    The on-board pull-up makes this module slightly different from the
    bare 4-pin sensor — there's no NC pin and no external resistor to
    add on DATA.  See `DHT11` for the bare sensor model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    # Generic 3-pin SIP — the module's PCB outline isn't a standard
    # KiCad footprint, but the pin row is a 3-pin 0.1" header.  The
    # assembly-guide exporter only uses FOOTPRINT to choose between
    # DIP and SIP rendering; flag the package as TO-style THT so the
    # SIP renderer kicks in.
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:DHT11_Module"

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
        "**The module already has its DATA pull-up on board.** Don't "
        "add another external resistor — two pull-ups in parallel "
        "stiffen the line and can drag the edges out of spec for "
        "the DHT11's bit-banged protocol.  The bare 4-pin sensor "
        "(see DHT11) does need an external 5 kΩ pull-up; the module "
        "does not.",
        "**The DHT11's protocol is timing-sensitive, and the standard "
        "library reads disable interrupts for ~25 ms.** If your sketch "
        "also runs PWM, software-serial, or an interrupt-driven task, "
        "the DHT11 read can disrupt those. On RTOS-class boards "
        "(ESP32, RP2040 under MicroPython) prefer the BME280 — its "
        "I²C protocol is interrupt-friendly.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'VCC',  Direction.IN,    Analog),
        (2, 'DATA', Direction.BIDIR, Digital),
        (3, 'GND',  Direction.IN,    Analog),
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
        return f"DHT11_Module(refdes={self.refdes!r})"
