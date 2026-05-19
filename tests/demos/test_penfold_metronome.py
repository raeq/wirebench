"""Targeted topology test for the Penfold metronome demo.

The teaching point: exactly one astable oscillator (NE555) + exactly
one speaker, joined by an AC-coupling capacitor.  Pairs with the
P8 one-second-timer (op-amp relaxation oscillator) to demonstrate
both classical astable topologies.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_metronome'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))

from framework.refdes import RefdesBearing


@pytest.fixture
def metro():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from penfold_metronome import Metronome
        return Metronome()


def _instances(circuit, cls_name: str):
    return [
        fn for fn in circuit.parts
        if isinstance(fn, RefdesBearing) and type(fn).__name__ == cls_name
    ]


def test_exactly_one_astable(metro):
    """One NE555 is the astable oscillator."""
    timers = _instances(metro, 'NE555')
    assert len(timers) == 1


def test_exactly_one_speaker(metro):
    """One small speaker — the metronome's audible output."""
    speakers = _instances(metro, 'Speaker')
    assert len(speakers) == 1
    assert float(speakers[0].impedance_ohms) == pytest.approx(8.0)


def test_ac_coupling_capacitor_present(metro):
    """At least one electrolytic-grade coupling cap (>= 1 µF) sits
    on the output path — the canonical 555-to-speaker AC coupler."""
    caps = _instances(metro, 'Capacitor')
    coupling_caps = [c for c in caps if float(c.farads) >= 1e-6]
    assert len(coupling_caps) >= 1, (
        "expected at least one ≥ 1 µF capacitor as the AC coupler "
        "between the 555 OUT and the speaker — protecting the voice "
        "coil from the 555's DC offset"
    )
