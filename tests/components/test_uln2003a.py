import pytest
from components.uln2003a import ULN2003A


def test_all_channels_undriven_on_init():
    # power-on with no evaluation: outputs are undriven (None), not "all HIGH"
    uln = ULN2003A()
    assert uln.out == (None,) * 7


def test_channel_high_below_threshold():
    # below threshold → transistor off → pin HIGH
    uln = ULN2003A()
    assert uln(0.5)[0] is True


def test_channel_low_above_threshold():
    # above threshold → transistor conducts → open-collector pulls pin LOW
    uln = ULN2003A()
    assert uln(5.0)[0] is False


def test_channel_high_at_exact_threshold():
    # not strictly greater → transistor off → pin HIGH
    uln = ULN2003A()
    assert uln(ULN2003A.V_THRESHOLD)[0] is True


def test_unspecified_channels_default_high():
    # unspecified channels get 0 V → transistor off → pin HIGH
    uln = ULN2003A()
    result = uln(5.0)
    assert all(s for s in result[1:])


def test_multiple_independent_channels():
    uln = ULN2003A()
    result = uln(5.0, 0.0, 5.0, 0.0, 5.0, 0.0, 5.0)
    assert result == (False, True, False, True, False, True, False)


def test_all_seven_channels_conducting():
    # all inputs above threshold → all outputs LOW
    uln = ULN2003A()
    assert uln(5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0) == (False,) * 7


def test_too_many_inputs_raises():
    uln = ULN2003A()
    with pytest.raises(ValueError):
        uln(5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0)


def test_out_reflects_last_call():
    uln = ULN2003A()
    uln(5.0, 0.0)
    assert uln.out[0] is False   # ch1 conducting → LOW
    assert uln.out[1] is True    # ch2 off → HIGH


def test_repr():
    uln = ULN2003A()
    assert repr(uln) == f'ULN2003A(out={(None,) * 7})'


def test_str_channel_labels():
    uln = ULN2003A()
    uln(5.0)
    s = str(uln)
    assert 'CH1:LOW' in s
    assert 'CH2:HIGH' in s
