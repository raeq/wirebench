"""Top-level breadboard SVG renderer.

Walks a wirebench `Part` and emits the full breadboard SVG document.
The output is one self-contained `<svg>` block per `Circuit`.

Pipeline:
  1. `placement.collect_parts(design)` — walk the design's BOM-level
     leaf parts (Chip + Connector + 2-lead passives + Rails).
  2. `placement.refuse_unsupported(design, …)` — refuse SMD / Board /
     multi-Board top levels with `BreadboardIncompatibleError`.
  3. `placement.place_design(placeable)` — run the shared
     assembly_guide placement so positions match the assembly guide.
  4. Refuse designs that don't fit the 63-position canvas (acceptance
     criterion 7).
  5. Build the SVG: surface (board / rails / tie-point holes), then
     component bodies, then jumpers, then refdes labels.
"""
from __future__ import annotations

from typing import Iterable

from framework.chip import Chip
from framework.connector import Connector
from framework.errors import BreadboardIncompatibleError
from framework.part import Part

from framework.export.base import ExporterContext

from framework.export.assembly_guide.placement import ComponentPlacement, PinPlacement

from framework.export.breadboard import colors, svg
from framework.export.breadboard.placement import (
    collect_parts, place_design, refuse_unsupported,
)
from framework.export.breadboard.routing import Jumper, JumperKind, route_jumpers


__all__ = ['render']


# --------------------------------------------------------- public entry

def render(design: Part, ctx: ExporterContext) -> str:
    """Render `design` to an SVG document. Raises
    `BreadboardIncompatibleError` for unsupported designs."""
    all_parts, placeable = collect_parts(design)
    refuse_unsupported(design, placeable)
    pl = place_design(placeable)

    num_positions = _check_capacity(pl.components)
    width = svg.canvas_width(num_positions)

    chip_ranges = _chip_column_ranges(pl.components)
    jumpers = route_jumpers(all_parts, pl.by_component)
    endpoint_rows = _assign_endpoint_rows(jumpers, pl.by_component)
    band_assignment, pivot_by_jumper = _assign_detour_bands(
        jumpers, chip_ranges, endpoint_rows,
    )

    # Size the viewBox to fit however many detour bands the greedy
    # interval-colour allocator needed — overflow past the default
    # margins shifts the viewBox origin negative on top and grows the
    # canvas height on the bottom.
    top_bands = max(
        (b for sides in band_assignment.values() for b, s in sides if s == 'top'),
        default=-1,
    ) + 1
    bot_bands = max(
        (b for sides in band_assignment.values() for b, s in sides if s == 'bot'),
        default=-1,
    ) + 1
    extra_top, extra_bot = svg.detour_overflow(top_bands, bot_bands)
    total_height = svg.CANVAS_HEIGHT + extra_top + extra_bot

    # Z-order: surface → jumpers → components. Jumpers render BEFORE
    # components so chip bodies (drawn opaque) hide the portion of a
    # jumper that passes "behind" them — a cross-bank jumper whose
    # vertical at the source column traverses the chip body now appears
    # to disappear into the chip's footprint and re-emerge on the other
    # side, matching how a real jumper physically routes around the
    # chip's plastic. Pin-number labels live inside the chip's
    # `<g class="component">` group so they still draw on top of the
    # body fill.
    parts: list[str] = []
    parts.append(svg.open_svg(width, total_height, y_offset=-extra_top))
    parts.append(f'<title>{type(design).__name__} — breadboard layout</title>')
    parts.append(_render_surface(num_positions, width))
    parts.extend(_render_jumpers(
        jumpers, band_assignment, pivot_by_jumper, endpoint_rows,
    ))
    parts.extend(_render_components(pl.components))
    parts.append(svg.close_svg())
    return '\n'.join(parts) + '\n'


# --------------------------------------------------------- capacity check

def _check_capacity(components: Iterable[ComponentPlacement]) -> int:
    """Return the number of columns the canvas should hold for this
    design — at least 63 (one full-size breadboard) and at most
    `MAX_POSITIONS` (raises otherwise so the SVG never grows unboundedly
    for pathological designs)."""
    max_pos = 0
    for c in components:
        for _, pp in c.pins:
            if pp.position > max_pos:
                max_pos = pp.position
    if max_pos > svg.MAX_POSITIONS:
        raise BreadboardIncompatibleError(
            f"Design exceeds maximum breadboard capacity. Placement "
            f"reaches position {max_pos}, but the visualiser caps at "
            f"{svg.MAX_POSITIONS} columns (four daisy-chained full-size "
            "breadboards). Split the design into separate Circuits, or "
            "use the `kicad` exporter to lay out a custom PCB."
        )
    # Always show at least one full-size breadboard's worth of columns so
    # the user reads "63 visible columns" as the canonical reference even
    # for small designs.
    return max(svg.NUM_POSITIONS, max_pos)


# --------------------------------------------------------- surface

def _render_surface(num_positions: int, width: int) -> str:
    """The board's bottom layer: cream card, four power rail strips, all
    tie-point holes, and the central trough.

    Drawn first so component bodies and jumpers can overlay it. The
    canvas is sized to `num_positions` columns so designs over 63
    positions (Dice → 106) get their full visual extent."""
    pieces: list[str] = []
    pieces.append(svg.group_open('board-surface'))
    # Card
    pieces.append(svg.rect(
        0, 0, width, svg.CANVAS_HEIGHT,
        fill=colors.BOARD_BACKGROUND,
        stroke=colors.BOARD_BORDER, stroke_width=1,
    ))

    # Power rails: each pair has a + and a − line. Stripes drawn as
    # thick lines so they're recognisable as rails (not just thin
    # gridlines).
    for top in (True, False):
        for high in (True, False):
            y = svg.rail_y(high, top=top)
            color = colors.RAIL_PLUS_LINE if high else colors.RAIL_MINUS_LINE
            pieces.append(svg.line(
                svg.LEFT_MARGIN, y, width - svg.RIGHT_MARGIN, y,
                stroke=color, stroke_width=2, klass='rail-strip',
            ))
            # Rail label at the left edge.
            label = '+' if high else '−'
            pieces.append(svg.text(
                svg.LEFT_MARGIN - 14, y + 4, label, fill=color,
                size=12, weight='bold',
            ))

    # Tie-point holes — top + bottom rails first, then the bank rows.
    # Drawn as small dark circles; lots of them so they read as a real
    # breadboard.
    for top in (True, False):
        for high in (True, False):
            y = svg.rail_y(high, top=top)
            for pos in range(1, num_positions + 1):
                pieces.append(svg.circle(
                    svg.position_x(pos), y, 1.5,
                    fill=colors.TIE_POINT, klass='tie-point',
                ))
    for row in 'ABCDEFGHIJ':
        y = svg.row_y(row)
        for pos in range(1, num_positions + 1):
            pieces.append(svg.circle(
                svg.position_x(pos), y, 1.5,
                fill=colors.TIE_POINT, klass='tie-point',
            ))

    # Central trough — a hint of darker fill to convey the gap.
    pieces.append(svg.rect(
        svg.LEFT_MARGIN, svg.Y_TROUGH_TOP,
        width - svg.LEFT_MARGIN - svg.RIGHT_MARGIN,
        svg.Y_TROUGH_BOT - svg.Y_TROUGH_TOP,
        fill='#f0e8d0', stroke='', klass='trough',
    ))

    # Position numbers above and below the board — every fifth position
    # gets a label so the user can read off positions at the bench.
    for pos in range(5, num_positions + 1, 5):
        x = svg.position_x(pos)
        pieces.append(svg.text(
            x, svg.Y_ROW_A - 14, str(pos),
            fill='#888888', size=8, anchor='middle',
        ))
        pieces.append(svg.text(
            x, svg.Y_ROW_J + 16, str(pos),
            fill='#888888', size=8, anchor='middle',
        ))

    # Visual break every 63 positions to suggest "this would be a fresh
    # breadboard" — only relevant for designs that need more than one.
    for break_pos in range(svg.NUM_POSITIONS, num_positions, svg.NUM_POSITIONS):
        x = svg.position_x(break_pos) + svg.POSITION_PITCH // 2
        pieces.append(svg.line(
            x, svg.Y_RAIL_TOP_PLUS - 5, x, svg.Y_RAIL_BOT_MINUS + 5,
            stroke='#cccccc', stroke_width=1, klass='board-break',
        ))

    # Row letters on each side.
    for row in 'ABCDEFGHIJ':
        y = svg.row_y(row)
        pieces.append(svg.text(
            svg.LEFT_MARGIN - 14, y + 3, row,
            fill='#888888', size=8, weight='bold',
        ))

    pieces.append(svg.group_close())
    return '\n'.join(pieces)


# --------------------------------------------------------- components

def _render_components(
    components: Iterable[ComponentPlacement],
) -> list[str]:
    """Emit one SVG group per placed component."""
    out: list[str] = []
    for placement in components:
        out.append(_render_one_component(placement))
    return out


def _render_one_component(placement: ComponentPlacement) -> str:
    """Render one component's body + refdes label. The drawing style
    depends on whether the component is a Chip, a Connector, or a
    2-lead passive — but each is a labelled rectangle covering its
    pin span."""
    part = placement.component
    if not placement.pins:
        # No pin placements (e.g. an off-board Uno board). Drawn as a
        # callout box in the right margin.
        return _render_off_board_callout(part)

    refdes = getattr(part, 'refdes', '?')
    cls = type(part).__name__

    if isinstance(part, Chip):
        return _render_chip_body(part, placement, refdes, cls)
    if isinstance(part, Connector):
        return _render_connector_body(part, placement, refdes, cls)
    return _render_passive_body(part, placement, refdes, cls)


def _component_bbox(placement: ComponentPlacement) -> tuple[int, int, int, int]:
    """Return (min_pos, max_pos, top_rows_used, bot_rows_used)."""
    positions = [pp.position for _, pp in placement.pins]
    rows = [pp.row for _, pp in placement.pins]
    return (
        min(positions), max(positions),
        sum(1 for r in rows if r.upper() in 'ABCDE'),
        sum(1 for r in rows if r.upper() in 'FGHIJ'),
    )


def _render_chip_body(
    part: Part, placement: ComponentPlacement, refdes: str, cls: str,
) -> str:
    """A DIP body straddling the trough — rectangle covering positions
    p_min..p_max, vertically spanning from row E to row F."""
    p_min, p_max, _, _ = _component_bbox(placement)
    x1 = svg.position_x(p_min) - svg.POSITION_PITCH // 2 + 4
    x2 = svg.position_x(p_max) + svg.POSITION_PITCH // 2 - 4
    # Detect SIP (all pins on one bank) vs DIP (straddling trough).
    rows = [pp.row for _, pp in placement.pins]
    sip = all(r.upper() in 'ABCDE' for r in rows) or all(
        r.upper() in 'FGHIJ' for r in rows
    )
    if sip:
        # SIP: body sits on the bank rows of the pin row.
        bank_top = 'ABCDE' if rows[0].upper() in 'ABCDE' else 'FGHIJ'
        y1 = svg.row_y(bank_top[0]) - 6
        y2 = svg.row_y(bank_top[-1]) + 6
    else:
        # DIP: straddle the trough, from row E down to row F.
        y1 = svg.row_y('E') - 4
        y2 = svg.row_y('F') + 4
    parts: list[str] = []
    parts.append(svg.group_open('component', **{
        'data-refdes': refdes, 'data-kind': 'chip',
    }))
    parts.append(svg.rect(
        x1, y1, x2 - x1, y2 - y1,
        fill=colors.CHIP_BODY, stroke='#000000', stroke_width=1, rx=3,
    ))
    # Notch indicator on the left edge.
    parts.append(svg.circle(
        x1 + 8, (y1 + y2) / 2, 2.5, fill=colors.CHIP_LABEL,
    ))
    # Class label centred on the body.
    cx = (x1 + x2) / 2
    cy_label = (y1 + y2) / 2 - 4
    cy_refdes = (y1 + y2) / 2 + 8
    parts.append(svg.text(
        cx, cy_label, cls, fill=colors.CHIP_LABEL,
        size=10, anchor='middle',
    ))
    parts.append(svg.text(
        cx, cy_refdes, refdes, fill=colors.CHIP_LABEL,
        size=9, anchor='middle', weight='bold',
    ))
    # Pin-name labels — small white text printed inside the chip body
    # next to each pin's column. The framework's pin name (`VSS`,
    # `q_1`, `OE`, `in_3`, …) is what the design's `wire()` calls use,
    # so showing it on the chip directly lets the builder cross-
    # reference the schematic / source / assembly guide against the
    # physical chip at a glance. Pin NUMBERS are intentionally not
    # shown — the DIP convention (pin 1 top-left at the notch, then
    # counter-clockwise) makes the number derivable from position.
    from framework.chip import Chip
    if isinstance(part, Chip):
        for pin_name, pp in placement.pins:
            x_pin = svg.position_x(pp.position)
            if pp.row.upper() in 'ABCDE':
                y_pin = y1 + 10   # just inside the body's top edge
            else:
                y_pin = y2 - 4    # just inside the body's bottom edge
            parts.append(svg.text(
                x_pin, y_pin, pin_name,
                fill=colors.CHIP_LABEL, size=7,
                anchor='middle', weight='bold',
            ))
    parts.append(svg.group_close())
    return '\n'.join(parts)


def _render_connector_body(
    part: Part, placement: ComponentPlacement, refdes: str, cls: str,
) -> str:
    """Header strip — narrow rectangle on the top bank."""
    p_min, p_max, _, _ = _component_bbox(placement)
    x1 = svg.position_x(p_min) - svg.POSITION_PITCH // 2 + 4
    x2 = svg.position_x(p_max) + svg.POSITION_PITCH // 2 - 4
    y1 = svg.row_y('A') - 6
    y2 = svg.row_y('C') + 4
    parts: list[str] = []
    parts.append(svg.group_open('component', **{
        'data-refdes': refdes, 'data-kind': 'connector',
    }))
    parts.append(svg.rect(
        x1, y1, x2 - x1, y2 - y1,
        fill=colors.CONNECTOR_BODY, stroke='#000000', stroke_width=1, rx=2,
    ))
    cx = (x1 + x2) / 2
    parts.append(svg.text(
        cx, (y1 + y2) / 2 - 1, cls, fill=colors.CONNECTOR_LABEL,
        size=9, anchor='middle',
    ))
    parts.append(svg.text(
        cx, (y1 + y2) / 2 + 10, refdes, fill=colors.CONNECTOR_LABEL,
        size=8, anchor='middle', weight='bold',
    ))
    parts.append(svg.group_close())
    return '\n'.join(parts)


def _render_passive_body(
    part: Part, placement: ComponentPlacement, refdes: str, cls: str,
) -> str:
    """2-lead axial part: thin body spanning the two pin positions on
    the top bank.

    Slightly different stroke / fill per part type so a hobbyist
    glancing at the board can tell resistors from LEDs from caps."""
    from components.passives.resistor import Resistor
    from components.passives.capacitor import Capacitor
    from components.passives.led import LED
    from framework.diode import Diode

    p_min, p_max, _, _ = _component_bbox(placement)
    x1 = svg.position_x(p_min)
    x2 = svg.position_x(p_max)
    if x2 - x1 < svg.POSITION_PITCH:
        x2 = x1 + svg.POSITION_PITCH
    # Pins land at the placement's row (row D per assembly_guide
    # placement — near the trough). The body sits just above its pin
    # row, between rows B and C, so rows A and B above it remain
    # entirely clear for jumpers terminating at row A on the same
    # tie strip. Refdes label fits above the body around row B.
    pin_row = placement.pins[0][1].row if placement.pins else 'D'
    y_tie = svg.row_y(pin_row)
    y_center = svg.row_y('C') - 3
    body_h = 14
    body_y1 = y_center - body_h / 2
    body_y2 = y_center + body_h / 2

    parts: list[str] = []
    parts.append(svg.group_open('component', **{
        'data-refdes': refdes, 'data-kind': 'passive',
    }))
    # Lead lines: from the body bottom down through row A to the tie
    # point at row B. Drawn as part of the component so they move
    # with it logically.
    parts.append(svg.line(
        x1, y_tie, x1, body_y2, stroke='#222222', stroke_width=1,
    ))
    parts.append(svg.line(
        x2, y_tie, x2, body_y2, stroke='#222222', stroke_width=1,
    ))

    if isinstance(part, LED):
        body_color = colors.led_body_color(getattr(part, 'color', '') or '')
        # Round-ish LED body — short oval centred on the part.
        parts.append(svg.rect(
            x1 + 2, body_y1, x2 - x1 - 4, body_h,
            fill=body_color, stroke='#000000', stroke_width=1, rx=5,
        ))
        # Tiny notch hint (the cathode flat).
        parts.append(svg.line(
            x2 - 4, body_y1 + 1, x2 - 4, body_y2 - 1,
            stroke='#000000', stroke_width=1,
        ))
        label = f"{refdes} ({getattr(part, 'color', '?')})"
    elif isinstance(part, Capacitor):
        parts.append(svg.rect(
            x1 + 2, body_y1, x2 - x1 - 4, body_h,
            fill=colors.CAP_BODY, stroke='#000000', stroke_width=1, rx=3,
        ))
        label = refdes
    elif isinstance(part, Diode):
        parts.append(svg.rect(
            x1 + 2, body_y1, x2 - x1 - 4, body_h,
            fill=colors.DIODE_BODY, stroke='#000000', stroke_width=1, rx=2,
        ))
        # Cathode stripe at the second lead end.
        parts.append(svg.line(
            x2 - 4, body_y1 + 1, x2 - 4, body_y2 - 1,
            stroke=colors.DIODE_LABEL, stroke_width=2,
        ))
        label = refdes
    elif isinstance(part, Resistor):
        parts.append(svg.rect(
            x1 + 2, body_y1, x2 - x1 - 4, body_h,
            fill=colors.PASSIVE_BODY, stroke='#000000', stroke_width=1, rx=4,
        ))
        # Value label inside the body — engineering notation
        # (47 Ω, 4.7 kΩ, 10 kΩ, 1 MΩ) via the Ohms class's
        # canonical str. Matches what a bench builder reads off a
        # resistor's colour bands or sees on a schematic.
        ohms = getattr(part, 'ohms', None)
        val_label = str(ohms) if ohms is not None else ""
        parts.append(svg.text(
            (x1 + x2) / 2, y_center + 3, val_label, fill=colors.PASSIVE_LABEL,
            size=8, anchor='middle',
        ))
        label = refdes
    else:
        parts.append(svg.rect(
            x1 + 2, body_y1, x2 - x1 - 4, body_h,
            fill=colors.PASSIVE_BODY, stroke='#000000', stroke_width=1, rx=3,
        ))
        label = refdes

    # Refdes label above the body so it doesn't fight with the value
    # text inside the body.
    parts.append(svg.text(
        (x1 + x2) / 2, body_y1 - 3, label, fill=colors.PASSIVE_LABEL,
        size=8, anchor='middle', weight='bold',
    ))
    parts.append(svg.group_close())
    return '\n'.join(parts)


def _render_off_board_callout(part: Part) -> str:
    """Render off-board parts (Arduino Uno boards) as a callout label
    floating beside the breadboard. They have no pin placements; the
    jumpers that connect to their headers are still drawn but anchored
    to the right edge.

    For v1 we just draw a small annotation in the top-right corner of
    the canvas; off-board jumpers won't have a sensible destination
    point so we omit them in the routing pass."""
    refdes = getattr(part, 'refdes', '?')
    cls = type(part).__name__
    # Anchored to the canvas right edge — recomputed at draw time so it
    # tracks dynamic canvas widths.
    x = svg.canvas_width(svg.NUM_POSITIONS) - svg.RIGHT_MARGIN - 140
    y = svg.Y_RAIL_BOT_PLUS + 12
    parts: list[str] = []
    parts.append(svg.group_open('component', **{
        'data-refdes': refdes, 'data-kind': 'off-board',
    }))
    parts.append(svg.rect(
        x, y, 140, 16, fill='#404040', stroke='#000000', stroke_width=1, rx=2,
    ))
    parts.append(svg.text(
        x + 70, y + 11, f"{refdes} — {cls} (off-board)",
        fill='#ffffff', size=8, anchor='middle',
    ))
    parts.append(svg.group_close())
    return '\n'.join(parts)


# --------------------------------------------------------- jumpers

def _assign_endpoint_rows(
    jumpers: list[Jumper],
    placements: dict[int, ComponentPlacement],
) -> dict[tuple[int, int], str]:
    """For every jumper endpoint, pick a specific row letter on its
    tie strip so two jumpers terminating at the same strip don't try
    to plug into the same physical hole.

    On a real breadboard the five top-bank holes (rows A–E at one
    column) are one tie strip — wired together by internal copper —
    but each hole accepts only ONE wire or one component lead. A
    3-endpoint net needs two jumpers, and where the two meet on a
    shared strip, each jumper plugs into a different hole.

    Algorithm: walk every jumper's two endpoints and group by tie
    strip (col, bank). For each strip, list the rows already
    occupied (chip pins on rows E/F, passive leads on row D), then
    assign each jumper endpoint the next free hole in display order
    (A→D for top bank, J→G for bottom bank).

    Returns: (jumper_index, endpoint_index) → row letter, where
    endpoint_index is 0 for the source side, 1 for the destination
    side. Rail markers ('+TOP', '-TOP', '+BOT', '-BOT') aren't tie
    strip endpoints and don't appear in the result."""
    # 1. Which row is taken at each tie strip (by a chip pin or a
    #    passive lead)?
    occupied: dict[tuple[int, str], set[str]] = {}
    for placement in placements.values():
        for _pin_name, pp in placement.pins:
            bank = 'top' if pp.row.upper() in 'ABCDE' else 'bot'
            occupied.setdefault((pp.position, bank), set()).add(pp.row.upper())

    # 2. Which jumper endpoints land at each tie strip?
    by_strip: dict[tuple[int, str], list[tuple[int, int]]] = {}
    for jidx, j in enumerate(jumpers):
        ends = [(j.src_position, j.src_row),
                (j.dst_position, j.dst_row)]
        for end_idx, (col, row) in enumerate(ends):
            if row in ('+TOP', '-TOP', '+BOT', '-BOT'):
                continue
            bank = 'top' if row.upper() in 'ABCDE' else 'bot'
            by_strip.setdefault((col, bank), []).append((jidx, end_idx))

    # 3. Assign each endpoint a distinct row from the strip's free
    #    holes, in display order (A first for top, J first for bot).
    assignment: dict[tuple[int, int], str] = {}
    for (col, bank), endpoint_list in by_strip.items():
        used = occupied.get((col, bank), set())
        if bank == 'top':
            order = ['A', 'B', 'C', 'D', 'E']
        else:
            order = ['J', 'I', 'H', 'G', 'F']
        free = [r for r in order if r not in used]
        if not free:
            # Tie strip is fully occupied (unusual — would mean 5
            # component leads on one strip). Fall back to the first
            # row in display order so something is drawn.
            free = [order[0]]
        for i, (jidx, end_idx) in enumerate(endpoint_list):
            # Cycle through the free holes; if there are more
            # endpoints than free holes (rare), reuse the last one.
            assignment[(jidx, end_idx)] = free[min(i, len(free) - 1)]

    return assignment


def _endpoint_row(
    jumpers: list[Jumper],
    endpoint_rows: dict[tuple[int, int], str],
    jidx: int,
    end_idx: int,
) -> str:
    """Return the assigned row letter for a jumper endpoint, falling
    back to the legacy 'first hole on the strip' rule if the endpoint
    is a rail marker (which has no tie-strip position)."""
    j = jumpers[jidx]
    raw_row = j.src_row if end_idx == 0 else j.dst_row
    if raw_row in ('+TOP', '-TOP', '+BOT', '-BOT'):
        return raw_row
    return endpoint_rows.get((jidx, end_idx), 'A')


def _render_jumpers(
    jumpers: list[Jumper],
    band_assignment: dict[int, tuple[tuple[int, str], ...]],
    pivot_by_jumper: dict[int, float],
    endpoint_rows: dict[tuple[int, int], str],
) -> list[str]:
    """Emit one SVG path per jumper.

    Routing strategy:
      - Same-bank jumpers: one detour band on the matching side
        (top-to-top above the top rails, bot-to-bot below the bottom
        rails) — vertical at the bank doesn't cross any chip body.
      - Cross-bank jumpers: TWO detour bands — bot to escape the
        source chip's column, vertical at a CLEAR pivot column, top
        to approach the destination chip's column from above. The
        wire never has a visible vertical segment that "passes
        through" an opposite-bank tie strip at a chip column, which
        a reader would mistake for a connection to the chip's
        opposite-bank pin.
    """
    out: list[str] = []
    out.append(svg.group_open('jumpers'))
    for jidx, j in enumerate(jumpers):
        bands = band_assignment.get(id(j))
        pivot = pivot_by_jumper.get(id(j))
        src_row = _endpoint_row(jumpers, endpoint_rows, jidx, 0)
        dst_row = _endpoint_row(jumpers, endpoint_rows, jidx, 1)
        out.append(_render_one_jumper(j, bands, pivot, src_row, dst_row))
    out.append(svg.group_close())
    return out


def _chip_column_ranges(
    components: Iterable[ComponentPlacement],
) -> list[tuple[int, int]]:
    """Return (min_col, max_col) span for every Chip in the design.

    Used by the cross-bank router to find a CLEAR column between
    source and destination (one not inside any chip's footprint) so
    the vertical that bridges bot-detour ↔ top-detour doesn't visually
    cut through any chip body."""
    from framework.chip import Chip
    ranges: list[tuple[int, int]] = []
    for cp in components:
        if not isinstance(cp.component, Chip):
            continue
        if not cp.pins:
            continue
        positions = [pp.position for _, pp in cp.pins]
        ranges.append((min(positions), max(positions)))
    return ranges


def _find_clear_pivot(
    x_src: float, x_dst: float, chip_ranges: list[tuple[int, int]],
) -> float:
    """Return the pixel x of a column with no chip body, between
    `x_src` and `x_dst`.

    Strategy: prefer the midpoint of the gap between the source's
    chip and the destination's chip (or just past the source's chip
    in the direction of the destination). Fall back to the geometric
    midpoint if no clear column exists in the range — extremely
    unlikely on a normal breadboard layout, but the fallback keeps
    the renderer robust on pathological inputs."""
    lo_x = min(x_src, x_dst)
    hi_x = max(x_src, x_dst)
    # Build a set of pixel-x values occupied by any chip body. A
    # "column inside a chip body" is one between (min_col, max_col)
    # for any chip. Convert to pixel x with position_x().
    occupied: set[float] = set()
    for min_c, max_c in chip_ranges:
        for col in range(min_c, max_c + 1):
            occupied.add(float(svg.position_x(col)))
    # Scan columns between lo_x and hi_x (exclusive) for the first
    # one NOT in `occupied`. Round to the nearest position pitch so
    # the pivot always sits on a real breadboard column.
    pitch = svg.POSITION_PITCH
    # The src column itself is at lo_x or hi_x; skip those endpoints.
    candidates: list[float] = []
    x = lo_x + pitch
    while x < hi_x:
        if x not in occupied:
            candidates.append(x)
        x += pitch
    if candidates:
        # Prefer a column near the LEFT chip's right edge so the
        # source-side bot-detour segment is as short as possible —
        # the wire goes "around" the source chip locally rather than
        # detouring far before turning up.
        return candidates[0]
    return (lo_x + hi_x) / 2


def _assign_detour_bands(
    jumpers: list[Jumper],
    chip_ranges: list[tuple[int, int]],
    endpoint_rows: dict[tuple[int, int], str],
) -> tuple[
    dict[int, tuple[tuple[int, str], ...]],
    dict[int, float],
]:
    """Greedy interval colouring of jumper detour bands.

    For same-bank jumpers, one interval on the matching side.
    For cross-bank jumpers, TWO intervals: (x_src, x_pivot) on the
    source-side and (x_pivot, x_dst) on the destination-side.

    Returns:
      band_assignment: id(jumper) → tuple of (band_index, side) pairs.
        Same-bank jumpers have a 1-tuple; cross-bank have a 2-tuple
        whose first entry is the source-side band, second is the
        destination-side band.
      pivot_by_jumper: id(jumper) → pivot x (only for cross-bank).
    """
    # Each interval is (x_lo, x_hi, jumper_id, kind). 'kind' is 'src',
    # 'dst', or 'same' — used to decide what side ('top' or 'bot') the
    # interval lives on for cross-bank cases.
    top_intervals: list[tuple[float, float, int, str]] = []
    bot_intervals: list[tuple[float, float, int, str]] = []
    short_top_intervals: list[tuple[float, float, int, str]] = []
    short_bot_intervals: list[tuple[float, float, int, str]] = []
    pivot_by_jumper: dict[int, float] = {}

    # Same-bank jumpers within ~3 columns get a "short hop" detour
    # just above (or below) the bank row instead of all the way up to
    # the canvas-top detour band. A wide arch for a 2-column gap looks
    # absurd at the bench; a short hop reads as a small jumper bridge
    # between adjacent tie strips.
    short_threshold = svg.POSITION_PITCH * 3

    for jidx, j in enumerate(jumpers):
        src_row = _endpoint_row(jumpers, endpoint_rows, jidx, 0)
        dst_row = _endpoint_row(jumpers, endpoint_rows, jidx, 1)
        x1 = float(svg.position_x(j.src_position))
        x2 = float(svg.position_x(j.dst_position))
        if x1 == x2:
            continue   # straight vertical — no detour
        src_top = (src_row.upper() in 'ABCDE'
                   or '+TOP' in src_row or '-TOP' in src_row)
        dst_top = (dst_row.upper() in 'ABCDE'
                   or '+TOP' in dst_row or '-TOP' in dst_row)
        x_lo, x_hi = min(x1, x2), max(x1, x2)
        # Short same-bank jumper.
        if src_top and dst_top and (x_hi - x_lo) <= short_threshold:
            short_top_intervals.append((x_lo, x_hi, id(j), 'short-top'))
            continue
        if (not src_top) and (not dst_top) and (x_hi - x_lo) <= short_threshold:
            short_bot_intervals.append((x_lo, x_hi, id(j), 'short-bot'))
            continue
        if src_top and dst_top:
            top_intervals.append((x_lo, x_hi, id(j), 'same-top'))
        elif (not src_top) and (not dst_top):
            bot_intervals.append((x_lo, x_hi, id(j), 'same-bot'))
        else:
            # Cross-bank: pick a clear pivot column between src and dst.
            pivot = _find_clear_pivot(x1, x2, chip_ranges)
            pivot_by_jumper[id(j)] = pivot
            # Source-side segment: from x1 to pivot on the source's bank.
            src_lo, src_hi = min(x1, pivot), max(x1, pivot)
            # Destination-side segment: from pivot to x2 on dst's bank.
            dst_lo, dst_hi = min(pivot, x2), max(pivot, x2)
            if src_top:
                top_intervals.append((src_lo, src_hi, id(j), 'src'))
                bot_intervals.append((dst_lo, dst_hi, id(j), 'dst'))
            else:
                bot_intervals.append((src_lo, src_hi, id(j), 'src'))
                top_intervals.append((dst_lo, dst_hi, id(j), 'dst'))

    band_assignment: dict[int, tuple[tuple[int, str], ...]] = {}

    def _color(
        intervals: list[tuple[float, float, int, str]],
        side: str,
    ) -> None:
        intervals.sort(key=lambda t: (t[0], t[1], t[2]))
        bands_max_x: list[float] = []
        for x_lo, x_hi, jid, kind in intervals:
            band = -1
            for i, used_max in enumerate(bands_max_x):
                if used_max < x_lo:
                    bands_max_x[i] = x_hi
                    band = i
                    break
            if band == -1:
                bands_max_x.append(x_hi)
                band = len(bands_max_x) - 1
            existing = band_assignment.get(jid, ())
            # For cross-bank, store src-side first then dst-side.
            if kind == 'src':
                band_assignment[jid] = ((band, side),) + existing
            elif kind == 'dst':
                band_assignment[jid] = existing + ((band, side),)
            else:
                band_assignment[jid] = ((band, side),)

    _color(top_intervals, 'top')
    _color(bot_intervals, 'bot')
    _color(short_top_intervals, 'short-top')
    _color(short_bot_intervals, 'short-bot')
    return band_assignment, pivot_by_jumper


def _jumper_row(row: str) -> str:
    """Remap a chip-pin row to the canonical free hole on the same tie
    strip.

    The five top-bank holes (A..E) are one tie strip — wired together
    by the breadboard's internal copper. A chip's pin occupies one of
    those holes (almost always row E, the inner edge straddling the
    trough); the jumper that connects to that chip pin plugs into one
    of the remaining four holes (A..D) on the same strip. Same idea on
    the bottom bank (rows F..J share one strip; chip pins are on row
    F; jumpers plug into row J).

    Drawing the jumper terminus AT the chip-pin row (E or F) renders
    the wire visually merging into the chip body, which a hobbyist
    reads as "the wire goes inside the chip." Re-routing the visual
    terminus to row A or row J — both clear holes on the same strip —
    keeps the wire's endpoint visibly outside the chip and matches
    where the user actually plugs the jumper at the bench. The
    assembly guide already narrates each tie strip as "any of
    `<pos>A`–`<pos>E`", so this remap is consistent with the textual
    instructions.

    Rail markers ('+TOP', '-TOP', '+BOT', '-BOT') pass through
    unchanged — they don't represent a tie-strip position."""
    if row in ('+TOP', '-TOP', '+BOT', '-BOT'):
        return row
    up = row.upper()
    if up in 'ABCDE':
        return 'A'
    if up in 'FGHIJ':
        return 'J'
    return row


def _pin_pixel(position: int, row: str) -> tuple[float, float, str]:
    """Resolve a (position, row) to (x, y, surface_tag).

    Recognises rail markers '+TOP', '-TOP', '+BOT', '-BOT' produced by
    the routing layer for rail jumpers."""
    if row in ('+TOP', '-TOP', '+BOT', '-BOT'):
        high = row.startswith('+')
        top = row.endswith('TOP')
        return (
            float(svg.position_x(position)),
            float(svg.rail_y(high, top=top)),
            'rail',
        )
    return (
        float(svg.position_x(position)),
        float(svg.row_y(row)),
        'bank',
    )


def _render_one_jumper(
    j: Jumper,
    bands: tuple[tuple[int, str], ...] | None,
    pivot_x: float | None,
    src_row: str,
    dst_row: str,
) -> str:
    """Render one jumper at the pre-assigned detour band(s) and
    endpoint rows.

    `bands` is the tuple returned by `_assign_detour_bands`:
      - 1-tuple ((band, side),) → same-bank jumper with a single
        detour at the given side
      - 2-tuple ((src_band, src_side), (dst_band, dst_side)) →
        cross-bank jumper with two detours connected by a vertical
        at `pivot_x` (a column that has no chip body)

    `src_row` / `dst_row` are the per-endpoint row letters chosen by
    `_assign_endpoint_rows` so two jumpers terminating on the same
    tie strip use distinct holes.

    Same-column verticals (src_position == dst_position) ignore
    bands entirely and draw a single straight line."""
    x1, y1, _ = _pin_pixel(j.src_position, src_row)
    x2, y2, _ = _pin_pixel(j.dst_position, dst_row)

    if x1 == x2:
        d = f"M {x1:g} {y1:g} L {x2:g} {y2:g}"
    else:
        pitch = svg.DETOUR_BAND_PITCH

        def _detour_y(band: int, side: str) -> float:
            # 'top' / 'bot': full-canvas detour above / below the rails.
            # 'short-top' / 'short-bot': tight hop just above / below
            #   the bank row — used for same-bank jumpers within a few
            #   columns where a full detour reads as overkill.
            if side == 'top':
                return svg.Y_RAIL_TOP_PLUS - 10 - band * pitch
            if side == 'bot':
                return svg.Y_RAIL_BOT_MINUS + 10 + band * pitch
            if side == 'short-top':
                return svg.row_y('A') - 8 - band * pitch
            # 'short-bot'
            return svg.row_y('J') + 8 + band * pitch

        if not bands or len(bands) == 1:
            side = bands[0][1] if bands else 'top'
            band = bands[0][0] if bands else 0
            dy = _detour_y(band, side)
            d = svg.manhattan_path(x1, y1, x2, y2, detour_y=dy)
        else:
            # Cross-bank double detour. Path:
            #   (x1, y1) → (x1, src_detour) → (pivot, src_detour) →
            #   (pivot, dst_detour) → (x2, dst_detour) → (x2, y2)
            (src_band, src_side), (dst_band, dst_side) = bands[0], bands[1]
            src_dy = _detour_y(src_band, src_side)
            dst_dy = _detour_y(dst_band, dst_side)
            px = pivot_x if pivot_x is not None else (x1 + x2) / 2
            d = (
                f"M {x1:g} {y1:g} "
                f"L {x1:g} {src_dy:g} "
                f"L {px:g} {src_dy:g} "
                f"L {px:g} {dst_dy:g} "
                f"L {x2:g} {dst_dy:g} "
                f"L {x2:g} {y2:g}"
            )

    # Termination caps: a small filled circle in the jumper's colour at
    # each end so the reader can spot the plug-in point at a glance.
    # Distinguishes a real connection from a wire merely passing
    # through a column on its way to its actual termination.
    cap_r = 3.0
    cap1 = svg.circle(
        x1, y1, cap_r, fill=j.color,
        stroke='#000000', stroke_width=0.5, klass=f'jumper-cap {j.kind}',
    )
    cap2 = svg.circle(
        x2, y2, cap_r, fill=j.color,
        stroke='#000000', stroke_width=0.5, klass=f'jumper-cap {j.kind}',
    )
    line = svg.path(d, stroke=j.color, stroke_width=2.0,
                    klass=f'jumper {j.kind}')
    return '\n'.join([line, cap1, cap2])
