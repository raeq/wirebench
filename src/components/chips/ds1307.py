from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from .concepts._helpers import wire_idle_drivers


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
    # I²C SDA is open-drain by protocol (the docstring above already
    # calls out that SDA/SCL need external pull-ups).  SCL is
    # Direction.IN on this slave-only chip, so it has no drive type.
    # SQW/OUT is also open-drain (pin 7) — datasheet section 7.4.
    PIN_DRIVE_TYPES: ClassVar[dict[str, "DriveType"]] = {
        'SDA':     DriveType.OPEN_DRAIN,
        'SQW_OUT': DriveType.OPEN_DRAIN,
    }

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Solder a 32.768 kHz watch crystal directly between pins 1 "
        "and 2 — and don't add load capacitors.** The DS1307 has the "
        "load caps built in; adding external ones changes the load "
        "capacitance and the crystal either won't start or runs at "
        "the wrong rate. Keep the crystal's leads short (under 1 cm) "
        "and away from anything switching fast; on PCBs surround it "
        "with a grounded copper guard.",
        "**Wire a CR2032 coin-cell battery to Vbat (pin 3) so the "
        "clock keeps time when power is off.** Expect ~7 years on one "
        "cell. Coin-cell holders are easy to confuse — check polarity "
        "with a multimeter before pushing the cell in. Reverse it and "
        "+3 V lands on what was supposed to be ground, instantly "
        "destroying the chip.",
        "**Wire the SQW pin (pin 7) up through a pull-up resistor if "
        "you want a square-wave output.** SQW is open-drain — it can "
        "only pull LOW; a 10 kΩ pull-up to Vcc gives it something to "
        "drive against. SQW set to 1 Hz makes a handy interrupt input "
        "for clocks that need an exact tick without polling the I²C "
        "registers.",
        "**You can only have one DS1307 on a single I²C bus.** The "
        "chip's address (0x68) is fixed in silicon — no address pins "
        "to change it. If your design needs two clocks on the same "
        "I²C bus, use an I²C multiplexer (TCA9548A) between them, or "
        "switch to a part with selectable addresses (PCF8523).",
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
        return f"DS1307(refdes={self.refdes!r})"
