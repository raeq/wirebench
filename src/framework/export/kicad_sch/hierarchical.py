"""Hierarchical sheet emission for multi-Board designs — Phase 2.5b.

Multi-Board designs (a top-level Circuit that contains Board children)
become hierarchical KiCad schematics:

  - The top-level `.kicad_sch` contains one `(sheet ...)` block per Board.
  - Each Board's contents become a separate `.kicad_sch` file referenced
    by the top-level sheet.
  - File naming: `<Design>.kicad_sch` (top-level),
    `<Design>__<BoardClassName>.kicad_sch` (per-Board sub-sheets).

For single-Board and flat Circuit designs the renderer uses a single flat
`.kicad_sch`; this module is only invoked for multi-Board designs.

Phase 2.5b ships this module as a detection helper. Full multi-Board sheet
emission (the actual `(sheet ...)` S-expression blocks) is out of scope
for this PR but the interface is established so the renderer can call
`is_multi_board()` and branch appropriately.
"""
from __future__ import annotations

from framework.board import Board
from framework.circuit import Circuit
from framework.part import Part


def collect_boards(design: Part) -> list[Board]:
    """Return the immediate Board children of `design`.

    Returns an empty list for flat (non-Circuit or single-board) designs.
    """
    if not isinstance(design, Circuit):
        return []
    return [p for p in design.parts if isinstance(p, Board)]


def is_multi_board(design: Part) -> bool:
    """True if `design` contains more than one Board child."""
    return len(collect_boards(design)) > 1


def sub_sheet_filename(design_name: str, board_class_name: str) -> str:
    """Conventional filename for a Board's sub-sheet.

    Example: design_name='WaterAlarmAssembly',
             board_class_name='SensorBoard'
          → 'WaterAlarmAssembly__SensorBoard.kicad_sch'
    """
    return f'{design_name}__{board_class_name}.kicad_sch'
