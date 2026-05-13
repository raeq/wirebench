from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Digital
from framework.wire import wire
from framework.registry import register
from .concepts.segment_matrix import SegmentMatrix


# Glyph table: frozenset of segment names that are lit for each
# recognised character.  Anything not in the table renders as '?'.
# Segment order: a (top), b (top-right), c (bottom-right), d (bottom),
# e (bottom-left), f (top-left), g (middle), dp (decimal point).
_GLYPHS: dict[frozenset[str], str] = {
    frozenset({'a', 'b', 'c', 'd', 'e', 'f'}):           '0',
    frozenset({'b', 'c'}):                               '1',
    frozenset({'a', 'b', 'd', 'e', 'g'}):                '2',
    frozenset({'a', 'b', 'c', 'd', 'g'}):                '3',
    frozenset({'b', 'c', 'f', 'g'}):                     '4',
    frozenset({'a', 'c', 'd', 'f', 'g'}):                '5',
    frozenset({'a', 'c', 'd', 'e', 'f', 'g'}):           '6',
    frozenset({'a', 'b', 'c'}):                          '7',
    frozenset({'a', 'b', 'c', 'd', 'e', 'f', 'g'}):      '8',
    frozenset({'a', 'b', 'c', 'd', 'f', 'g'}):           '9',
    frozenset({'a', 'd', 'e', 'f'}):                     'C',
    frozenset({'g'}):                                    '-',
    frozenset():                                         ' ',
}

_SEGMENT_NAMES = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp')


@register('Display5641AS')
class Display5641AS(Chip):
    """5641AS — 4-digit common-anode 7-segment LED display module
    (0.56" digits, 12-pin DIP-like single-row package).

    The four digits share segment cathodes (a..g, dp); each digit has a
    private anode common (DIG_1..DIG_4).  Driving DIG_n HIGH and any
    SEG_x LOW lights the corresponding segment on digit n.  Real
    hardware uses multiplexing — only one DIG_n HIGH at a time, scanned
    fast enough that the eye sees all digits — and a series resistor
    per segment (or per common) to limit current.

    The chip composes a single internal SegmentMatrix cell that maps
    pin signals to a 4×8 lit-pattern matrix.  Use `glyphs` to read back
    a tuple of characters (one per digit), or `glyph(digit_index)` for a
    single digit.
    """

    __slots__ = ('_matrix', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Display_7Segment:Display_5641AS"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**This is the common-cathode version: pull a digit's cathode "
        "LOW to enable it, and drive segments HIGH to light them.** "
        "If you accidentally bought the 5641AH (common-anode), the "
        "polarity is reversed and code written for one will light all "
        "the wrong digits in the other. Check the part number on the "
        "device label before wiring.",
        "**One current-limit resistor per segment, never one shared "
        "across segments.** Use ~330 Ω on each of the seven segment "
        "lines for a 5 V supply. Sharing a single resistor sounds "
        "frugal but the brightness changes with the digit's content "
        "— a '1' (two segments lit) glows twice as bright as a '8' "
        "(seven segments) because each segment gets half the current "
        "when shared with a partner.",
        "**The MCU drives one digit at a time, very quickly, and your "
        "eye fuses them into one image.** The firmware loop is: "
        "enable digit 0 → drive its segment pattern → 1 ms later "
        "enable digit 1 → drive that pattern → ... and so on, cycling "
        "through all four digits about 100 times a second. Refresh "
        "slower than ~50 Hz and you see visible flicker; faster than "
        "~200 Hz needs care with timer interrupts.",
        "**The digit's common pin can sink a lot of current — too much "
        "for an MCU to handle directly.** When all seven segments are "
        "on, ~70 mA flows through one digit's cathode pin (7 × 10 mA). "
        "Most MCU pins are rated for only ~20 mA. Put an NPN transistor "
        "or a low-side MOSFET between each digit's common pin and "
        "ground, and switch *that* with the MCU; never wire a digit "
        "common straight into a logic pin.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'SEG_E',  Direction.IN, Digital),
        ( 2, 'SEG_D',  Direction.IN, Digital),
        ( 3, 'SEG_DP', Direction.IN, Digital),
        ( 4, 'SEG_C',  Direction.IN, Digital),
        ( 5, 'SEG_G',  Direction.IN, Digital),
        ( 6, 'DIG_4',  Direction.IN, Digital),
        ( 7, 'SEG_B',  Direction.IN, Digital),
        ( 8, 'DIG_3',  Direction.IN, Digital),
        ( 9, 'DIG_2',  Direction.IN, Digital),
        (10, 'SEG_F',  Direction.IN, Digital),
        (11, 'SEG_A',  Direction.IN, Digital),
        (12, 'DIG_1',  Direction.IN, Digital),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._matrix = SegmentMatrix(domain)

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        # Wire each pin's internal face to the matching matrix input.
        # Pin signal names ('DIG_1', 'SEG_A') → matrix cell port names
        # ('dig_1', 'seg_a'): same identifier, lowercased.
        for pin_name, pin in by_name.items():
            wire(pin.internal, self._matrix.ports[pin_name.lower()])

        super().__init__(pins=pins, cells=[self._matrix])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def lit_matrix(self) -> tuple[tuple[bool | None, ...], ...]:
        """Row-major lit pattern: [digit_index][segment_index]."""
        return self._matrix.lit_matrix

    def glyph(self, digit_index: int) -> str:
        """Decode the lit pattern of digit `digit_index` (0..3) into a
        character, or '?' if the pattern isn't a recognised glyph.  A
        digit with no lit segments returns ' ' (blank)."""
        if not 0 <= digit_index < self._matrix.DIGITS:
            raise IndexError(
                f"digit_index {digit_index} out of range 0..{self._matrix.DIGITS - 1}"
            )
        row = self.lit_matrix[digit_index]
        lit = frozenset(name for name, on in zip(_SEGMENT_NAMES, row) if on)
        return _GLYPHS.get(lit, '?')

    @property
    def glyphs(self) -> tuple[str, str, str, str]:
        """Characters currently shown on digits 1..4."""
        return tuple(self.glyph(i) for i in range(self._matrix.DIGITS))  # type: ignore[return-value]

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self,
                 DIG_1: bool | None = False, DIG_2: bool | None = False,
                 DIG_3: bool | None = False, DIG_4: bool | None = False,
                 SEG_A: bool | None = True,  SEG_B: bool | None = True,
                 SEG_C: bool | None = True,  SEG_D: bool | None = True,
                 SEG_E: bool | None = True,  SEG_F: bool | None = True,
                 SEG_G: bool | None = True,  SEG_DP: bool | None = True,
                 ) -> tuple[str, str, str, str]:
        self._assert_no_inputs_wired()
        drives = {
            'DIG_1': DIG_1, 'DIG_2': DIG_2, 'DIG_3': DIG_3, 'DIG_4': DIG_4,
            'SEG_A': SEG_A, 'SEG_B': SEG_B, 'SEG_C': SEG_C, 'SEG_D': SEG_D,
            'SEG_E': SEG_E, 'SEG_F': SEG_F, 'SEG_G': SEG_G, 'SEG_DP': SEG_DP,
        }
        for name, value in drives.items():
            self._ports[name].drive(value)
        self.evaluate()
        return self.glyphs

    def __repr__(self) -> str:
        return f"Display5641AS(glyphs={self.glyphs!r}, refdes={self.refdes!r})"
