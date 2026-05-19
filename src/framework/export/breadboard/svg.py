"""SVG emission utilities for the breadboard visualiser.

Pure-Python string templating — no external SVG library dependency.
Every element is written with inline styles so the output is fully
self-contained for GitHub-README / email / doc-site embed without
external stylesheet dependencies (spec §6, decision 6).

This module owns the coordinate system: positions 1..63 map to pixel
columns, rows A..J map to pixel rows, and the breadboard surface
fixtures (rails, tie-point holes, trough) are drawn relative to those.
"""
from __future__ import annotations

from dataclasses import dataclass


# --------------------------------------------------------- canvas geometry

# Full-size 63-position breadboard. Per locked decision in §12: render
# all demos onto the full-size board so positions in this SVG match the
# positions in the assembly-guide steps (acceptance criterion 8).
#
# The canvas width is grown dynamically by `canvas_width()` so designs
# whose assembly-guide placement spans more than one breadboard's worth
# of columns (Dice, DoorbellProtector) still get a faithful drawing —
# the resulting SVG is "wider than one breadboard" the way two physical
# breadboards daisy-chained at the bench would be.

NUM_POSITIONS:   int = 63
MAX_POSITIONS:   int = 252   # 4 boards' worth — hard upper bound for refusal
LEFT_MARGIN:     int = 40
RIGHT_MARGIN:    int = 40

# Above-rail / below-rail detour zones. Each jumper that uses a top
# or bottom detour band picks a y inside this zone, offset by its
# emission ordinal. Sized to fit a 16-band cycle at DETOUR_BAND_PITCH
# pixels apart — well above the 1-pixel "are these the same line?"
# threshold a hobbyist's eye can resolve.
DETOUR_BAND_PITCH:  int = 3
DETOUR_BAND_COUNT:  int = 16
DETOUR_ZONE_HEIGHT: int = DETOUR_BAND_PITCH * DETOUR_BAND_COUNT     # 48
TOP_MARGIN:      int = DETOUR_ZONE_HEIGHT + 16                       # 64
BOTTOM_MARGIN:   int = DETOUR_ZONE_HEIGHT + 20                       # 68

# Horizontal pitch between tie strips (≈ 25 px = visually generous).
POSITION_PITCH:  int = 25

# Vertical pitch within a five-hole bank.
ROW_PITCH:       int = 18

# Y coordinates for each named row / rail strip. The top rail and the
# bank rows are shifted down from the canvas top so the above-top
# detour zone has room to fan out without colliding with the rails.
Y_RAIL_TOP_PLUS:     int = TOP_MARGIN + 10                            # 74
Y_RAIL_TOP_MINUS:    int = Y_RAIL_TOP_PLUS + 20                       # 94
Y_ROW_A:             int = Y_RAIL_TOP_MINUS + 50                      # 144
Y_ROW_B: int = Y_ROW_A + ROW_PITCH       # 162
Y_ROW_C: int = Y_ROW_A + ROW_PITCH * 2   # 180
Y_ROW_D: int = Y_ROW_A + ROW_PITCH * 3   # 198
Y_ROW_E: int = Y_ROW_A + ROW_PITCH * 4   # 216

# Trough between row E and row F. Wide enough to clearly read as a gap.
TROUGH_HEIGHT: int = 22
Y_TROUGH_TOP:    int = Y_ROW_E + ROW_PITCH // 2 + 2   # 227
Y_TROUGH_BOT:    int = Y_TROUGH_TOP + TROUGH_HEIGHT   # 249

Y_ROW_F: int = Y_TROUGH_BOT + ROW_PITCH // 2 + 2      # 260
Y_ROW_G: int = Y_ROW_F + ROW_PITCH                    # 278
Y_ROW_H: int = Y_ROW_F + ROW_PITCH * 2                # 296
Y_ROW_I: int = Y_ROW_F + ROW_PITCH * 3                # 314
Y_ROW_J: int = Y_ROW_F + ROW_PITCH * 4                # 332

Y_RAIL_BOT_PLUS:  int = Y_ROW_J + 50                                  # 382
Y_RAIL_BOT_MINUS: int = Y_RAIL_BOT_PLUS + 20                          # 402

CANVAS_HEIGHT:   int = Y_RAIL_BOT_MINUS + BOTTOM_MARGIN

# Offset from the rail to the first detour band (band 0). Higher band
# indices stack outward at DETOUR_BAND_PITCH px each.
DETOUR_BASE_OFFSET: int = 10


def canvas_width(num_positions: int) -> int:
    """Pixel width of a canvas holding `num_positions` columns. Use this
    instead of a CANVAS_WIDTH constant so designs that need more than 63
    positions (Dice → 106, DoorbellProtector → 92) still get a drawing —
    visually the equivalent of two breadboards daisy-chained at the bench."""
    return (
        LEFT_MARGIN + RIGHT_MARGIN
        + POSITION_PITCH * (num_positions - 1)
        + POSITION_PITCH
    )


def detour_overflow(top_bands: int, bot_bands: int) -> tuple[int, int]:
    """Return (extra_top, extra_bot) — how many pixels the detour
    bands extend above the default top margin / below the default
    bottom margin.

    Each band needs DETOUR_BAND_PITCH px. A modest 16-px cushion sits
    above the topmost band and below the bottommost so jumpers don't
    crowd the canvas edge.

    Used by the renderer to extend the viewBox just enough to keep
    every detour band on canvas, without changing any of the rail or
    bank-row coordinates."""
    cushion = 16
    needed_top = DETOUR_BASE_OFFSET + top_bands * DETOUR_BAND_PITCH + cushion
    needed_bot = DETOUR_BASE_OFFSET + bot_bands * DETOUR_BAND_PITCH + cushion
    extra_top = max(0, needed_top - Y_RAIL_TOP_PLUS)
    extra_bot = max(0, needed_bot - (CANVAS_HEIGHT - Y_RAIL_BOT_MINUS))
    return extra_top, extra_bot

# Mapping from row letter → y pixel.
_ROW_Y: dict[str, int] = {
    'A': Y_ROW_A, 'B': Y_ROW_B, 'C': Y_ROW_C, 'D': Y_ROW_D, 'E': Y_ROW_E,
    'F': Y_ROW_F, 'G': Y_ROW_G, 'H': Y_ROW_H, 'I': Y_ROW_I, 'J': Y_ROW_J,
}


def position_x(position: int) -> int:
    """Pixel x of position `position` (1..63). Position 1 sits at the
    left edge of the tie-strip area; position 63 sits at the right."""
    return LEFT_MARGIN + POSITION_PITCH // 2 + (position - 1) * POSITION_PITCH


def row_y(row: str) -> int:
    """Pixel y for a row letter A..J. Raises KeyError on unknown row."""
    return _ROW_Y[row.upper()]


def is_top_bank(row: str) -> bool:
    """True if the row is in the top bank (A..E), False for F..J."""
    return row.upper() in ('A', 'B', 'C', 'D', 'E')


def rail_y(polarity_high: bool, top: bool = True) -> int:
    """Pixel y for a power-rail strip. `top` selects the top vs bottom
    rail pair; `polarity_high` selects + (high) vs − (low)."""
    if top:
        return Y_RAIL_TOP_PLUS if polarity_high else Y_RAIL_TOP_MINUS
    return Y_RAIL_BOT_PLUS if polarity_high else Y_RAIL_BOT_MINUS


# --------------------------------------------------------- SVG primitives

def open_svg(
    width: int, height: int, x_offset: int = 0, y_offset: int = 0,
) -> str:
    """Opening `<svg>` tag with namespace and viewBox.

    `x_offset` / `y_offset` shift the viewBox origin so jumper detour
    bands that overflow the default canvas margins remain visible
    without renumbering every other y-coordinate in the renderer."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{x_offset} {y_offset} {width} {height}" '
        f'width="{width}" height="{height}">'
    )


def close_svg() -> str:
    """Closing `</svg>` tag."""
    return '</svg>'


def rect(x: float, y: float, w: float, h: float, fill: str,
         stroke: str = '', stroke_width: float = 1.0,
         rx: float = 0.0, klass: str = '') -> str:
    """Render a `<rect>` with inline style."""
    style_parts = [f'fill:{fill}']
    if stroke:
        style_parts.append(f'stroke:{stroke}')
        style_parts.append(f'stroke-width:{stroke_width:g}')
    style = ';'.join(style_parts)
    cls = f' class="{klass}"' if klass else ''
    rx_attr = f' rx="{rx:g}"' if rx else ''
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
        f'{rx_attr}{cls} style="{style}"/>'
    )


def line(x1: float, y1: float, x2: float, y2: float,
         stroke: str, stroke_width: float = 1.0,
         klass: str = '') -> str:
    """Render a `<line>` with inline style."""
    cls = f' class="{klass}"' if klass else ''
    return (
        f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"'
        f'{cls} style="stroke:{stroke};stroke-width:{stroke_width:g}"/>'
    )


def circle(cx: float, cy: float, r: float, fill: str,
           stroke: str = '', stroke_width: float = 1.0,
           klass: str = '') -> str:
    """Render a `<circle>` with inline style."""
    style_parts = [f'fill:{fill}']
    if stroke:
        style_parts.append(f'stroke:{stroke}')
        style_parts.append(f'stroke-width:{stroke_width:g}')
    cls = f' class="{klass}"' if klass else ''
    return (
        f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}"'
        f'{cls} style="{";".join(style_parts)}"/>'
    )


def text(x: float, y: float, content: str, fill: str = '#000000',
         size: int = 10, anchor: str = 'start',
         font_family: str = 'monospace', klass: str = '',
         weight: str = 'normal') -> str:
    """Render a `<text>` with inline style. The content is escaped for
    `&`, `<`, `>` so user-supplied refdes / class names can't break the
    SVG."""
    escaped = (
        content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    )
    cls = f' class="{klass}"' if klass else ''
    return (
        f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}"'
        f'{cls} style="font-family:{font_family};font-size:{size}px;'
        f'fill:{fill};font-weight:{weight}">{escaped}</text>'
    )


def path(d: str, stroke: str, stroke_width: float = 2.0,
         fill: str = 'none', klass: str = '') -> str:
    """Render a `<path>` with the given SVG path-data string."""
    cls = f' class="{klass}"' if klass else ''
    return (
        f'<path d="{d}"{cls} style="fill:{fill};stroke:{stroke};'
        f'stroke-width:{stroke_width:g}"/>'
    )


def group_open(klass: str, **attrs: str) -> str:
    """Open a `<g>` element with class + optional `data-*` attributes."""
    attr_str = ''.join(f' {k}="{v}"' for k, v in attrs.items())
    return f'<g class="{klass}"{attr_str}>'


def group_close() -> str:
    return '</g>'


# --------------------------------------------------------- path helpers

def manhattan_path(x1: float, y1: float, x2: float, y2: float,
                   detour_y: float | None = None) -> str:
    """Build an L-shaped (or U-shaped) Manhattan jumper path.

    If `detour_y` is given the path goes (x1,y1) → (x1,detour_y) →
    (x2,detour_y) → (x2,y2). This is the canonical jumper shape: pop
    up out of the tie strip, run horizontally above the board, drop
    back down into the destination strip. The detour level is also
    what keeps multiple jumpers from overlaying on the same bank row.

    With no detour the path is just a single L: (x1,y1) → (x2,y1) →
    (x2,y2). Used for short same-bank jumpers.
    """
    if detour_y is None:
        return f'M {x1:g} {y1:g} L {x2:g} {y1:g} L {x2:g} {y2:g}'
    return (
        f'M {x1:g} {y1:g} L {x1:g} {detour_y:g} '
        f'L {x2:g} {detour_y:g} L {x2:g} {y2:g}'
    )


# --------------------------------------------------------- pin coordinate

@dataclass(frozen=True, slots=True)
class PinPixel:
    """A pin's (x, y) pixel position on the SVG canvas, plus a tag
    indicating which bank or rail it sits in so the routing layer can
    decide how to drop the jumper out of the tie strip."""
    x: float
    y: float
    # 'top_bank' | 'bot_bank' | 'top_plus' | 'top_minus' | 'bot_plus' | 'bot_minus'
    surface: str
