"""Optional external-tool round-trip via `mmdc`. Skips when absent.

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
import framework.export.mermaid  # noqa: F401

from framework.export import export

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.skipif(not shutil.which('mmdc'), reason='mermaid-cli `mmdc` not installed')
@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'wa.mmd'),
    (WaterAlarmAssembly, 'asm.mmd'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_mermaid_parses_under_mmdc(factory, filename, tmp_path):
    design = _silently(factory)
    out = tmp_path / filename
    export(design, 'mermaid', out)
    svg = tmp_path / 'out.svg'
    result = subprocess.run(
        ['mmdc', '-i', str(out), '-o', str(svg)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, (
        f"`mmdc` rejected the diagram:\n{result.stderr}"
    )
