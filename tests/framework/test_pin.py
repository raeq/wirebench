import pytest
from framework.ground import ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital, Analog


# --- direction inversion: external direction sets internal's role ---

def test_in_pin_external_is_in_internal_is_out():
    p = Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.IN
    assert p.internal.direction is Direction.OUT


def test_out_pin_external_is_out_internal_is_in():
    p = Pin('y', Direction.OUT, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.OUT
    assert p.internal.direction is Direction.IN


def test_bidir_pin_not_supported():
    with pytest.raises(NotImplementedError, match="BIDIR"):
        Pin('t', Direction.BIDIR, ELECTRICAL, signal_type=Digital)


# --- evaluate copies signal across the boundary ---

def test_in_pin_evaluate_copies_external_to_internal():
    p = Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.evaluate()
    assert p.internal.value is True


def test_out_pin_evaluate_copies_internal_to_external():
    p = Pin('y', Direction.OUT, ELECTRICAL, signal_type=Digital)
    p.internal.drive(False)
    p.evaluate()
    assert p.external.value is False


def test_in_pin_undriven_external_propagates_none():
    p = Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    p.evaluate()
    assert p.internal.value is None


# --- default models a weak pull-up / pull-down on an IN pin ---

def test_in_pin_default_applies_when_external_undriven():
    p = Pin('oe', Direction.IN, ELECTRICAL, signal_type=Digital, default=True)
    p.evaluate()
    assert p.internal.value is True


def test_in_pin_default_overridden_by_driven_external():
    p = Pin('oe', Direction.IN, ELECTRICAL, signal_type=Digital, default=True)
    p.external.drive(False)
    p.evaluate()
    assert p.internal.value is False


def test_out_pin_default_is_irrelevant():
    # default doesn't apply to OUT pins (they propagate internal -> external).
    p = Pin('y', Direction.OUT, ELECTRICAL, signal_type=Digital, default=True)
    p.evaluate()
    assert p.external.value is None


# --- ports surface ---

def test_pin_ports_dict_exposes_both_faces():
    p = Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    assert set(p.ports.keys()) == {'external', 'internal'}
    assert p.ports['external'] is p.external
    assert p.ports['internal'] is p.internal


def test_pin_carries_signal_type_to_both_faces():
    p = Pin('v', Direction.IN, ELECTRICAL, signal_type=Analog)
    assert p.external.signal_type is Analog
    assert p.internal.signal_type is Analog
