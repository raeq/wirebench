"""Targeted topology test for the Penfold warbling-doorbuzzer demo.

The teaching point is *oscillator composition*: two astables, with
one modulating the other.  The test asserts exactly two 555s exist
and that the modulator (U1) output is wired to the carrier (U2)
reset pin.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_warbling_doorbuzzer'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))

from framework.refdes import RefdesBearing


@pytest.fixture
def buzzer():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from penfold_warbling_doorbuzzer import WarblingDoorbuzzer
        return WarblingDoorbuzzer()


def _instances(circuit, cls_name: str):
    return [
        fn for fn in circuit.parts
        if isinstance(fn, RefdesBearing) and type(fn).__name__ == cls_name
    ]


def test_exactly_two_ne555_oscillators(buzzer):
    """The composition pattern is two astables: a slow modulator and
    a fast carrier.  The catalogue's NE556 (dual 555 in one package)
    is an alternative single-chip implementation if added later, but
    the two-555 form is the canonical Penfold layout."""
    timers = _instances(buzzer, 'NE555')
    assert len(timers) == 2


def test_modulator_drives_carrier_reset(buzzer):
    """The slow oscillator (U1) output net is shared with the fast
    oscillator (U2) RESET input — the *modulation* topology."""
    u1_out = buzzer.u1.ports['OUT']
    u2_reset = buzzer.u2.ports['RESET']
    # Same node = wired together at the same logical net.
    assert u1_out.node is not None
    assert u1_out.node is u2_reset.node, (
        "U1.OUT and U2.RESET must share a node — that's the "
        "modulator → carrier composition.  If they don't, the warble "
        "topology isn't actually present."
    )


def test_exactly_one_speaker(buzzer):
    speakers = _instances(buzzer, 'Speaker')
    assert len(speakers) == 1
