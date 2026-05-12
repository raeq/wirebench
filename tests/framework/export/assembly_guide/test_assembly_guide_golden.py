"""Golden-file regression test for the assembly-guide adapter.

Refresh with:
    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/assembly_guide/test_assembly_guide_golden.py

The golden files live under `tests/golden/assembly_guide/` — one
`.md` per breadboard-compatible demo.  Multi-board and SMD-containing
demos are intentionally not covered because the exporter refuses them.
"""
from __future__ import annotations

import os
import sys
import warnings
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
import framework.export.assembly_guide  # noqa: F401 — register adapter

from framework.export import export_to_string

from hello_led import HelloLED                  
from water_alarm import WaterAlarm              
from dice import Dice                           
from digital_thermometer import DigitalThermometer
from doorbell_protector import DoorbellProtector


GOLDEN_DIR = Path(__file__).resolve().parents[3] / 'golden' / 'assembly_guide'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (HelloLED,            'hello_led.md'),
    (WaterAlarm,          'water_alarm.md'),
    (Dice,                'dice.md'),
    (DigitalThermometer,  'digital_thermometer.md'),
    (DoorbellProtector,   'doorbell_protector.md'),
], ids=['HelloLED', 'WaterAlarm', 'Dice', 'DigitalThermometer', 'DoorbellProtector'])
def test_assembly_guide_matches_golden(factory, filename):
    design = _silently(factory)
    actual = export_to_string(design, 'assembly_guide')
    path = GOLDEN_DIR / filename
    if os.environ.get('UPDATE_GOLDEN'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual)
        pytest.skip(f"golden refreshed: {path}")
    if not path.exists():
        pytest.fail(
            f"Golden file missing: {path}\n"
            f"Seed with: UPDATE_GOLDEN=1 python -m pytest {__file__}"
        )
    expected = path.read_text()
    assert actual == expected, (
        f"Assembly-guide output differs from golden {path.name}.\n"
        f"If this change is deliberate, refresh with:\n"
        f"    UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
