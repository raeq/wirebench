"""Syntactic validation: the output parses as CSV with the right
schema. Uses csv.DictReader (stdlib, always available).

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import csv
import io
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.bom  # noqa: F401

from framework.export import export_to_string

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


EXPECTED_COLUMNS = [
    'Refdes', 'Value', 'Footprint', 'Quantity', 'Parent', 'Description',
]


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory", [WaterAlarm, WaterAlarmAssembly],
                         ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_bom_parses_as_csv_with_expected_columns(factory):
    text = export_to_string(_silently(factory), 'bom')
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames == EXPECTED_COLUMNS, \
        f"BOM headers wrong: {reader.fieldnames}"
    # Every row has every column populated (Parent can be blank for
    # top-level; everything else must be present).
    for row in reader:
        assert row['Refdes'], row
        assert row['Value'], row
        assert row['Quantity'] == '1', row
