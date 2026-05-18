"""Golden-file regression test for the kicad_sch (`.kicad_sch`) adapter.

Mirrors `tests/framework/export/kicad/test_kicad_golden.py`. Byte-identical
comparison of `export_to_string(<design>, 'kicad_sch')` against committed
goldens under `tests/golden/kicad_sch/`. Acceptance criterion #7 of the
Phase 2.5 spec.

Refresh:
    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/kicad_sch/test_kicad_sch_golden.py

If a test fails because the placement / routing / symbol-map output drifts,
investigate the drift first — a deliberate change to the layout algorithm or
the embedded symbol library is the only legitimate reason to refresh the
golden. Silent emission drift is the failure mode this test exists to catch.
"""
from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

import components.chips      # noqa: F401, E402
import components.passives   # noqa: F401, E402
import components.connectors # noqa: F401, E402
import components.diodes     # noqa: F401, E402
import framework.export.kicad_sch  # noqa: F401, E402

from framework.export import export_to_string  # noqa: E402

from water_alarm import WaterAlarm  # noqa: E402
from water_alarm_split import WaterAlarmAssembly  # noqa: E402


GOLDEN_DIR = Path(__file__).resolve().parents[3] / 'golden' / 'kicad_sch'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (WaterAlarm,         'water_alarm.kicad_sch'),
    (WaterAlarmAssembly, 'water_alarm_assembly.kicad_sch'),
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_kicad_sch_output_matches_golden(factory, filename):
    actual = export_to_string(_silently(factory), 'kicad_sch')
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
        f"kicad_sch output differs from golden {path.name}.\n"
        f"Refresh deliberately with "
        f"UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
