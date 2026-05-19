"""Targeted topology test for the Penfold light-activated-switch demo.

The teaching point is the *sensor → threshold → switched output* chain:
exactly one Photoresistor, one op-amp comparator, one NPN switching
transistor, and an indicator output stage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_light_switch'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))

from framework.refdes import RefdesBearing


@pytest.fixture
def switch():
    from penfold_light_switch import LightActivatedSwitch
    return LightActivatedSwitch()


def _instances(circuit, cls_name: str):
    return [
        fn for fn in circuit.parts
        if isinstance(fn, RefdesBearing) and type(fn).__name__ == cls_name
    ]


def test_exactly_one_photoresistor(switch):
    """The LDR is the design's distinguishing part — exactly one
    instance.  More than one would suggest a different topology
    (differential light sensor, etc.)."""
    assert len(_instances(switch, 'Photoresistor')) == 1


def test_comparator_present(switch):
    """The LM741 op-amp is the comparator."""
    opamps = _instances(switch, 'LM741')
    assert len(opamps) == 1


def test_switching_transistor_present(switch):
    """A single NPN BC547 sits between the comparator output and the
    LED, the saturated-switch idiom."""
    bjts = _instances(switch, 'BC547')
    assert len(bjts) == 1


def test_indicator_led_present(switch):
    """One LED indicates the switch state."""
    leds = _instances(switch, 'LED')
    assert len(leds) == 1


def test_no_chip_other_than_lm741(switch):
    """No CMOS / logic chips — the design is the pure-analog version
    of the sensor → threshold → output pattern.  This is what makes
    the demo a teaching exemplar distinct from the water-alarm
    (which routes through digital logic immediately)."""
    from framework.chip import Chip
    chips = [
        fn for fn in switch.parts
        if isinstance(fn, RefdesBearing) and isinstance(fn, Chip)
    ]
    assert len(chips) == 1
    assert type(chips[0]).__name__ == 'LM741'


def test_lit_port_present(switch):
    """The composite exposes a `lit` external port — a downstream
    consumer can read the indicator state without poking at the
    LED's anode directly."""
    assert 'lit' in switch.ports
