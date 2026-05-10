import pytest
from components.parts.concepts.resistor import Resistor


def test_ohms_law(shunt):
    # 100 A through 1 Ω → 100 V
    assert shunt(100) == 100


def test_scaling():
    # 50 mA through 10 Ω → 500 mV (V = I × R, consistent units)
    r = Resistor(ohms=10)
    assert r(50) == 500


def test_zero_current(shunt):
    assert shunt(0) == 0


def test_repeated_calls_recompute():
    # second call must overwrite the result of the first, not no-op
    r = Resistor(ohms=10)
    assert r(5) == 50
    assert r(7) == 70


def test_port_names():
    r = Resistor(ohms=470)
    assert 't1' in r.ports
    assert 't2' in r.ports


def test_repr():
    r = Resistor(ohms=47)
    assert repr(r) == "Resistor(ohms=47.0)"


def test_repr_round_trip_for_unit_inputs():
    from framework.units import Ohms, Kilohms
    assert repr(Resistor(Ohms(47)))     == "Resistor(ohms=47.0)"
    assert repr(Resistor(Kilohms(4.7))) == "Resistor(ohms=4700.0)"


def test_str():
    r = Resistor(ohms=47)
    assert str(r) == "47.0 Ω"
