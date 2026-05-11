"""Golden-file regression test for the Yosys JSON adapter.

Refresh:
    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/yosys/test_yosys_golden.py

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
import framework.export.yosys  # noqa: F401

from framework.export import export_to_string

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


GOLDEN_DIR = Path(__file__).resolve().parents[3] / 'golden' / 'yosys'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'water_alarm.json'),
    (WaterAlarmAssembly, 'water_alarm_assembly.json'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_yosys_output_matches_golden(factory, filename):
    actual = export_to_string(_silently(factory), 'yosys')
    path = GOLDEN_DIR / filename
    if os.environ.get('UPDATE_GOLDEN'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual)
        pytest.skip(f"golden refreshed: {path}")
    if not path.exists():
        pytest.fail(
            f"Golden missing: {path}\n"
            f"Seed with: UPDATE_GOLDEN=1 python -m pytest {__file__}"
        )
    expected = path.read_text()
    assert actual == expected, (
        f"Yosys output differs from golden {path.name}.\n"
        f"Refresh deliberately with UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
