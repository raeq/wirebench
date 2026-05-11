"""Optional external-tool round-trip via `netlistsvg`. Skips when
absent.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import shutil
import subprocess
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.yosys  # noqa: F401

from framework.export import export

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.skipif(not shutil.which('netlistsvg'), reason='netlistsvg not installed')
@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'wa.json'),
    (WaterAlarmAssembly, 'asm.json'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_yosys_parses_under_netlistsvg(factory, filename, tmp_path):
    design = _silently(factory)
    out = tmp_path / filename
    export(design, 'yosys', out)
    svg = tmp_path / 'out.svg'
    result = subprocess.run(
        ['netlistsvg', str(out), '-o', str(svg)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, (
        f"netlistsvg rejected the JSON:\n{result.stderr}"
    )
