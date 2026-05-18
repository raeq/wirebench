"""Tests for the Phase 2.5b Layered Signal Flow placement algorithm."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

import components.chips      # noqa: F401
import components.passives   # noqa: F401
import components.connectors # noqa: F401
import components.diodes     # noqa: F401

from framework.export.nets import compute_logical_nets
from framework.export.kicad_sch.placement import (
    INTER_BAND_GUTTER_MM,
    PAGE_MARGIN_MM,
    SAME_BAND_SPACING_MM,
    _part_band,
    _bfs_layers,
    _build_adj,
    layered_place,
    sheet_size_for_layout,
)


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


# ---------------------------------------------------------------------------
# Band classification
# ---------------------------------------------------------------------------

def test_rail_goes_to_power_band():
    from components.passives.rail import Rail
    r = Rail(True)
    assert _part_band(r) == 'power'


def test_led_goes_to_indicator_band():
    from components.passives.led import LED
    d = LED('red', refdes_number=1)
    assert _part_band(d) == 'indicator'


def test_resistor_goes_to_signal_band():
    from components.passives.resistor import Resistor
    r = Resistor(330, refdes_number=1)
    assert _part_band(r) == 'signal'


def test_lm7805_goes_to_power_band():
    from components.chips.lm7805 import LM7805
    u = LM7805(refdes_number=1)
    assert _part_band(u) == 'power'


# ---------------------------------------------------------------------------
# layered_place
# ---------------------------------------------------------------------------

def test_layered_place_hello_led_positions():
    from hello_led import HelloLED
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)
    assert len(positions) == len(non_rail)


def test_layered_place_all_positions_on_grid():
    """Every coordinate must snap to the 1.27 mm grid."""
    from hello_led import HelloLED
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)
    for pid, (x, y) in positions.items():
        assert abs(round(x / 1.27) * 1.27 - x) < 0.001, f"x={x} not on grid"
        assert abs(round(y / 1.27) * 1.27 - y) < 0.001, f"y={y} not on grid"


def test_layered_place_deterministic():
    """Two calls on the same design must produce identical positions."""
    from hello_led import HelloLED
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    p1 = layered_place(non_rail, nets)
    p2 = layered_place(non_rail, nets)
    assert p1 == p2


def test_layered_place_minimum_spacing():
    """No two parts in the same band should be closer than 0.9× SAME_BAND_SPACING."""
    from hello_led import HelloLED
    import math
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    from framework.export.kicad_sch.placement import _part_band
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)
    parts = non_rail
    threshold = SAME_BAND_SPACING_MM * 0.9
    for i, p in enumerate(parts):
        for q in parts[i + 1:]:
            if _part_band(p) != _part_band(q):
                continue
            if id(p) not in positions or id(q) not in positions:
                continue
            px, py = positions[id(p)]
            qx, qy = positions[id(q)]
            dist = math.sqrt((px - qx) ** 2 + (py - qy) ** 2)
            assert dist >= threshold * 0.99, (
                f"{p!r} and {q!r} are only {dist:.2f} mm apart "
                f"(threshold {threshold:.2f} mm)"
            )


def test_layered_place_power_band_above_signal_band():
    """Power band parts must have smaller Y (higher on page) than signal band."""
    from water_alarm import WaterAlarm
    design = _silently(WaterAlarm)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    from framework.export.kicad_sch.placement import _part_band
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)

    power_ys = [positions[id(p)][1] for p in non_rail
                if id(p) in positions and _part_band(p) == 'power']
    signal_ys = [positions[id(p)][1] for p in non_rail
                 if id(p) in positions and _part_band(p) == 'signal']

    if power_ys and signal_ys:
        assert max(power_ys) < min(signal_ys), (
            f"Power band max Y={max(power_ys):.2f} >= signal band min Y={min(signal_ys):.2f}"
        )


def test_layered_place_indicator_band_below_signal_band():
    """Indicator band parts must have larger Y (lower on page) than signal band."""
    from hello_led import HelloLED
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    from framework.export.kicad_sch.placement import _part_band
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)

    signal_ys = [positions[id(p)][1] for p in non_rail
                 if id(p) in positions and _part_band(p) == 'signal']
    indicator_ys = [positions[id(p)][1] for p in non_rail
                    if id(p) in positions and _part_band(p) == 'indicator']

    if signal_ys and indicator_ys:
        assert max(signal_ys) < min(indicator_ys), (
            f"Signal band max Y={max(signal_ys):.2f} >= "
            f"indicator band min Y={min(indicator_ys):.2f}"
        )


def test_layered_place_parts_within_page_margin():
    """All placed parts must be at least PAGE_MARGIN_MM from the origin."""
    from hello_led import HelloLED
    design = _silently(HelloLED)
    from components.passives.rail import Rail
    from framework.export.kicad_sch.renderer import _collect_leaf_parts
    nets = compute_logical_nets(design)
    non_rail = [p for p in _collect_leaf_parts(design) if not isinstance(p, Rail)]
    positions = layered_place(non_rail, nets)
    for pid, (x, y) in positions.items():
        assert x >= PAGE_MARGIN_MM - 0.01
        assert y >= PAGE_MARGIN_MM - 0.01


# ---------------------------------------------------------------------------
# sheet_size_for_layout
# ---------------------------------------------------------------------------

def test_sheet_size_empty():
    assert sheet_size_for_layout({}) == (297.0, 210.0)


def test_sheet_size_small_layout_fits_a4():
    # Two points well within A4 (297×210)
    pos = {1: (50.0, 50.0), 2: (100.0, 100.0)}
    sw, sh = sheet_size_for_layout(pos)
    assert (sw, sh) == (297.0, 210.0)


def test_sheet_size_large_layout_grows_to_a3():
    # Points that exceed A4 but fit A3 (420×297)
    pos = {1: (50.0, 50.0), 2: (350.0, 200.0)}
    sw, sh = sheet_size_for_layout(pos)
    assert (sw, sh) == (420.0, 297.0)
