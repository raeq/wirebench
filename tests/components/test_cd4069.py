import pytest
from components.cd4069 import CD4069


def test_invert_high():
    ic = CD4069()
    assert ic(True)[0] is False


def test_invert_low():
    ic = CD4069()
    assert ic(False)[0] is True


def test_none_propagates():
    ic = CD4069()
    assert ic(None)[0] is None


def test_unspecified_channels_default_low_in_high_out():
    ic = CD4069()
    result = ic(True)
    assert all(v is True for v in result[1:])


def test_all_six_channels():
    ic = CD4069()
    result = ic(True, False, True, False, True, False)
    assert result == (False, True, False, True, False, True)


def test_too_many_inputs_raises():
    ic = CD4069()
    with pytest.raises(ValueError):
        ic(True, True, True, True, True, True, True)


def test_ports_named_a1_to_a6_and_y1_to_y6():
    ic = CD4069()
    for i in range(1, 7):
        assert f'a_{i}' in ic.ports
        assert f'y_{i}' in ic.ports


def test_repr():
    assert repr(CD4069()) == 'CD4069()'
