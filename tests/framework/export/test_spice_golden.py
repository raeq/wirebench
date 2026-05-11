"""Golden-file regression test for the SPICE exporter.

For each application the rendered SPICE deck is compared byte-for-byte
against a checked-in golden file under tests/golden/spice/. Any change
in the exporter's output — pin reorder, renamed net, reformatted line
— must surface as a deliberate diff in the PR that introduced it.

When a change is genuinely expected, refresh the goldens:

    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/test_spice_golden.py

The diff in the resulting commit *is* the record of what changed.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import pytest

# Trigger registrations.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.spice  # noqa: F401

from framework.export import export_to_string
from framework.export.base import ExportConfig

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


GOLDEN_DIR = Path(__file__).resolve().parents[2] / 'golden' / 'spice'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'water_alarm.cir'),
    (WaterAlarmAssembly, 'water_alarm_assembly.cir'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_spice_output_matches_golden(factory, filename):
    design = _silently(factory)
    # Header comment carries a timestamp — disable so the deck is
    # byte-stable across runs.
    actual = export_to_string(
        design, 'spice',
        config=ExportConfig(include_header_comment=False),
    )

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
        f"SPICE output differs from golden {path.name}.\n"
        f"If this change is deliberate, refresh with:\n"
        f"    UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
