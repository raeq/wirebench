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
        "**Decouple every Vcc pin separately.** The ATmega328P has VCC "
        "and AVCC (analogue Vcc) — both need a 100 nF cap to their "
        "respective ground pin, leads under 5 mm. AVCC should be tied "
        "to VCC through a ferrite bead or 10 Ω resistor with its own "
        "100 nF + 10 µF on the chip side; without that, ADC readings "
        "pick up digital switching noise.",
        "**RESET pin must be pulled high.** A 10 kΩ pull-up from RESET "
        "(pin 1) to Vcc is mandatory — floating RESET drifts low and "
        "the chip cycles. Add a 100 nF cap from RESET to ground for noise "
        "immunity (an auto-reset arrangement for serial bootloaders also "
        "uses this capacitor).",
        "**Fuse settings persist across power cycles** and aren't visible "
        "in the program. The chip ships with the internal 8 MHz RC "
        "oscillator divided by 8 (so 1 MHz effective). If you wired an "
        "external crystal but forgot to update CKSEL fuses, the chip "
        "still runs from the internal oscillator and your timing is "
        "wrong. Worse: setting CKSEL to external crystal without one "
        "wired up bricks the chip until you apply an external clock "
        "via HVPP.",
        "**Don't drive RESET as an I/O.** PC6 doubles as the RESET pin "
        "but using it for I/O requires setting the RSTDISBL fuse — which "
        "disables ISP programming permanently. Only do this with HVPP "
        "available as a recovery path.",
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
