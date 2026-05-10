import pytest
from components.chips.lm393 import LM393


@pytest.fixture
def chip():
    return LM393()


def test_channel_1_v_plus_greater_is_high(chip):
    out_1, _ = chip(100, 80, 0, 0)
    assert out_1 is True


def test_channel_1_v_minus_greater_is_low(chip):
    out_1, _ = chip(80, 100, 0, 0)
    assert out_1 is False


def test_channel_2_independent_of_channel_1(chip):
    out_1, out_2 = chip(100, 80, 50, 60)
    assert out_1 is True
    assert out_2 is False


def test_undriven_channel_2_returns_none(chip):
    chip.ports['v_plus_1'].drive(100.0)
    chip.ports['v_minus_1'].drive(80.0)
    chip.evaluate()
    assert chip.ports['out_1'].value is True
    assert chip.ports['out_2'].value is None


def test_repr(chip):
    assert repr(chip) == "LM393()"
