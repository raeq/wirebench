import pytest
from components.chips.sn74hc04 import SN74HC04


def test_invert_high():
    ic = SN74HC04()
    assert ic(True)[0] is False


def test_invert_low():
    ic = SN74HC04()
    assert ic(False)[0] is True


def test_none_propagates():
    ic = SN74HC04()
    assert ic(None)[0] is None


def test_unspecified_channels_default_low_in_high_out():
    ic = SN74HC04()
    result = ic(True)          # only ch1 specified
    assert all(v is True for v in result[1:])


def test_all_six_channels():
    ic = SN74HC04()
    result = ic(True, False, True, False, True, False)
    assert result == (False, True, False, True, False, True)


def test_too_many_inputs_raises():
    ic = SN74HC04()
    with pytest.raises(ValueError):
        ic(True, True, True, True, True, True, True)


def test_ports_named_a1_to_a6_and_y1_to_y6():
    ic = SN74HC04()
    for i in range(1, 7):
        assert f'a_{i}' in ic.ports
        assert f'y_{i}' in ic.ports


def test_repr():
    assert repr(SN74HC04()) == 'SN74HC04()'
