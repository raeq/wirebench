"""Placement tests for the breadboard visualiser.

The breadboard renderer shares its placement layer with the assembly
guide (acceptance criterion 8) — these tests verify the wrapper hands
back the same `ComponentPlacement` tuples assembly_guide consumes, and
that refusal / capacity rules fire as the spec requires.
"""
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

import components.chips        # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import components.diodes       # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import framework.export.assembly_guide   # noqa: F401, E402
import framework.export.breadboard       # noqa: F401, E402

from framework.errors import BreadboardIncompatibleError  # noqa: E402

from framework.export.breadboard.placement import (   # noqa: E402
    collect_parts, place_design, refuse_unsupported,
)

from hello_led import HelloLED                           # noqa: E402
from water_alarm import WaterAlarm                       # noqa: E402
from water_alarm_split import WaterAlarmAssembly         # noqa: E402


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def test_hello_led_places_resistor_and_led():
    """HelloLED has just R1 and D1. The placement output should contain
    both, each with two pins, on the top bank (rows A..E)."""
    design = _silently(HelloLED)
    _all, placeable = collect_parts(design)
    refuse_unsupported(design, placeable)
    result = place_design(placeable)
    refdes = {c.component.refdes for c in result.components}
    assert refdes == {'R1', 'D1'}
    for c in result.components:
        assert len(c.pins) == 2
        for _, pp in c.pins:
            assert pp.row in 'ABCDE'


def test_placement_is_deterministic():
    """Same input → byte-identical placement positions across runs."""
    design1 = _silently(HelloLED)
    design2 = _silently(HelloLED)
    r1 = place_design(collect_parts(design1)[1])
    r2 = place_design(collect_parts(design2)[1])
    pos1 = [(c.component.refdes, c.pins) for c in r1.components]
    pos2 = [(c.component.refdes, c.pins) for c in r2.components]
    assert pos1 == pos2


def test_refuse_multi_board():
    """Multi-board designs (WaterAlarmAssembly) are refused for v1."""
    design = _silently(WaterAlarmAssembly)
    _all, placeable = collect_parts(design)
    with pytest.raises(BreadboardIncompatibleError, match='Multi-board'):
        refuse_unsupported(design, placeable)


def test_dip_chip_straddles_trough():
    """A chip is placed with pins on both top (E) and bottom (F) banks."""
    from framework.chip import Chip
    design = _silently(WaterAlarm)
    _all, placeable = collect_parts(design)
    refuse_unsupported(design, placeable)
    result = place_design(placeable)
    chips = [c for c in result.components if isinstance(c.component, Chip)]
    assert chips, "WaterAlarm should contain at least one chip"
    # Find a chip whose pins span both banks.
    found_straddler = False
    for chip_pl in chips:
        rows = {pp.row for _, pp in chip_pl.pins}
        has_top = bool(rows & set('ABCDE'))
        has_bot = bool(rows & set('FGHIJ'))
        if has_top and has_bot:
            found_straddler = True
            break
    assert found_straddler, (
        "At least one chip should straddle the trough (pins on E and F rows)"
    )
