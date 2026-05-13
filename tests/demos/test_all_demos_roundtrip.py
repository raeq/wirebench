"""Round-trip tests for every demo construction.

The framework's extension-record path (see `framework/format_extension.py`)
plus the per-class `SERIALIZE_KWARGS` declarations are what let a demo
save its design through `save_wirebench` and reload it with
`load_wirebench`.  This module proves that every top-level construct
in `demos/*.py` roundtrips structurally:

    - same number of factor_nodes
    - same set of refdes strings on refdes-bearing children
    - second `save_wirebench` produces a byte-identical file (proves
      determinism — the JSON output is canonical)

It does not assert behavioural equivalence (the demos run scenarios,
which are tested in each demo's own test module).  This is a
structural-equivalence check at the file-format layer.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pytest

# Trigger registration of every chip / passive / connector and every
# demo's locally-defined subclasses.  Without these imports the
# registry only has core library parts and load_wirebench can't find
# demo-local classes like Uno_ThermometerSketch.
import components.chips        # noqa: F401
import components.passives     # noqa: F401
import components.connectors   # noqa: F401
import framework.board         # noqa: F401

import water_alarm              # noqa: F401
import water_alarm_split        # noqa: F401
import dice                     # noqa: F401
import digital_thermometer      # noqa: F401
import doorbell_protector       # noqa: F401
import backup_power             # noqa: F401
import fan_cooling              # noqa: F401
import bldc_motor               # noqa: F401
import isolated_rs232           # noqa: F401
import li_ion_fuel_gauge        # noqa: F401

from framework.format import load_wirebench, save_wirebench
from framework.refdes import RefdesBearing


def _silent(fn, *a, **kw):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **kw)


def _refdes_set(c) -> set[str]:
    return {fn.refdes for fn in c._factor_nodes if isinstance(fn, RefdesBearing)}


# Each entry is (label, callable returning the live demo construct).
_FACTORIES = [
    ('water_alarm.WaterAlarm',
        lambda: __import__('water_alarm').WaterAlarm()),
    ('water_alarm_split.SensorBoard',
        lambda: __import__('water_alarm_split').SensorBoard(refdes_number=1)),
    ('water_alarm_split.ControllerBoard',
        lambda: __import__('water_alarm_split').ControllerBoard(refdes_number=2)),
    ('water_alarm_split.WaterAlarmAssembly',
        lambda: __import__('water_alarm_split').WaterAlarmAssembly()),
    ('dice.Dice',
        lambda: __import__('dice').Dice()),
    ('digital_thermometer.DigitalThermometer',
        lambda: __import__('digital_thermometer').DigitalThermometer()),
    ('doorbell_protector.DoorbellProtector',
        lambda: __import__('doorbell_protector').DoorbellProtector()),
    ('backup_power.BackupPower',
        lambda: __import__('backup_power').BackupPower()),
    ('fan_cooling.FanCoolingBoard',
        lambda: __import__('fan_cooling').FanCoolingBoard(refdes_number=1)),
    ('fan_cooling.CooledSystem',
        lambda: __import__('fan_cooling').CooledSystem()),
    ('bldc_motor.BLDCControllerBoard',
        lambda: __import__('bldc_motor').BLDCControllerBoard(refdes_number=1)),
    ('bldc_motor.BLDCSystem',
        lambda: __import__('bldc_motor').BLDCSystem()),
    ('isolated_rs232.IsolatedRS232Board',
        lambda: __import__('isolated_rs232').IsolatedRS232Board(refdes_number=1)),
    ('isolated_rs232.IsolatedRS232Link',
        lambda: __import__('isolated_rs232').IsolatedRS232Link()),
    ('li_ion_fuel_gauge.BatteryPackBoard',
        lambda: __import__('li_ion_fuel_gauge').BatteryPackBoard(refdes_number=1)),
]


@pytest.mark.parametrize("label,factory", _FACTORIES,
                         ids=[label for label, _ in _FACTORIES])
def test_demo_roundtrips_structurally(label, factory, tmp_path):
    original = factory()
    p1 = tmp_path / "a.wirebench"
    _silent(save_wirebench, original, p1)
    loaded = _silent(load_wirebench, p1)

    assert len(loaded._factor_nodes) == len(original._factor_nodes), (
        f"{label}: loaded has {len(loaded._factor_nodes)} factor_nodes, "
        f"original has {len(original._factor_nodes)}"
    )
    assert _refdes_set(loaded) == _refdes_set(original), (
        f"{label}: refdes set diverges"
    )


@pytest.mark.parametrize("label,factory", _FACTORIES,
                         ids=[label for label, _ in _FACTORIES])
def test_demo_resave_is_byte_identical(label, factory, tmp_path):
    """Save → load → re-save must produce a byte-for-byte identical
    file.  This proves the JSON output is canonical (deterministic
    key order, no spurious whitespace) and that the extension-record
    path correctly round-trips every kwarg it touched."""
    original = factory()
    p1 = tmp_path / "a.wirebench"
    p2 = tmp_path / "b.wirebench"

    _silent(save_wirebench, original, p1)
    loaded = _silent(load_wirebench, p1)
    _silent(save_wirebench, loaded, p2)

    assert p1.read_text() == p2.read_text(), (
        f"{label}: re-save is not byte-identical — non-deterministic "
        f"or kwarg lost in transit"
    )
