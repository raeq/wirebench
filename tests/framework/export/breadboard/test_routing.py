"""Routing / colour tests for the breadboard visualiser.

Verify that the routing layer assigns the locked palette (red for +,
black for −, analog vs digital signal cycles) and that the two
reserved colours never leak into the signal palette cycle.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

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

from framework.export.breadboard import colors           # noqa: E402
from framework.export.breadboard.placement import (      # noqa: E402
    collect_parts, place_design,
)
from framework.export.breadboard.routing import (         # noqa: E402
    JumperKind, route_jumpers,
)

from hello_led import HelloLED                            # noqa: E402
from water_alarm import WaterAlarm                        # noqa: E402


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _jumpers_for(design_cls):
    design = _silently(design_cls)
    all_parts, placeable = collect_parts(design)
    placements = place_design(placeable)
    return route_jumpers(all_parts, placements.by_component)


def test_plus_rail_jumpers_are_red():
    """Every jumper landing on the + rail uses the reserved red hex."""
    for j in _jumpers_for(HelloLED):
        if j.kind == JumperKind.RAIL_PLUS:
            assert j.color == colors.RAIL_PLUS_JUMPER == '#cc0000'


def test_minus_rail_jumpers_are_black():
    """Every jumper landing on the − rail uses the reserved black hex."""
    for j in _jumpers_for(HelloLED):
        if j.kind == JumperKind.RAIL_MINUS:
            assert j.color == colors.RAIL_MINUS_JUMPER == '#000000'


def test_reserved_colors_never_appear_in_signal_palettes():
    """The two reserved hex codes are off-limits to the signal cycles
    (acceptance criterion 5)."""
    assert colors.RAIL_PLUS_JUMPER not in colors.ANALOG_PALETTE
    assert colors.RAIL_PLUS_JUMPER not in colors.DIGITAL_PALETTE
    assert colors.RAIL_MINUS_JUMPER not in colors.ANALOG_PALETTE
    assert colors.RAIL_MINUS_JUMPER not in colors.DIGITAL_PALETTE


def test_signal_color_is_stable_across_calls():
    """Same ordinal → same colour. Ordinals wrap deterministically at
    palette size."""
    assert colors.analog_color(0) == colors.analog_color(0)
    assert colors.digital_color(0) == colors.digital_color(0)
    # Palette wrap: ordinal N and N+palette_size return the same colour.
    assert colors.analog_color(0) == colors.analog_color(len(colors.ANALOG_PALETTE))
    assert colors.digital_color(0) == colors.digital_color(len(colors.DIGITAL_PALETTE))


def test_adjacent_ordinals_get_distinct_colors():
    """Two nets with adjacent ordinals get different colours — this is
    the property that keeps two visually-adjacent jumpers on the board
    from landing on the same colour."""
    for i in range(len(colors.ANALOG_PALETTE) - 1):
        assert colors.analog_color(i) != colors.analog_color(i + 1)
    for i in range(len(colors.DIGITAL_PALETTE) - 1):
        assert colors.digital_color(i) != colors.digital_color(i + 1)


def test_water_alarm_has_both_rail_and_signal_jumpers():
    """A realistic design has a mix of rail jumpers and signal jumpers."""
    jumpers = _jumpers_for(WaterAlarm)
    kinds = {j.kind for j in jumpers}
    assert JumperKind.RAIL_PLUS in kinds
    assert JumperKind.RAIL_MINUS in kinds
    # At least one signal jumper too.
    assert (JumperKind.ANALOG in kinds) or (JumperKind.DIGITAL in kinds)
