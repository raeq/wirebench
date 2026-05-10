import pytest
from components.lm393 import LM393


def test_ref_on_plus_sensor_below_fires(comp_low):
    # vref=100 on V+, sensor on V−: 100 > 80 → True
    assert comp_low(80) is True


def test_ref_on_plus_sensor_above_silent(comp_low):
    # vref=100 on V+, sensor on V−: 100 > 120 → False
    assert comp_low(120) is False


def test_ref_on_plus_sensor_equal_silent(comp_low):
    # strictly greater-than: equal does not fire
    assert comp_low(100) is False


def test_ref_on_minus_sensor_above_fires(comp_high):
    # vref=150 on V−, sensor on V+: 160 > 150 → True
    assert comp_high(160) is True


def test_ref_on_minus_sensor_below_silent(comp_high):
    # vref=150 on V−, sensor on V+: 120 > 150 → False
    assert comp_high(120) is False


def test_ref_on_minus_sensor_equal_silent(comp_high):
    assert comp_high(150) is False


def test_repr(comp_low):
    assert repr(comp_low) == "LM393(vref=100, ref_on_plus=True)"
