import pytest
from components.lm393 import LM393


def test_v_plus_greater_is_high(comparator):
    # 100 on V+, 80 on V− → 100 > 80 → True
    assert comparator(100, 80) is True


def test_v_minus_greater_is_low(comparator):
    # 80 on V+, 100 on V− → 80 > 100 → False
    assert comparator(80, 100) is False


def test_equal_inputs_low(comparator):
    # strictly greater-than: equal does not fire
    assert comparator(100, 100) is False


def test_unconnected_input_yields_none(comparator):
    # only v_plus driven → output undefined
    comparator.ports['v_plus'].drive(5.0)
    comparator._evaluate()
    assert comparator.ports['out'].value is None


def test_repr(comparator):
    assert repr(comparator) == "LM393()"
