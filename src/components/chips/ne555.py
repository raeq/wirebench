from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


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
        "**Bypass the supply close to the chip.** The 555's output stage "
        "draws an instantaneous current spike — without a 100 nF (or 100 µF "
        "+ 100 nF) cap right at pin 8, you get supply ringing that "
        "couples back into other circuits sharing the rail. A misbehaving "
        "555 oscillator with weird timing usually has poor decoupling.",
        "**Control voltage (pin 5) needs a 10 nF cap to ground** even when "
        "you're not using it. The internal voltage-divider node is high-"
        "impedance and picks up noise that modulates the comparator "
        "thresholds — your stable oscillator becomes a jittery one.",
        "**Bipolar NE555 vs CMOS variants (TLC555, ICM7555).** Use a CMOS "
        "555 for low-current battery work (~100 µA supply vs the bipolar "
        "part's 3–10 mA) and for clean output edges. Bipolar parts can "
        "source/sink ~200 mA directly — handy for driving small loads "
        "but rough on the supply rail.",
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
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"NE555(refdes={self.refdes!r})"
