from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('ATtiny85')
class ATtiny85(Chip):
    """Microchip ATtiny85 — 8-bit AVR microcontroller, 8 KB flash (PDIP-8).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal logic is instantiated. For behavioural simulation,
    substitute a vendor-supplied IBIS or behavioural macro.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = 'Package_DIP:DIP-8_W7.62mm'

    # Category C — application-firmware-driven (per
    # docs/behavioural-cell-audit-spec.md §7.3): the MCU's OUT
    # pins are driven by user firmware, not by a deterministic
    # function of its input pins. The bare class legitimately
    # ships with `cells=[]`; users subclass and inject a
    # firmware-as-cell per the existing `Uno_ThermometerSketch`
    # / `Uno_BLDCCommutator` pattern.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**A new ATtiny85 runs at 1 MHz out of the box, not 8 MHz.** "
        "The chip ships with the internal oscillator divided by 8 "
        "(via a fuse called CKDIV8). If your Arduino sketch was "
        "compiled assuming 8 MHz but the fuse is at its default, "
        "everything will run 8× too slow — serial baud rates wrong, "
        "timers drifting, `delay(1000)` taking 8 seconds. Either set "
        "F_CPU = 1000000 in your sketch or burn the CKDIV8 fuse "
        "to disable the divider.",
        "**Only 6 I/O pins are available — plan ahead.** Software-SPI "
        "alone uses three, an ADC input uses one, an interrupt input "
        "uses one, and a PWM output uses one. That's all six. The "
        "ATtiny85 is wonderfully compact but it forces you to choose "
        "between features; sketch out pin assignments on paper before "
        "wiring.",
        "**Don't reclaim pin 1 (PB5/RESET) as a GPIO unless you have "
        "an HVPP programmer.** PB5 doubles as RESET; turning it into "
        "a normal pin requires setting the RSTDISBL fuse, which "
        "permanently disables the standard ISP programming interface. "
        "From that point you can only update the firmware with a "
        "high-voltage parallel programmer — and most people don't "
        "have one. Sacrificing the ability to ever reprogram the chip "
        "is rarely worth one extra I/O pin.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (  1, 'PB5',          Direction.BIDIR,  Digital),
        (  2, 'PB3',          Direction.BIDIR,  Digital),
        (  3, 'PB4',          Direction.BIDIR,  Digital),
        (  4, 'GND',          Direction.IN,     Analog),
        (  5, 'PB0',          Direction.BIDIR,  Digital),
        (  6, 'PB1',          Direction.BIDIR,  Digital),
        (  7, 'PB2',          Direction.BIDIR,  Digital),
        (  8, 'VCC',          Direction.IN,     Analog),
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
        return f"ATtiny85(refdes={self.refdes!r})"
