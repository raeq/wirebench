"""Naive grid placement for Phase 2.5a.

Places each component on a regular grid, left-to-right then
top-to-bottom.  Power symbols (Rails) are excluded — they are placed
inline at each pin stub in the renderer.

Grid spacing is generous (40 mm) so even 20-pin symbols don't overlap.
"""
from __future__ import annotations

import math

from framework.part import Part

# Millimetres between component origins on the grid.
GRID_SPACING_MM: float = 40.0

# Top-left origin of the component grid on the sheet.
ORIGIN_X_MM: float = 30.0
ORIGIN_Y_MM: float = 30.0

# How many columns before wrapping to the next row.
COLS: int = 6


def grid_place(parts: list[Part]) -> dict[int, tuple[float, float]]:
    """Return {id(part): (x_mm, y_mm)} for each part on a naive grid.

    The position is the schematic placement origin for the symbol.
    Coordinates snap to the KiCad 50-mil (1.27 mm) grid.
    """
    positions: dict[int, tuple[float, float]] = {}
    for idx, part in enumerate(parts):
        col = idx % COLS
        row = idx // COLS
        x = ORIGIN_X_MM + col * GRID_SPACING_MM
        y = ORIGIN_Y_MM + row * GRID_SPACING_MM
        # Snap to 1.27 mm (50-mil) grid
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        positions[id(part)] = (x, y)
    return positions


def sheet_size_mm(n_parts: int) -> tuple[float, float]:
    """Minimum bounding sheet size in mm for `n_parts` components."""
    rows = math.ceil(n_parts / COLS) if n_parts else 1
    cols = min(n_parts, COLS)
    w = ORIGIN_X_MM * 2 + cols * GRID_SPACING_MM
    h = ORIGIN_Y_MM * 2 + rows * GRID_SPACING_MM
    # Round up to A-series sheet sizes (A4=297×210, A3=420×297, A2=594×420)
    for sw, sh in ((297, 210), (420, 297), (594, 420), (841, 594)):
        if w <= sw and h <= sh:
            return sw, sh
    return w, h
