"""Targeted topology test for the Penfold fuzz unit demo.

The teaching point is the *clipping-diode-pair* topology: a high-
gain stage feeds two anti-parallel diodes that clamp the output
to ±0.7 V.  The test asserts:
  - input + output audio jacks exist (the design's external surface)
  - exactly two clipping diodes sit on the op-amp output net
  - both diodes share the same two-node anti-parallel arrangement
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_fuzz_unit'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))

from framework.refdes import RefdesBearing


@pytest.fixture
def fuzz():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from penfold_fuzz_unit import FuzzUnit
        return FuzzUnit()


def _instances(circuit, cls_name: str):
    return [
        fn for fn in circuit.parts
        if isinstance(fn, RefdesBearing) and type(fn).__name__ == cls_name
    ]


def test_input_and_output_jacks_present(fuzz):
    """Two TRS audio jacks — input and output."""
    jacks = _instances(fuzz, 'Audio3p5mmTRSJack')
    assert len(jacks) == 2


def test_exactly_two_clipping_diodes(fuzz):
    """Two D1N4148s form the anti-parallel clipping pair.  More
    or fewer would suggest a different effect topology."""
    diodes = _instances(fuzz, 'D1N4148')
    assert len(diodes) == 2


def test_clipping_diodes_anti_parallel_on_output(fuzz):
    """D1 and D2 wired anti-parallel between OUT and GND: one diode's
    anode is on OUT, its cathode on GND; the other diode is reversed.
    Both share the same two nodes."""
    d1, d2 = fuzz.d1, fuzz.d2
    # D1.anode and D2.cathode meet at the OUT-side node.
    # D1.cathode and D2.anode meet at the GND-side node.
    assert d1.ports['anode'].node is not None
    assert d1.ports['anode'].node is d2.ports['cathode'].node, (
        "D1.anode and D2.cathode must share a node (the OUT side "
        "of the anti-parallel pair) — otherwise the clipping is "
        "asymmetric and the demo isn't a fuzz."
    )
    assert d1.ports['cathode'].node is d2.ports['anode'].node, (
        "D1.cathode and D2.anode must share a node (the GND side "
        "of the anti-parallel pair)."
    )


def test_op_amp_present(fuzz):
    opamps = _instances(fuzz, 'LM741')
    assert len(opamps) == 1
