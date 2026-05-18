"""Unit tests for the KiCad symbol library loader."""
from __future__ import annotations

import pytest

from framework.export.kicad_sch.library_loader import (
    PinDef, collect_lib_symbols, get_pin_defs,
)


def test_get_pin_defs_resistor():
    pins = get_pin_defs('Device', 'R')
    assert len(pins) == 2
    nums = {p.number for p in pins}
    assert nums == {'1', '2'}
    # Both pins are on the vertical axis
    for p in pins:
        assert p.x == pytest.approx(0.0, abs=0.01)
        assert abs(p.y) == pytest.approx(3.81, abs=0.01)


def test_get_pin_defs_led():
    pins = get_pin_defs('Device', 'LED')
    assert len(pins) == 2
    nums = {p.number for p in pins}
    assert nums == {'1', '2'}
    # LED pins are on the horizontal axis
    for p in pins:
        assert p.y == pytest.approx(0.0, abs=0.01)
        assert abs(p.x) == pytest.approx(3.81, abs=0.01)


def test_get_pin_defs_resolves_extends():
    """1N4148 extends 1N4001 — pins must resolve through the extends chain."""
    pins = get_pin_defs('Diode', '1N4148')
    assert len(pins) == 2


def test_get_pin_defs_power_gnd():
    pins = get_pin_defs('power', 'GND')
    assert len(pins) == 1
    assert pins[0].number == '1'


def test_get_pin_defs_unknown_returns_empty():
    pins = get_pin_defs('Device', 'NonExistentSymbol_XYZ')
    assert pins == []


def test_collect_lib_symbols_includes_requested():
    result = collect_lib_symbols([('Device', 'R')])
    assert 'Device:R' in result
    assert 'symbol "Device:R"' in result['Device:R']


def test_collect_lib_symbols_qualifies_subsymbols():
    result = collect_lib_symbols([('Device', 'R')])
    sym_text = result['Device:R']
    # Only the top-level symbol gets the lib: prefix; sub-symbols stay bare.
    # KiCad 9 schematics use bare names for nested sub-units.
    assert 'symbol "R_0_1"' in sym_text or 'symbol "R_1_1"' in sym_text
    # And the old qualified names must NOT appear (would break KiCad 9)
    assert 'symbol "Device:R_0_1"' not in sym_text
    assert 'symbol "Device:R_1_1"' not in sym_text


def test_collect_lib_symbols_resolves_extends_chain():
    """1N4148 extends 1N4001 — parent must appear in result."""
    result = collect_lib_symbols([('Diode', '1N4148')])
    assert 'Diode:1N4001' in result
    assert 'Diode:1N4148' in result


def test_collect_lib_symbols_deduplicates():
    result = collect_lib_symbols([('Device', 'R'), ('Device', 'R')])
    assert list(result.keys()).count('Device:R') == 1


def test_collect_lib_symbols_unknown_ignored():
    result = collect_lib_symbols([('Device', 'NonExistentSymbol_XYZ')])
    assert 'Device:NonExistentSymbol_XYZ' not in result
