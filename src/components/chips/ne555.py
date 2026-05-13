from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from .concepts._helpers import wire_idle_drivers


@register('NE555')
class NE555(Chip):
    """Texas Instruments NE555 — precision astable/monostable timer (DIP-8).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-8_W7.62mm"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Put a capacitor across the supply pins, right at the chip.** "
        "A 100 nF ceramic from pin 8 (Vcc) to pin 1 (GND), leads under "
        "5 mm long. The 555 draws a sharp current spike every time its "
        "output switches, and without a local cap the supply rail rings "
        "— making the oscillator's timing drift and coupling noise into "
        "anything else sharing the supply. If your 555 oscillator runs "
        "at the wrong frequency or jitters, this is the first thing "
        "to check.",
        "**Add a 10 nF cap from pin 5 to ground**, even if you're not "
        "using pin 5 for anything. Pin 5 (Control Voltage) is "
        "internally connected to the chip's reference divider, and "
        "without that little cap the pin acts as an antenna for nearby "
        "noise — your steady oscillator turns into a jittery one for "
        "no obvious reason. (The pin's high-impedance node picks up "
        "stray fields and modulates the comparator thresholds; the cap "
        "shorts that noise to ground.)",
        "**For battery-powered work, use a CMOS 555 instead** — the "
        "TLC555 or ICM7555 are drop-in replacements that draw "
        "~100 µA versus the original NE555's 3–10 mA. Same pinout, "
        "same external circuit, ten to a hundred times the battery "
        "life. The classic bipolar NE555 has one advantage: its "
        "output can drive ~200 mA directly into a load — useful for "
        "small lamps or relays at the cost of rougher supply behaviour.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'GND',   Direction.IN,    Analog),
        (2, 'TRIG',  Direction.IN,    Digital),
        (3, 'OUT',   Direction.OUT,   Digital),
        (4, 'RESET', Direction.IN,    Digital),
        (5, 'CONT',  Direction.BIDIR, Digital),
        (6, 'THRES', Direction.IN,    Digital),
        (7, 'DISCH', Direction.OUT,   Digital),
        (8, 'VCC',   Direction.IN,    Analog),
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
        # Behavioural placeholder: every OUT pin gets an `IdleDriver`
        # so the framework's logical-net walker sees a real driver on
        # each output net. Demos that need protocol-accurate behaviour
        # substitute a SPICE .SUBCKT or cycle-accurate emulator.
        drivers = wire_idle_drivers(pins, domain)
        super().__init__(pins=pins, cells=drivers)

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
        return f"NE555(refdes={self.refdes!r})"
