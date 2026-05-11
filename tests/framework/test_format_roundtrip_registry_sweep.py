"""Parametrised round-trip sweep over every class in the component
registry.  Catches refdes-collision regressions, pin-id serialisation
bugs, and any new-component class that doesn't survive
save_circuitry → load_circuitry.

Default construction is `cls(refdes_number=1)`.  Parts whose
constructor needs more than that are listed in `_OVERRIDES`.  Parts
that have no sensible round-trip-able default — abstract bases,
families parameterised by pin count, parts whose constructor signature
genuinely diverges from the convention — are listed in `_SKIP` with a
documented reason.
"""
from __future__ import annotations

import warnings

import pytest

# Trigger registration of every component.
import components.chips        # noqa: F401
import components.connectors   # noqa: F401
import components.diodes       # noqa: F401
import components.passives     # noqa: F401
import components.transistors  # noqa: F401
import framework.board         # noqa: F401

from framework.circuit import Circuit
from framework.format import load_circuitry, save_circuitry
from framework.registry import lookup, registered_names


def _passive(name, **kwargs):
    return lambda n: lookup(name)(refdes_number=n, **kwargs)


def _connector(name, **kwargs):
    """Pin-count-parameterised connector families — pass pin_count
    (and pitch if applicable) alongside refdes_number."""
    return lambda n: lookup(name)(refdes_number=n, **kwargs)


_OVERRIDES = {
    'Resistor': _passive('Resistor', ohms=330),
    'LED':      _passive('LED',      color='red'),
    'Rail':     lambda n: lookup('Rail')(level=True),
    # Pin-count-parameterised connector families.
    'Header1xNFemale':   _connector('Header1xNFemale',   pin_count=4, pitch_mm=2.54),
    'Header1xNMale':     _connector('Header1xNMale',     pin_count=4, pitch_mm=2.54),
    'Header2xNFemale':   _connector('Header2xNFemale',   pin_count=4, pitch_mm=2.54),
    'Header2xNMale':     _connector('Header2xNMale',     pin_count=4, pitch_mm=2.54),
    'IDC2xNMale':        _connector('IDC2xNMale',        pin_count=10, pitch_mm=2.54),
    'IDC2xNSocket':      _connector('IDC2xNSocket',      pin_count=10, pitch_mm=2.54),
    'ScrewTerminalBlock': _connector('ScrewTerminalBlock', pin_count=4, pitch_mm=5.08),
    'JSTPHBoardSide':    _connector('JSTPHBoardSide',    pin_count=4),
    'JSTPHCableHousing': _connector('JSTPHCableHousing', pin_count=4),
    'JSTXHBoardSide':    _connector('JSTXHBoardSide',    pin_count=4),
    'JSTXHCableHousing': _connector('JSTXHCableHousing', pin_count=4),
    'JSTSHBoardSide':    _connector('JSTSHBoardSide',    pin_count=4),
    'JSTSHCableHousing': _connector('JSTSHCableHousing', pin_count=4),
    'JSTGHBoardSide':    _connector('JSTGHBoardSide',    pin_count=4),
    'JSTGHCableHousing': _connector('JSTGHCableHousing', pin_count=4),
}

_SKIP: dict[str, str] = {
    'Board': 'abstract base; concrete boards covered by their own round-trip tests',
}


def _silently(fn, *args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*args, **kwargs)


@pytest.mark.parametrize('name', sorted(registered_names()))
def test_component_roundtrip(name, tmp_path):
    if name in _SKIP:
        pytest.skip(_SKIP[name])
    factory = _OVERRIDES.get(name, lambda n: lookup(name)(refdes_number=n))
    part = factory(1)
    # Expose the part's ports as the wrapper's surface so any mandatory
    # ports are considered "boundary" by Circuit._validate. Without this,
    # parts like LED (mandatory anode) fail unconnected-port validation.
    wrapper = Circuit(factor_nodes=[part], ports=dict(part.ports))

    p1 = tmp_path / 'a.circuitry'
    _silently(save_circuitry, wrapper, p1)
    loaded = _silently(load_circuitry, p1)

    assert len(loaded._factor_nodes) == 1, (
        f"{name}: loaded circuit has {len(loaded._factor_nodes)} components, "
        f"expected 1")
    loaded_part = loaded._factor_nodes[0]
    assert type(loaded_part).__name__ == name, (
        f"{name}: loaded component is {type(loaded_part).__name__}")

    p2 = tmp_path / 'b.circuitry'
    _silently(save_circuitry, loaded, p2)
    assert p1.read_text() == p2.read_text(), (
        f"{name}: re-save not byte-identical (non-deterministic round-trip)")
