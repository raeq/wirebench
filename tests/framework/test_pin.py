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


# --- ports surface ---

def test_pin_ports_dict_keyed_by_port_name():
    # Convention: every FactorNode's ports dict keys match the port name.
    # For Pin, that means {'a': external, 'a_inner': internal} for an IN
    # pin called 'a' — not {'external': ..., 'internal': ...}.
    p = Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    assert set(p.ports.keys()) == {'a', 'a_inner'}
    assert p.ports['a']       is p.external
    assert p.ports['a_inner'] is p.internal
    # Each entry's port.name matches its dict key.
    for name, port in p.ports.items():
        assert port.name == name


def test_pin_carries_signal_type_to_both_faces():
    p = Pin('v', Direction.IN, ELECTRICAL, signal_type=Analog)
    assert p.external.signal_type is Analog
    assert p.internal.signal_type is Analog
