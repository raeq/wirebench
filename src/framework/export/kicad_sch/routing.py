"""Orthogonal wire routing for the KiCad schematic emitter — Phase 2.5b.

Each net's pin stub ends are connected by Manhattan (horizontal + vertical)
wire segments. Junctions are emitted at points where three or more segment
endpoints meet (indicating a T- or X-junction in the schematic).

The router uses a simple chain strategy: pins are sorted by X (then Y) and
connected pairwise with L-shaped routes — horizontal first, then vertical.
This is deterministic, fast, and produces clean schematics for the layered
placement that Phase 2.5b uses.
"""
from __future__ import annotations

from collections import defaultdict

# A wire segment as two (x, y) endpoint pairs.
Segment = tuple[tuple[float, float], tuple[float, float]]


def _snap(v: float) -> float:
    """Snap to 1.27 mm (50-mil) grid."""
    return round(v / 1.27) * 1.27


def route_net(
    pin_ends: list[tuple[float, float]],
) -> list[Segment]:
    """Route Manhattan segments connecting all stub ends in one net.

    Connects pins in X-sorted order using L-shapes (horizontal first).
    Returns a list of (start, end) tuples where each segment is purely
    horizontal or purely vertical.
    """
    if len(pin_ends) < 2:
        return []

    pts = sorted((_snap(x), _snap(y)) for x, y in pin_ends)
    segments: list[Segment] = []

    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]

        if abs(ay - by) < 0.001:
            # Same Y — single horizontal segment.
            segments.append(((ax, ay), (bx, by)))
        elif abs(ax - bx) < 0.001:
            # Same X — single vertical segment.
            segments.append(((ax, ay), (bx, by)))
        else:
            # L-shape: go horizontal first (to bx), then vertical.
            segments.append(((ax, ay), (bx, ay)))
            segments.append(((bx, ay), (bx, by)))

    return segments


def find_junctions(
    all_segments: list[Segment],
) -> list[tuple[float, float]]:
    """Return grid points where three or more wire endpoints coincide.

    KiCad requires an explicit `(junction ...)` element wherever three or
    more wire segments share an endpoint (the schematic "dot").
    """
    count: dict[tuple[float, float], int] = defaultdict(int)
    for (x1, y1), (x2, y2) in all_segments:
        count[(_snap(x1), _snap(y1))] += 1
        count[(_snap(x2), _snap(y2))] += 1
    return [(x, y) for (x, y), n in count.items() if n >= 3]
