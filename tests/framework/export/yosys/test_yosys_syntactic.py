"""Syntactic validation: the output parses as JSON with the expected
top-level structure. Uses json.loads (stdlib).

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import json
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.yosys  # noqa: F401

from framework.export import export_to_string

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory", [WaterAlarm, WaterAlarmAssembly],
                         ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_yosys_parses_as_json_with_required_shape(factory):
    doc = json.loads(export_to_string(_silently(factory), 'yosys'))
    assert isinstance(doc, dict)
    assert 'creator' in doc
    assert 'modules' in doc
    assert isinstance(doc['modules'], dict)
    for module_name, module in doc['modules'].items():
        for required in ('ports', 'cells', 'netnames'):
            assert required in module, \
                f"module {module_name} missing {required}"
        for cell_name, cell in module['cells'].items():
            for required in ('type', 'hide_name', 'parameters',
                             'port_directions', 'connections'):
                assert required in cell, \
                    f"cell {cell_name} missing {required}"
