"""Layered Signal Flow placement — Phase 2.5b.

Replaces the naive grid layout with a deterministic bench-readable layout:

  Stage 1 — Band classification (power / signal / indicator)
  Stage 2 — Signal-flow DAG and BFS layer assignment
  Stage 3 — Cell placement within (band, layer) grid
  Stage 4 — Generous spacing constraints (1500/1000/800 mil)
  Stage 6 — Cluster detection and breakup (up to 10 iterations)
  Stage 8 — Page sizing (A4 → A3 → A2 → A1)

See .plans/phase-2.5-spec.md §5 for the full algorithm description.
"""
from __future__ import annotations

import math
from collections import defaultdict, deque

from framework.export.nets import LogicalNet
from framework.part import Part

# ---------------------------------------------------------------------------
# Spacing constants (mil → mm, 1 mil = 0.0254 mm)
# ---------------------------------------------------------------------------

_MIL: float = 0.0254

SAME_BAND_SPACING_MM:  float = 1500 * _MIL   # 38.1 mm
INTER_BAND_GUTTER_MM:  float = 1000 * _MIL   # 25.4 mm
INTER_LAYER_GUTTER_MM: float = 800  * _MIL   # 20.32 mm
PAGE_MARGIN_MM:        float = 1000 * _MIL   # 25.4 mm

# Chip classes that belong in the power band
_POWER_CHIP_CLASSES: frozenset[str] = frozenset({
    'LM7805', 'LM7812', 'LM7905', 'LM317', 'LM337', 'LM5002',
    'AMS1117_33', 'AMS1117_50', 'LP2950',
})


def _snap(v: float) -> float:
    """Snap to 1.27 mm (50-mil) grid."""
    return round(v / 1.27) * 1.27


# ---------------------------------------------------------------------------
# Stage 1 — Band classification
# ---------------------------------------------------------------------------

def _part_band(part: Part) -> str:
    """Classify a part into 'power', 'signal', or 'indicator' band."""
    from components.passives.led import LED
    from components.passives.rail import Rail

    if isinstance(part, Rail):
        return 'power'
    if type(part).__name__ in _POWER_CHIP_CLASSES:
        return 'power'
    if isinstance(part, LED):
        return 'indicator'
    return 'signal'


def _is_source(part: Part) -> bool:
    """True if the part is a natural signal source for BFS layer assignment."""
    from components.passives.rail import Rail
    from framework.connector import Connector

    return isinstance(part, (Rail, Connector))


# ---------------------------------------------------------------------------
# Stage 2 — Signal-flow DAG and BFS layer assignment
# ---------------------------------------------------------------------------

def _build_adj(
    parts: list[Part],
    nets: list[LogicalNet],
) -> dict[int, set[int]]:
    """Part-to-part adjacency via shared logical nets."""
    part_ids = {id(p) for p in parts}
    adj: dict[int, set[int]] = {id(p): set() for p in parts}
    for net in nets:
        connected: set[int] = set()
        for owner, _port in net.ports:
            if id(owner) in part_ids:
                connected.add(id(owner))
        for a in connected:
            for b in connected:
                if a != b:
                    adj[a].add(b)
    return adj


def _bfs_layers(
    parts: list[Part],
    adj: dict[int, set[int]],
) -> dict[int, int]:
    """Layer = BFS distance from nearest source; sources sit at layer 0."""
    layer: dict[int, int] = {}
    queue: deque[tuple[int, int]] = deque()

    for p in parts:
        if _is_source(p):
            layer[id(p)] = 0
            queue.append((id(p), 0))

    # Fallback: no recognised sources → start BFS from part with fewest connections.
    if not layer:
        fallback = min(parts, key=lambda p: len(adj.get(id(p), set())))
        layer[id(fallback)] = 0
        queue.append((id(fallback), 0))

    while queue:
        pid, d = queue.popleft()
        for nb in adj.get(pid, set()):
            if nb not in layer:
                layer[nb] = d + 1
                queue.append((nb, d + 1))

    # Parts unreachable from any source: assign to layer 1
    for p in parts:
        if id(p) not in layer:
            layer[id(p)] = 1

    return layer


# ---------------------------------------------------------------------------
# Stages 3 & 4 — Cell placement with generous spacing
# ---------------------------------------------------------------------------

def _refdes_sort_key(part: Part) -> tuple[str, int]:
    """Sort key: (prefix, number) so R1 < R2 < R10."""
    rd = str(getattr(part, 'refdes', type(part).__name__))
    # Split trailing digits from prefix
    i = len(rd)
    while i > 0 and rd[i - 1].isdigit():
        i -= 1
    prefix = rd[:i]
    number = int(rd[i:]) if rd[i:].isdigit() else 0
    return prefix, number


def _band_occupied_layers(
    parts: list[Part],
    band: str,
    band_of: dict[int, str],
    layer_of: dict[int, int],
    all_layers: list[int],
) -> int:
    """Count of items in the busiest layer-column of `band`."""
    bps = [p for p in parts if band_of[id(p)] == band]
    if not bps:
        return 0
    return max(
        sum(1 for p in bps if layer_of[id(p)] == lay)
        for lay in all_layers
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def layered_place(
    parts: list[Part],
    nets: list[LogicalNet],
) -> dict[int, tuple[float, float]]:
    """Return {id(part): (x_mm, y_mm)} using Layered Signal Flow placement.

    Coordinates are snapped to the 1.27 mm (50-mil) KiCad grid.
    """
    if not parts:
        return {}

    # Stage 1: band classification
    band_of: dict[int, str] = {id(p): _part_band(p) for p in parts}

    # Stage 2: layer assignment via BFS from sources
    adj = _build_adj(parts, nets)
    layer_of = _bfs_layers(parts, adj)

    # Group into (band, layer) cells
    cells: dict[tuple[str, int], list[Part]] = defaultdict(list)
    for p in parts:
        cells[(band_of[id(p)], layer_of[id(p)])].append(p)
    for key in cells:
        cells[key].sort(key=_refdes_sort_key)

    # Stage 3: assign X positions per layer column (same for all bands)
    all_layers = sorted({layer_of[id(p)] for p in parts})
    layer_x: dict[int, float] = {}
    cur_x = PAGE_MARGIN_MM
    for lay in all_layers:
        layer_x[lay] = _snap(cur_x)
        cur_x += SAME_BAND_SPACING_MM

    # Stage 4: assign Y band starts (power top, signal middle, indicator bottom)
    band_parts: dict[str, list[Part]] = {b: [] for b in ('power', 'signal', 'indicator')}
    for p in parts:
        band_parts[band_of[id(p)]].append(p)

    def _band_height(band: str) -> float:
        max_col = _band_occupied_layers(parts, band, band_of, layer_of, all_layers)
        if max_col == 0:
            return 0.0
        return max(SAME_BAND_SPACING_MM, max_col * SAME_BAND_SPACING_MM)

    band_y_start: dict[str, float] = {}
    cur_y = PAGE_MARGIN_MM
    for band in ('power', 'signal', 'indicator'):
        band_y_start[band] = _snap(cur_y)
        h = _band_height(band)
        if h > 0:
            cur_y += h + INTER_BAND_GUTTER_MM

    # Assign positions within each (band, layer) cell
    positions: dict[int, tuple[float, float]] = {}
    for (band, lay), cell_parts in sorted(cells.items()):
        bx = layer_x[lay]
        by = band_y_start[band]
        for i, p in enumerate(cell_parts):
            positions[id(p)] = (_snap(bx), _snap(by + i * SAME_BAND_SPACING_MM))

    # Stage 6: cluster breakup
    _break_clusters(positions, parts, band_of)

    return positions


# ---------------------------------------------------------------------------
# Stage 6 — Cluster detection and breakup
# ---------------------------------------------------------------------------

def _break_clusters(
    positions: dict[int, tuple[float, float]],
    parts: list[Part],
    band_of: dict[int, str],
    max_iters: int = 10,
) -> None:
    """Shift same-band parts that are too close outward until spacing clears."""
    pids = [id(p) for p in parts if id(p) in positions]
    threshold = SAME_BAND_SPACING_MM * 0.9

    for _ in range(max_iters):
        changed = False
        for i, pid in enumerate(pids):
            for qid in pids[i + 1:]:
                if band_of.get(pid) != band_of.get(qid):
                    continue
                px, py = positions[pid]
                qx, qy = positions[qid]
                dy = abs(py - qy)
                dx = abs(px - qx)
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < threshold:
                    shift = SAME_BAND_SPACING_MM - (dy if dy >= dx else dx) + 1.27
                    if dy >= dx:
                        positions[qid] = (_snap(qx), _snap(qy + shift))
                    else:
                        positions[qid] = (_snap(qx + shift), _snap(qy))
                    changed = True
        if not changed:
            break


# ---------------------------------------------------------------------------
# Stage 8 — Page sizing
# ---------------------------------------------------------------------------

def sheet_size_for_layout(
    positions: dict[int, tuple[float, float]],
) -> tuple[float, float]:
    """Return the smallest A-series sheet (w, h) that contains the layout."""
    if not positions:
        return 297.0, 210.0
    max_x = max(x for x, _ in positions.values()) + PAGE_MARGIN_MM
    max_y = max(y for _, y in positions.values()) + PAGE_MARGIN_MM
    for sw, sh in ((297, 210), (420, 297), (594, 420), (841, 594)):
        if max_x <= sw and max_y <= sh:
            return float(sw), float(sh)
    return max_x, max_y


# ---------------------------------------------------------------------------
# Phase 2.5a shims — kept for backward compatibility with existing tests
# ---------------------------------------------------------------------------

GRID_SPACING_MM: float = 40.0
ORIGIN_X_MM: float = 30.0
ORIGIN_Y_MM: float = 30.0
COLS: int = 6


def grid_place(parts: list[Part]) -> dict[int, tuple[float, float]]:
    """Naive grid placement (Phase 2.5a). Kept for tests."""
    positions: dict[int, tuple[float, float]] = {}
    for idx, part in enumerate(parts):
        col = idx % COLS
        row = idx // COLS
        x = _snap(ORIGIN_X_MM + col * GRID_SPACING_MM)
        y = _snap(ORIGIN_Y_MM + row * GRID_SPACING_MM)
        positions[id(part)] = (x, y)
    return positions


def sheet_size_mm(n_parts: int) -> tuple[float, float]:
    """Minimum bounding sheet size for n_parts (Phase 2.5a shim)."""
    rows = math.ceil(n_parts / COLS) if n_parts else 1
    cols_used = min(n_parts, COLS)
    w = ORIGIN_X_MM * 2 + cols_used * GRID_SPACING_MM
    h = ORIGIN_Y_MM * 2 + rows * GRID_SPACING_MM
    for sw, sh in ((297, 210), (420, 297), (594, 420), (841, 594)):
        if w <= sw and h <= sh:
            return float(sw), float(sh)
    return w, h
