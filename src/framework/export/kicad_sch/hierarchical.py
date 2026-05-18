"""Hierarchical sheet emission for multi-Board designs — Phase 2.5c.

Multi-Board designs (a top-level Circuit that contains Board children)
become hierarchical KiCad schematics:

  - The top-level `.kicad_sch` contains one `(sheet ...)` block per Board.
  - Each Board's contents become a separate `.kicad_sch` file referenced
    by the top-level sheet.
  - File naming: `<Design>.kicad_sch` (top-level),
    `<Design>__<BoardClassName>.kicad_sch` (per-Board sub-sheets).

For single-Board and flat Circuit designs the renderer uses a single flat
`.kicad_sch`; this module's full emission path is only invoked for
multi-Board designs.
"""
from __future__ import annotations

from framework.board import Board
from framework.circuit import Circuit
from framework.part import Part


_SHEET_W: float = 80.0
_SHEET_H: float = 50.0
_SHEET_GAP: float = 40.0
_MARGIN: float = 30.0
_LABEL_CLEARANCE_MM: float = 10.0   # headroom below box for the Sheetfile label

_PAPER_SIZES: tuple[tuple[int, int, str], ...] = (
    (297, 210, 'A4'),
    (420, 297, 'A3'),
    (594, 420, 'A2'),
    (841, 594, 'A1'),
)


def collect_boards(design: Part) -> list[Board]:
    """Return every immediate Board child of `design`, in declaration order.

    A `Circuit` containing a single Board yields a 1-element list; a
    `Circuit` containing only non-Board parts yields an empty list; a
    `design` that isn't a `Circuit` also yields an empty list. Use
    `is_multi_board()` to decide whether hierarchical-sheet emission
    applies — this function reports presence, not multi-Board-ness.
    """
    if not isinstance(design, Circuit):
        return []
    return [p for p in design.parts if isinstance(p, Board)]


def is_multi_board(design: Part) -> bool:
    """True if `design` contains more than one Board child."""
    return len(collect_boards(design)) > 1


def sub_sheet_filename(design_name: str, board_class_name: str) -> str:
    """Conventional filename for a Board's sub-sheet."""
    return f'{design_name}__{board_class_name}.kicad_sch'


def _pick_paper(total_w: float, total_h: float) -> tuple[str, float, float]:
    """Pick the smallest A-series paper that fits `total_w x total_h`."""
    for pw, ph, name in _PAPER_SIZES:
        if pw >= total_w and ph >= total_h:
            return name, float(pw), float(ph)
    return 'User', total_w, total_h


def emit_top_level(boards: list[Board], design_name: str) -> str:
    """Emit the top-level system schematic with one (sheet ...) block per Board."""
    from framework.export.kicad_sch.renderer import (
        _uuid, _q, _f, _xy, _effects, _SCH_VERSION,
    )

    n = len(boards)
    total_w = 2 * _MARGIN + n * _SHEET_W + max(0, n - 1) * _SHEET_GAP
    total_h = 2 * _MARGIN + _SHEET_H + _LABEL_CLEARANCE_MM
    paper, pw, ph = _pick_paper(total_w, total_h)

    lines: list[str] = []
    lines.append('(kicad_sch')
    lines.append(f'  (version {_SCH_VERSION})')
    lines.append('  (generator "wirebench")')
    lines.append('  (generator_version "0.2")')
    lines.append(f'  (uuid {_q(_uuid(design_name + "_top"))})')
    if paper == 'User':
        lines.append(f'  (paper "User" {_f(pw)} {_f(ph)})')
    else:
        lines.append(f'  (paper {_q(paper)})')

    x = _MARGIN
    y = _MARGIN
    for board in boards:
        board_class_name = type(board).__name__
        sheet_file = sub_sheet_filename(design_name, board_class_name)
        seed = f'{design_name}_sheet_{board_class_name}'

        sheetname_y = y - 1.5
        sheetfile_y = y + _SHEET_H + 1.0

        lines.append('  (sheet')
        lines.append(f'    (at {_xy(x, y)})')
        lines.append(f'    (size {_f(_SHEET_W)} {_f(_SHEET_H)})')
        lines.append('    (fields_autoplaced yes)')
        lines.append('    (stroke (width 0.0006) (type default))')
        lines.append('    (fill (color 0 0 0 0.0000))')
        lines.append(f'    (uuid {_q(_uuid(seed))})')
        lines.append(
            f'    (property "Sheetname" {_q(board_class_name)}\n'
            f'      (at {_xy(x, sheetname_y)} 0)\n'
            f'      {_effects(justify="left bottom")}\n'
            f'    )'
        )
        lines.append(
            f'    (property "Sheetfile" {_q(sheet_file)}\n'
            f'      (at {_xy(x, sheetfile_y)} 0)\n'
            f'      {_effects(justify="left top")}\n'
            f'    )'
        )
        lines.append('  )')

        x += _SHEET_W + _SHEET_GAP

    lines.append(
        '  (sheet_instances\n'
        '    (path "/" (page "1"))\n'
        '  )'
    )
    lines.append(')')
    return '\n'.join(lines) + '\n'
