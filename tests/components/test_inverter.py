import pytest
from components.chips.concepts.inverter import Inverter


def test_inverts_high():
    assert Inverter()(True) is False


def test_inverts_low():
    assert Inverter()(False) is True


def test_none_propagates():
    assert Inverter()(None) is None


def test_repr_undriven():
    assert repr(Inverter()) == "Inverter(y=None)"
