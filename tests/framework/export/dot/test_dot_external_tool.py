"""Optional external-tool round-trip: parse the DOT output with the
real `dot` binary. Skips cleanly when Graphviz isn't installed.

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
import framework.export.dot  # noqa: F401

from framework.export import export

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.skipif(not shutil.which('dot'), reason='Graphviz `dot` not installed')
@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'wa.dot'),
    (WaterAlarmAssembly, 'asm.dot'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_dot_parses_under_graphviz(factory, filename, tmp_path):
    design = _silently(factory)
    out = tmp_path / filename
    export(design, 'dot', out)
    result = subprocess.run(
        ['dot', '-Tsvg', '-o', '/dev/null', str(out)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, (
        f"`dot` rejected the deck:\n{result.stderr}"
    )
