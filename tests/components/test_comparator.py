import pytest
from components.comparator import Comparator


def test_v_plus_greater_is_high(comparator):
    assert comparator(100, 80) is True


def test_v_minus_greater_is_low(comparator):
    assert comparator(80, 100) is False


def test_equal_inputs_low(comparator):
    assert comparator(100, 100) is False


def test_unconnected_input_yields_none(comparator):
    comparator.ports['v_plus'].drive(5.0)
    comparator._evaluate()
    assert comparator.ports['out'].value is None


def test_repr(comparator):
    assert repr(comparator) == "Comparator()"
