import pytest
from framework.errors import PortContentionError, UnknownPortError
from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.signals import Digital, Analog


# --- direction inversion: external direction sets internal's role ---

def test_in_pin_external_is_in_internal_is_out():
    p = Pin(PinId(1, 'a'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.IN
    assert p.internal.direction is Direction.OUT


def test_out_pin_external_is_out_internal_is_in():
    p = Pin(PinId(1, 'y'), Direction.OUT, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.OUT
    assert p.internal.direction is Direction.IN


def test_bidir_pin_supported():
    # BIDIR pins are now supported — connector contacts need them.
    p = Pin(PinId(1, 't'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.BIDIR
    assert p.internal.direction is Direction.BIDIR


def test_bidir_pin_relays_external_to_internal():
    p = Pin(PinId(1, 't'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.evaluate()
    assert p.internal.value is True


def test_bidir_pin_relays_internal_to_external():
    p = Pin(PinId(1, 't'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.internal.drive(False)
    p.evaluate()
    assert p.external.value is False


def test_bidir_pin_contention_raises():
    p = Pin(PinId(1, 't'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.internal.drive(False)
    with pytest.raises(PortContentionError, match="contention"):
        p.evaluate()


def test_pin_is_conductor():
    assert Pin.IS_CONDUCTOR is True


def test_pin_other_face_returns_opposite():
    p = Pin(PinId(1, 'x'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.other_face(p.external) is p.internal
    assert p.other_face(p.internal) is p.external


def test_pin_other_face_rejects_stranger_port():
    from framework.port import Port
    p = Pin(PinId(1, 'x'), Direction.IN, ELECTRICAL, signal_type=Digital)
    stranger = Port('stranger', Direction.IN, ELECTRICAL, signal_type=Digital)
    with pytest.raises(UnknownPortError):
        p.other_face(stranger)


def test_pin_rejects_bare_string():
    # First arg used to be a bare string; it must now be a PinId.
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)  # type: ignore[arg-type]


# --- evaluate copies signal across the boundary ---

def test_in_pin_evaluate_copies_external_to_internal():
    p = Pin(PinId(1, 'a'), Direction.IN, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.evaluate()
    assert p.internal.value is True


def test_out_pin_evaluate_copies_internal_to_external():
    p = Pin(PinId(1, 'y'), Direction.OUT, ELECTRICAL, signal_type=Digital)
    p.internal.drive(False)
    p.evaluate()
    assert p.external.value is False


def test_in_pin_undriven_external_propagates_none():
    p = Pin(PinId(1, 'a'), Direction.IN, ELECTRICAL, signal_type=Digital)
    p.evaluate()
    assert p.internal.value is None


# --- ports surface ---

def test_pin_ports_dict_keyed_by_port_name():
    # Convention: every FactorNode's ports dict keys match the port name.
    # For Pin, that means {'a': external, 'a_inner': internal} for an IN
    # pin called 'a' — not {'external': ..., 'internal': ...}.
    p = Pin(PinId(1, 'a'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert set(p.ports.keys()) == {'a', 'a_inner'}
    assert p.ports['a']       is p.external
    assert p.ports['a_inner'] is p.internal
    # Each entry's port.name matches its dict key.
    for name, port in p.ports.items():
        assert port.name == name


def test_pin_carries_signal_type_to_both_faces():
    p = Pin(PinId(1, 'v'), Direction.IN, ELECTRICAL, signal_type=Analog)
    assert p.external.signal_type is Analog
    assert p.internal.signal_type is Analog


# --- PinId metadata exposed on Pin ---

def test_pin_exposes_id_number_name():
    p = Pin(PinId(7, 'GND'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.id == PinId(7, 'GND')
    assert p.number == 7
    assert p.name == 'GND'


def test_pin_repr_includes_pin_id():
    p = Pin(PinId(7, 'GND'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert 'pin 7 (GND)' in repr(p)


def test_pin_external_port_carries_pin_name():
    # The underlying Port keeps the name that wiring code uses today.
    p = Pin(PinId(7, 'GND'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.external.name == 'GND'
    assert p.internal.name == 'GND_inner'
