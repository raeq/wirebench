"""Locked breadboard SVG palette.

Two reserved colours (red = current, black = ground) and two cycling
palettes (analog and digital signal jumpers) per spec §5. The two
reserved colours are off-limits to the signal palettes so a hobbyist
reading the board can always parse red-as-power and black-as-ground at
a glance.

Each signal net is assigned a colour by its ordinal position in a
deterministic sort of all nets of that kind — adjacent nets along the
board get adjacent palette indices, so two physically-adjacent jumpers
only end up the same colour at palette-wrap distance (every 4 nets,
not at random based on hash collision).
"""
from __future__ import annotations


# --------------------------------------------------------- reserved colours

# Current (+ rail and any jumper carrying + to a passive).
RAIL_PLUS_LINE: str   = '#cc0000'
RAIL_PLUS_JUMPER: str = '#cc0000'

# Ground (− rail and any jumper carrying − to a passive).
RAIL_MINUS_LINE: str   = '#6cb4e4'   # light blue, distinct from jumper black
RAIL_MINUS_JUMPER: str = '#000000'


# --------------------------------------------------------- signal palettes

# Analog: warm / earth tones. Visually separable from the digital
# palette's cool / saturated tones so the breadboard at a glance
# reveals the analog vs digital topology of the design.
ANALOG_PALETTE: tuple[str, ...] = (
    '#e07a17',   # orange
    '#d4a017',   # yellow / amber
    '#8b5a2b',   # brown
    '#9acd32',   # light green
)

# Digital: cool / saturated tones. The spec listed 'white' as the
# fourth digital colour but pure white sits invisibly on the cream
# board surface; we substitute a saturated magenta-pink so the fourth
# digital is genuinely distinguishable from the other three. The
# magenta is also separable from any analog-palette tone so the
# analog-vs-digital scan remains intact.
DIGITAL_PALETTE: tuple[str, ...] = (
    '#2a6dbf',   # blue
    '#7c3aed',   # purple
    '#1f6e3a',   # dark green
    '#c0317a',   # magenta-pink (substituted for unreadable 'white')
)


def analog_color(ordinal: int) -> str:
    """Pick a colour from the analog palette by ordinal position. Same
    ordinal always returns the same colour."""
    return ANALOG_PALETTE[ordinal % len(ANALOG_PALETTE)]


def digital_color(ordinal: int) -> str:
    """Pick a colour from the digital palette by ordinal position. Same
    ordinal always returns the same colour."""
    return DIGITAL_PALETTE[ordinal % len(DIGITAL_PALETTE)]


# --------------------------------------------------------- surface colours

# Breadboard surface: slight cream card.
BOARD_BACKGROUND: str = '#fffaf0'
BOARD_BORDER:     str = '#888888'

# Tie-point holes drawn as small dark circles on the board surface.
TIE_POINT:        str = '#666666'

# Chip / passive body fills.
CHIP_BODY:        str = '#222222'
CHIP_LABEL:       str = '#ffffff'
PASSIVE_BODY:     str = '#e8d7a8'    # tan, hobbyist-recognisable resistor body
PASSIVE_LABEL:    str = '#222222'
LED_BODY_RED:     str = '#cc3333'
LED_BODY_GREEN:   str = '#33aa33'
LED_BODY_BLUE:    str = '#3366cc'
LED_BODY_YELLOW:  str = '#ddcc33'
LED_BODY_DEFAULT: str = '#dd9933'
CAP_BODY:         str = '#a0a0c8'
DIODE_BODY:       str = '#333333'
DIODE_LABEL:      str = '#ffffff'

# Connector body — distinct from chips to read as a header strip.
CONNECTOR_BODY:   str = '#404040'
CONNECTOR_LABEL:  str = '#ffffff'


def led_body_color(color_name: str) -> str:
    """Map a wirebench LED.color string to a body fill colour. Unknown
    colour names fall back to the default amber."""
    return {
        'red':    LED_BODY_RED,
        'green':  LED_BODY_GREEN,
        'blue':   LED_BODY_BLUE,
        'yellow': LED_BODY_YELLOW,
    }.get(color_name.lower(), LED_BODY_DEFAULT)
