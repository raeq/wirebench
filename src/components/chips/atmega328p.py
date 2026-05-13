from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ATmega328P')
class ATmega328P(Chip):
    """Microchip ATmega328P — 8-bit AVR microcontroller, 32 KB flash (PDIP-28).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_DIP:DIP-28_W7.62mm'

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Put a 100 nF capacitor at each supply pin, leads under 5 mm "
        "long.** The ATmega328P has two supply pins (VCC and AVCC, "
        "the analogue Vcc) and each needs its own cap to ground. "
        "Without these caps the chip glitches under load and ADC "
        "readings drift. For clean ADC readings, also wire AVCC to "
        "VCC through a small ferrite bead or 10 Ω resistor, with a "
        "10 µF cap on the AVCC side — this isolates the analogue "
        "supply from digital switching noise.",
        "**Add a 10 kΩ resistor from RESET (pin 1) to the + rail.** "
        "Without that pull-up, RESET drifts LOW and the chip resets "
        "itself in a loop. Add a 100 nF cap from RESET to ground too "
        "— it makes RESET noise-immune, and Arduino-style serial "
        "bootloaders also use that cap to auto-reset the board for "
        "uploads.",
        "**Don't try to use PC6 (pin 1) as a normal I/O pin** unless "
        "you have a high-voltage programmer (HVPP). PC6 doubles as "
        "the RESET pin; freeing it as I/O requires setting the "
        "RSTDISBL fuse, which permanently disables the standard ISP "
        "programming interface. If you ever need to update the "
        "firmware after that, your only path is HVPP — which most "
        "hobbyists don't have. Hardly worth it for one extra I/O pin.",
        "**'Fuse' settings persist across power cycles and aren't "
        "visible in your program.** They're a separate set of "
        "configuration bytes that control things like clock source, "
        "brown-out detection, and bootloader behaviour. New chips "
        "ship configured for the internal 8 MHz oscillator divided "
        "by 8 (so 1 MHz effective) — if you wired an external "
        "crystal but didn't update the CKSEL fuses, your code still "
        "runs from the internal oscillator and timing is wrong. "
        "Worse: setting CKSEL to 'external crystal' without one "
        "actually wired up bricks the chip until you apply an "
        "external clock via HVPP.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'PC6',          Direction.BIDIR,  Digital),
        (  2, 'PD0',          Direction.BIDIR,  Digital),
        (  3, 'PD1',          Direction.BIDIR,  Digital),
        (  4, 'PD2',          Direction.BIDIR,  Digital),
        (  5, 'PD3',          Direction.BIDIR,  Digital),
        (  6, 'PD4',          Direction.BIDIR,  Digital),
        (  7, 'VCC',          Direction.IN,     Analog),
        (  8, 'GND',        Direction.IN,     Analog),
        (  9, 'PB6',          Direction.BIDIR,  Digital),
        ( 10, 'PB7',          Direction.BIDIR,  Digital),
        ( 11, 'PD5',          Direction.BIDIR,  Digital),
        ( 12, 'PD6',          Direction.BIDIR,  Digital),
        ( 13, 'PD7',          Direction.BIDIR,  Digital),
        ( 14, 'PB0',          Direction.BIDIR,  Digital),
        ( 15, 'PB1',          Direction.BIDIR,  Digital),
        ( 16, 'PB2',          Direction.BIDIR,  Digital),
        ( 17, 'PB3',          Direction.BIDIR,  Digital),
        ( 18, 'PB4',          Direction.BIDIR,  Digital),
        ( 19, 'PB5',          Direction.BIDIR,  Digital),
        ( 20, 'AVCC',         Direction.IN,     Analog),
        ( 21, 'AREF',         Direction.IN,     Analog),
        ( 22, 'GND',        Direction.IN,     Analog),
        ( 23, 'PC0',          Direction.BIDIR,  Digital),
        ( 24, 'PC1',          Direction.BIDIR,  Digital),
        ( 25, 'PC2',          Direction.BIDIR,  Digital),
        ( 26, 'PC3',          Direction.BIDIR,  Digital),
        ( 27, 'PC4',          Direction.BIDIR,  Digital),
        ( 28, 'PC5',          Direction.BIDIR,  Digital),
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
        return f"ATmega328P(refdes={self.refdes!r})"
