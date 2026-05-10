import pytest
from dataclasses import FrozenInstanceError

from framework.pin import PinId


def test_constructs_with_valid_number_and_name():
    pid = PinId(1, 'VBUS')
    assert pid.number == 1
    assert pid.name == 'VBUS'


def test_equality_and_hash_by_value():
    assert PinId(1, 'X') == PinId(1, 'X')
    assert hash(PinId(1, 'X')) == hash(PinId(1, 'X'))
    assert PinId(1, 'X') != PinId(2, 'X')
    assert PinId(1, 'X') != PinId(1, 'Y')


def test_frozen():
    pid = PinId(1, 'X')
    with pytest.raises(FrozenInstanceError):
        pid.number = 2  # type: ignore[misc]


@pytest.mark.parametrize("bad", [0, -1, 1.0, True, '1', None])
def test_number_must_be_positive_int(bad):
    with pytest.raises((ValueError, TypeError)):
        PinId(bad, 'X')  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ['', None, 7])
def test_name_must_be_non_empty_string(bad):
    with pytest.raises((ValueError, TypeError)):
        PinId(1, bad)  # type: ignore[arg-type]


def test_str_format():
    assert str(PinId(7, 'GND')) == 'pin 7 (GND)'


def test_slots_is_set():
    # @dataclass(slots=True) gives the dataclass a real __slots__.
    assert hasattr(PinId, '__slots__')
    assert 'number' in PinId.__slots__
    assert 'name'   in PinId.__slots__
