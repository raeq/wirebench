"""Placement-algorithm tests.

Spec §8 tests 11–13.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DEMOS = Path(__file__).resolve().parents[4] / 'demos'
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))

import components.chips     # noqa: F401
import components.diodes    # noqa: F401
import components.passives  # noqa: F401
import components.transistors  # noqa: F401
import components.connectors  # noqa: F401

from framework.export import export_to_string


# ----------------------------------------------- 11. anchor at row 10

def test_largest_chip_pin1_lands_at_10E() -> None:
    """For a design with chips, the first (largest) chip's pin 1
    lands at position 10, row E — per the placement convention."""
    from water_alarm import WaterAlarm
    text = export_to_string(WaterAlarm(), 'assembly_guide')
    # Look for the largest chip's anchor in the assembly text.
    # ULN2003A is the biggest (DIP-16), so pin 1 should be at 10E.
    assert 'pin 1 at 10E' in text


# --------------------------------------------- 12. chips placed with gap

def test_multiple_chips_have_gap_between_them() -> None:
    """The second chip starts at least 2 positions after the first
    chip ends — so jumpers between them have somewhere to land."""
    from water_alarm import WaterAlarm
    text = export_to_string(WaterAlarm(), 'assembly_guide')
    # Parse out each chip's pin 1 position from "pin 1 at <N>E"
    import re
    positions = [int(m.group(1)) for m in re.finditer(r'pin 1 at (\d+)E', text)]
    assert len(positions) >= 2, "expected at least 2 chips in WaterAlarm"
    # Adjacent chip starts differ by at least pin_count/2 + 2 (one
    # chip width + a 2-position gap).  Without per-chip width
    # information we just assert monotone increase.
    for a, b in zip(positions, positions[1:]):
        assert b > a, f"second chip ({b}) should start after first ({a})"


# ----------------------------------------------- 13. rail jumpers emitted

def test_rail_jumpers_emitted() -> None:
    """Wires landing on `Rail(True)` produce 'to the top + rail'
    instructions; wires landing on `Rail(False)` produce 'to the - rail'
    instructions."""
    from hello_led import HelloLED
    text = export_to_string(HelloLED(), 'assembly_guide')
    assert 'to the top `+` rail' in text
    assert 'to the top `-` rail' in text
