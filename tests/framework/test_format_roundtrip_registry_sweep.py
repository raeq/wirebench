"""Parametrised round-trip sweep over every class in the component
registry.  Catches refdes-collision regressions, pin-id serialisation
bugs, and any new-component class that doesn't survive
save_wirebench → load_wirebench.

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
from framework.format import load_wirebench, save_wirebench
from framework.registry import lookup, registered_names


def _passive(name, **kwargs):
    return lambda n: lookup(name)(refdes_number=n, **kwargs)


def _connector(name, **kwargs):
    """Pin-count-parameterised connector families — pass pin_count
    (and pitch if applicable) alongside refdes_number."""
    return lambda n: lookup(name)(refdes_number=n, **kwargs)


_OVERRIDES = {
    'Resistor':   _passive('Resistor',  ohms=330),
    'Capacitor':  _passive('Capacitor', farads=100e-9),
    'Inductor':   _passive('Inductor',  henries=100e-6),
    'LED':        _passive('LED',       color='red'),
    'Relay_SPDT': lambda n: lookup('Relay_SPDT')(refdes_number=n),
    'Rail':       lambda n: lookup('Rail')(level=True),
    'Cell':       lambda n: lookup('Cell')(
                              initial_state_of_charge=1.0, refdes_number=n,
                          ),
    'ISOW7841':   lambda n: lookup('ISOW7841')(
        refdes_number=n,
        iso_domain=__import__('framework.ground', fromlist=['GroundDomain'])
                       .GroundDomain('isolated_roundtrip'),
    ),
    # Concept cells — internal to chips / boards but registered for
    # extension-record save/load.  None of them are refdes-bearing.
    'Inverter':         lambda n: lookup('Inverter')(),
    'Monostable':       lambda n: lookup('Monostable')(duration_ms=120.0),
    'DiodeOR':          lambda n: lookup('DiodeOR')(input_names=('a', 'b')),
    'FanController':    lambda n: lookup('FanController')(),
    'BackupSupervisor': lambda n: lookup('BackupSupervisor')(),
    'BLDCMotor':        lambda n: lookup('BLDCMotor')(),
    'SeriesRectifier':  lambda n: lookup('SeriesRectifier')(v_f=0.3),
    'ZenerShunt':       lambda n: lookup('ZenerShunt')(v_z=5.1),
    'MOSFETSwitch':     lambda n: lookup('MOSFETSwitch')(channel='n'),
    'BJTSwitch':        lambda n: lookup('BJTSwitch')(polarity='npn'),
    'NE555_Monostable': lambda n: lookup('NE555_Monostable')(
                              duration_ms=120.0, refdes_number=n,
                          ),
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
    # Concrete demo boards are exercised by tests/demos/test_all_demos_roundtrip.py
    # — the generic sweep here just constructs each class with
    # refdes_number=1, which conflicts with the specific refdes
    # assignments and wiring topology those boards expect.
    'BLDCControllerBoard':   'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'BLDCSupplyBoard':       'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'BatteryPackBoard':      'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'ControllerSourceBoard': 'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'IsolatedRS232Board':    'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'PowerSourceBoard':      'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'RS232CableBoard':       'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'FanCoolingBoard':       'demo-local; covered by tests/demos/test_all_demos_roundtrip.py',
    'ISOW7841': ('multi-domain chip: __init__ requires a per-instance '
                 'iso_domain that does not fit the generic sweep record; '
                 'covered by test_isow7841.py'),
    'SeriesRectifier': ('concept cell with constructor v_f that isn\'t '
                        'serialised by the save format — it lives '
                        'inside a Chip instance whose __init__ rebuilds '
                        'it with the right v_f; never round-tripped '
                        'standalone'),
    'ZenerShunt': ('concept cell with constructor v_z, same shape as '
                   'SeriesRectifier'),
    'MOSFETSwitch': ('concept cell with constructor channel arg, same '
                     'shape as SeriesRectifier'),
    'BJTSwitch': ('concept cell with constructor polarity arg, same '
                  'shape as SeriesRectifier'),
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
    wrapper = Circuit(parts=[part], ports=dict(part.ports))

    p1 = tmp_path / 'a.wirebench'
    _silently(save_wirebench, wrapper, p1)
    loaded = _silently(load_wirebench, p1)

    assert len(loaded.parts) == 1, (
        f"{name}: loaded circuit has {len(loaded.parts)} components, "
        f"expected 1")
    loaded_part = loaded.parts[0]
    assert type(loaded_part).__name__ == name, (
        f"{name}: loaded component is {type(loaded_part).__name__}")

    p2 = tmp_path / 'b.wirebench'
    _silently(save_wirebench, loaded, p2)
    assert p1.read_text() == p2.read_text(), (
        f"{name}: re-save not byte-identical (non-deterministic round-trip)")
