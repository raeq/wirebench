"""Golden-file regression test for the breadboard SVG visualiser.

Mirrors `tests/framework/export/kicad_sch/test_kicad_sch_golden.py`. Byte-
identical comparison of `export_to_string(<design>, 'breadboard')` against
committed goldens under `tests/golden/breadboard/`. Acceptance criterion
10 of the Phase 2.6 spec (`.plans/phase-2.6-spec.md`).

Refresh:
    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/breadboard/test_breadboard_golden.py

If a test fails because placement / routing / palette output drifts,
investigate the drift first — a deliberate change to the breadboard
layout algorithm or the locked colour palette is the only legitimate
reason to refresh. Silent emission drift is the failure mode this test
exists to catch.
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

import components.chips        # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import components.diodes       # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import framework.export.assembly_guide  # noqa: F401, E402
import framework.export.breadboard      # noqa: F401, E402

from framework.export import export_to_string  # noqa: E402

from hello_led import HelloLED                     # noqa: E402
from water_alarm import WaterAlarm                 # noqa: E402
from dice import Dice                              # noqa: E402
from digital_thermometer import DigitalThermometer # noqa: E402
from doorbell_protector import DoorbellProtector   # noqa: E402


GOLDEN_DIR = Path(__file__).resolve().parents[3] / 'golden' / 'breadboard'


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize("factory,filename", [
    (HelloLED,           'hello_led.breadboard.svg'),
    (WaterAlarm,         'water_alarm.breadboard.svg'),
    (Dice,               'dice.breadboard.svg'),
    (DigitalThermometer, 'digital_thermometer.breadboard.svg'),
    (DoorbellProtector,  'doorbell_protector.breadboard.svg'),
], ids=['HelloLED', 'WaterAlarm', 'Dice', 'DigitalThermometer', 'DoorbellProtector'])
def test_breadboard_output_matches_golden(factory, filename):
    actual = export_to_string(_silently(factory), 'breadboard')
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
        f"breadboard output differs from golden {path.name}.\n"
        f"Refresh deliberately with "
        f"UPDATE_GOLDEN=1 python -m pytest {__file__}\n"
    )
