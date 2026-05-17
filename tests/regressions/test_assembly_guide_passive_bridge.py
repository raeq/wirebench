"""Regression: assembly-guide jumpers must not short the body of a passive.

Demo authors sometimes wire both terminals of a 2-lead passive
(Resistor, Capacitor, Diode, LED) into the same `wire()` call so the
framework's voltage-only solver can propagate the signal through the
part as a 0-Ω passthrough.  Example from the digital-thermometer
demo:

    wire(self.arduino.PD3,
         self.r1.t1, self.r1.t2,        # 0-Ω passthrough
         self.display.DIG_1)

At simulation time the four ports share one node; at the bench R1's
body is the connection from t1 to t2, so the correct assembly is:

    Run a jumper from R1 t1 ... to U1 D3 (Arduino Uno header).
    Run a jumper from R1 t2 ... to U3 pin 12 ...

Before the fix the exporter chained all four endpoints and emitted a
third jumper directly from R1 t1 ↔ R1 t2 (and, in the doorbell
demo, the same for C4 t1 ↔ C4 t2 and R1 t1 ↔ R1 t2).  Those wires
short the part's body — they can't happen physically.

This test asserts no jumper step has both endpoints on the same
refdes, across every breadboard-compatible demo.
"""
from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

import pytest

_DEMOS = Path(__file__).resolve().parents[2] / 'demos'
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))

import components.chips        # noqa: F401, E402 — registry side effects
import components.diodes       # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import framework.export.assembly_guide  # noqa: F401, E402

from framework.export import export_to_string  # noqa: E402

from hello_led import HelloLED                           # noqa: E402
from water_alarm import WaterAlarm                       # noqa: E402
from dice import Dice                                    # noqa: E402
from digital_thermometer import DigitalThermometer       # noqa: E402
from doorbell_protector import DoorbellProtector         # noqa: E402


# A jumper instruction always reads "Run a jumper from <SRC> ... to <DST>."
# where each endpoint starts with a refdes (e.g. R1, U2, D7, K1) followed
# by a port name.  Split on the first " at " / " to " / " — " so the
# trailing breadboard-position blurb doesn't get mixed into the SRC.
_JUMPER_RE = re.compile(
    r"Run a jumper from "
    r"(?P<src>[A-Z]+\d+\s+\S+)"
    r"(?:\s+at\s+position\s+\d+[^t]*?)?\s+to\s+"
    r"(?P<dst>[A-Z]+\d+\s+\S+|the\s+top)"
)


def _flatten(text: str) -> str:
    """Strip Markdown paragraph wrapping inside the Method section so
    each `Run a jumper …` step fits on one line."""
    method = text.split('## Method', 1)[1].split('## Notes', 1)[0]
    return ' '.join(method.split())


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _refdes(endpoint: str) -> str:
    """First whitespace-delimited token of an endpoint string is the
    refdes (e.g. `R1 t1` → `R1`, `U2 pin 3` → `U2`)."""
    return endpoint.split(maxsplit=1)[0]


@pytest.mark.parametrize("factory,name", [
    (HelloLED,           'HelloLED'),
    (WaterAlarm,         'WaterAlarm'),
    (Dice,               'Dice'),
    (DigitalThermometer, 'DigitalThermometer'),
    (DoorbellProtector,  'DoorbellProtector'),
])
def test_no_jumper_shorts_a_part_body(factory, name):
    """No emitted jumper has both endpoints on the same refdes.

    A jumper from `R1 t1` to `R1 t2` would short the resistor's
    body — impossible at the bench because the resistor IS the
    connection between its two leads."""
    design = _silently(factory)
    text = export_to_string(design, 'assembly_guide')
    flat = _flatten(text)
    offenders: list[str] = []
    for match in _JUMPER_RE.finditer(flat):
        src, dst = match.group('src'), match.group('dst')
        if dst == 'the top':
            continue   # rail jumper, only one endpoint with a refdes
        if _refdes(src) == _refdes(dst):
            offenders.append(match.group(0))
    assert not offenders, (
        f"{name} emits jumper(s) wiring across the body of a passive "
        f"(both endpoints on the same refdes):\n  "
        + "\n  ".join(offenders)
    )
