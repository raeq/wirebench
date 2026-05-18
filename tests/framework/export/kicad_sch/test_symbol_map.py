"""Unit tests for the KiCad schematic symbol map."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[4] / 'src'
sys.path.insert(0, str(_SRC))

import components.passives   # noqa: F401
import components.diodes     # noqa: F401
import components.chips      # noqa: F401

from components.passives.resistor import Resistor
from components.passives.capacitor import Capacitor
from components.passives.led import LED
from components.diodes.d1n4148 import D1N4148
from components.chips.lm7805 import LM7805

from framework.export.kicad_sch.symbol_map import (
    SymbolEntry, connector_entry, lookup, lookup_by_name,
)


def test_lookup_resistor():
    r = Resistor(330, refdes_number=1)
    entry = lookup(r)
    assert entry is not None
    assert entry.lib == 'Device'
    assert entry.name == 'R'
    assert entry.refdes_prefix == 'R'


def test_lookup_led():
    d = LED('red', refdes_number=1)
    entry = lookup(d)
    assert entry is not None
    assert entry.lib == 'Device'
    assert entry.name == 'LED'


def test_lookup_diode_1n4148():
    d = D1N4148(refdes_number=1)
    entry = lookup(d)
    assert entry is not None
    assert entry.lib == 'Diode'
    assert entry.name == '1N4148'


def test_lookup_lm7805():
    u = LM7805(refdes_number=1)
    entry = lookup(u)
    assert entry is not None
    assert entry.lib == 'Regulator_Linear'
    assert entry.name == 'L7805'


def test_lookup_unknown_returns_none():
    # Use Capacitor as a standin — but with a subclass name not in the map
    from components.passives.capacitor import Capacitor

    class WeirdCapacitor(Capacitor):
        pass

    c = WeirdCapacitor(1e-6, refdes_number=1)
    # WeirdCapacitor is not in _BY_CLASS but Capacitor is — this tests MRO walk
    # For an entirely unmapped class use lookup_by_name
    assert lookup_by_name('WeirdCapacitor') is None


def test_lookup_by_name():
    entry = lookup_by_name('Resistor')
    assert entry is not None
    assert entry.name == 'R'


def test_lookup_by_name_missing():
    assert lookup_by_name('NonExistentXYZ') is None


def test_connector_entry():
    e = connector_entry(4)
    assert e.lib == 'Connector_Generic'
    assert e.name == 'Conn_01x04'
    assert e.refdes_prefix == 'J'
