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

    Zero-length and duplicate segments are filtered out: multiple pins
    snapping to the same grid point would otherwise produce overlapping
    wires and inflate `find_junctions` endpoint counts into false dots.
    """
    if len(pin_ends) < 2:
        return []

    # Snap then de-duplicate — two pins landing on the same grid point
    # would generate a zero-length L-shape pair below.
    snapped = sorted({(_snap(x), _snap(y)) for x, y in pin_ends})
    if len(snapped) < 2:
        return []

    raw: list[Segment] = []
    for i in range(len(snapped) - 1):
        ax, ay = snapped[i]
        bx, by = snapped[i + 1]

        if abs(ay - by) < 0.001:
            raw.append(((ax, ay), (bx, by)))
        elif abs(ax - bx) < 0.001:
            raw.append(((ax, ay), (bx, by)))
        else:
            # L-shape: horizontal then vertical.
            raw.append(((ax, ay), (bx, ay)))
            raw.append(((bx, ay), (bx, by)))

    # Drop zero-length segments and dedupe by canonical (sorted-endpoint)
    # form so a segment and its reverse don't both ship.
    seen: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    segments: list[Segment] = []
    for a, b in raw:
        if a == b:
            continue
        key = (a, b) if a <= b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        segments.append((a, b))

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
