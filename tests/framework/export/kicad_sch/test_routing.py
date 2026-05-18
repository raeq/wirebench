"""Tests for the Phase 2.5b orthogonal wire routing module."""
from __future__ import annotations

import pytest

from framework.export.kicad_sch.routing import find_junctions, route_net


# ---------------------------------------------------------------------------
# route_net
# ---------------------------------------------------------------------------

def test_route_net_empty():
    assert route_net([]) == []


def test_route_net_single_point():
    assert route_net([(10.0, 20.0)]) == []


def test_route_net_two_points_same_y():
    """Two pins at the same Y → single horizontal segment."""
    segs = route_net([(10.0, 20.0), (50.0, 20.0)])
    assert len(segs) == 1
    (x1, y1), (x2, y2) = segs[0]
    assert y1 == pytest.approx(y2, abs=0.001)
    assert x1 < x2


def test_route_net_two_points_same_x():
    """Two pins at the same X → single vertical segment."""
    segs = route_net([(10.0, 10.0), (10.0, 50.0)])
    assert len(segs) == 1
    (x1, y1), (x2, y2) = segs[0]
    assert x1 == pytest.approx(x2, abs=0.001)
    assert y1 < y2


def test_route_net_two_points_l_shape():
    """Two pins at different X and Y → two orthogonal segments."""
    segs = route_net([(10.0, 10.0), (50.0, 40.0)])
    assert len(segs) == 2
    # Verify all segments are purely horizontal or vertical.
    for (x1, y1), (x2, y2) in segs:
        assert (abs(x1 - x2) < 0.001) or (abs(y1 - y2) < 0.001)


def test_route_net_all_segments_orthogonal():
    """For any input, every segment must be H or V."""
    pts = [(10.0, 5.0), (30.0, 20.0), (60.0, 10.0), (80.0, 40.0)]
    segs = route_net(pts)
    for (x1, y1), (x2, y2) in segs:
        is_h = abs(y1 - y2) < 0.001
        is_v = abs(x1 - x2) < 0.001
        assert is_h or is_v, f"Diagonal segment: ({x1},{y1})→({x2},{y2})"


def test_route_net_segments_on_grid():
    """All segment endpoint coordinates must sit on the 1.27 mm grid."""
    pts = [(11.0, 7.0), (33.0, 22.0)]
    segs = route_net(pts)
    for (x1, y1), (x2, y2) in segs:
        for v in (x1, y1, x2, y2):
            assert abs(round(v / 1.27) * 1.27 - v) < 0.001


def test_route_net_three_pins_chain():
    """Three pins → two L-shapes (4 segments or fewer if some are colinear)."""
    segs = route_net([(10.0, 10.0), (50.0, 40.0), (90.0, 10.0)])
    # Two L-shapes → max 4 segments; colinear merging can reduce this.
    assert 2 <= len(segs) <= 4


def test_route_net_coincident_pins_dedup_to_nothing():
    """Two pins snapping to the same grid point must not emit a wire."""
    # Both points land on the same 1.27 mm grid cell after snapping.
    assert route_net([(10.0, 10.0), (10.0, 10.0)]) == []
    assert route_net([(10.0, 10.0), (10.1, 10.1)]) == []


def test_route_net_emits_no_zero_length_segments():
    """No emitted segment may have start == end."""
    segs = route_net([(10.0, 10.0), (50.0, 10.0), (50.0, 10.4)])
    for a, b in segs:
        assert a != b, f"zero-length segment emitted: {a}→{b}"


def test_route_net_emits_no_duplicate_segments():
    """A segment and its reverse must not both appear in the output."""
    segs = route_net([(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)])
    canonical = {
        (a, b) if a <= b else (b, a)
        for a, b in segs
    }
    assert len(canonical) == len(segs), (
        f"duplicate segments emitted: {len(segs)} raw, "
        f"{len(canonical)} canonical"
    )


# ---------------------------------------------------------------------------
# find_junctions
# ---------------------------------------------------------------------------

def test_find_junctions_none():
    """Two segments sharing one endpoint → no junction (only 2 meet)."""
    segs = [((0.0, 0.0), (10.0, 0.0)), ((10.0, 0.0), (20.0, 0.0))]
    junctions = find_junctions(segs)
    assert junctions == []


def test_find_junctions_three_way():
    """Three segments all ending at the same point → one junction."""
    # Use grid-snapped coordinates: round(10.0/1.27)*1.27 = 8*1.27 = 10.16
    g = round(10.0 / 1.27) * 1.27
    segs = [
        ((0.0, g), (g, g)),
        ((g, 0.0), (g, g)),
        ((g * 2, g), (g, g)),
    ]
    junctions = find_junctions(segs)
    assert len(junctions) == 1
    assert junctions[0] == pytest.approx((g, g), abs=0.001)


def test_find_junctions_snaps_to_grid():
    """Junction detection snaps coordinates before counting."""
    segs = [
        ((0.0, 10.0), (10.001, 10.0)),
        ((10.002, 0.0), (10.001, 10.0)),
        ((20.0, 10.0), (10.003, 10.0)),
    ]
    junctions = find_junctions(segs)
    assert len(junctions) == 1
