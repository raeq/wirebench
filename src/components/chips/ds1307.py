from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('DS1307')
class DS1307(Chip):
    """Analog Devices (Maxim) DS1307 — I²C real-time clock with 56-byte
    NV RAM (DIP-8).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. Requires a 32.768 kHz crystal between X1/X2; SDA/SCL require
    external pull-ups; SQW/OUT is open-drain.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-8_W7.62mm"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**A 32.768 kHz watch crystal across X1/X2 is mandatory.** No "
        "external load caps — the DS1307 has them on-die. Any other "
        "crystal (a 32 kHz oscillator can, a different load capacitance) "
        "either won't start or runs at the wrong rate. Keep the crystal "
        "leads under 1 cm and surround it with a grounded guard ring on "
        "PCBs; long traces let it pick up noise.",
        "**Battery on Vbat (pin 3) keeps time across power-off.** A "
        "CR2032 coin cell is standard; expect ~7 years of timekeeping. "
        "Reversing the battery puts +3 V on what was meant to be ground "
        "and destroys the chip — coin-cell holders' orientation is "
        "easy to confuse on a fresh build.",
        "**Square-wave output (pin 7) is open-drain.** Needs a pull-up "
        "to Vcc; without one the SQW pin reads floating. Useful for "
        "interrupt-driven 1 Hz timing without polling the registers.",
        "**I²C address is fixed at 0x68.** No address pins — only one "
        "DS1307 per bus. If you need multiple, use an I²C mux (TCA9548A) "
        "or a part with addressable pins (PCF8523, DS3231 + 0x68 alone).",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'X1',      Direction.IN,    Analog),
        (2, 'X2',      Direction.OUT,   Analog),
        (3, 'VBAT',    Direction.IN,    Analog),
        (4, 'GND',     Direction.IN,    Analog),
        (5, 'SDA',     Direction.BIDIR, Digital),
        (6, 'SCL',     Direction.IN,    Digital),
        (7, 'SQW_OUT', Direction.OUT,   Digital),
        (8, 'VCC',     Direction.IN,    Analog),
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
        return f"DS1307(refdes={self.refdes!r})"
