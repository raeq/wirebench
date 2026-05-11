"""Golden-file regression test for the BOM CSV adapter.

Refresh with:
    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/bom/test_bom_golden.py

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.bom  # noqa: F401

from framework.export import export_to_string

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


GOLDEN_DIR = Path(__file__).resolve().parents[3] / 'golden' / 'bom'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'water_alarm.csv'),
    (WaterAlarmAssembly, 'water_alarm_assembly.csv'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_bom_output_matches_golden(factory, filename):
    design = _silently(factory)
    actual = export_to_string(design, 'bom')
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
        f"BOM output differs from golden {path.name}.\n"
        f"If this change is deliberate, refresh with:\n"
        f"    UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
