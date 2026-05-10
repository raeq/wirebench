import pytest
from components.led import LED


def test_initially_unlit(red_led):
    assert red_led.lit is False


def test_true_signal_lights(red_led):
    red_led(True)
    assert red_led.lit is True


def test_false_signal_extinguishes(red_led):
    red_led(True)
    red_led(False)
    assert red_led.lit is False


def test_none_signal_extinguishes(red_led):
    red_led(True)
    red_led(None)
    assert red_led.lit is False


def test_lit_is_readonly(red_led):
    with pytest.raises(AttributeError):
        red_led.lit = True


def test_str_on(red_led):
    red_led(True)
    assert str(red_led) == "red: ON"


def test_str_off(red_led):
    assert str(red_led) == "red: OFF"


def test_repr(red_led):
    assert repr(red_led) == "LED(color='red', lit=False)"


def test_cathode_port_exists(red_led):
    assert 'cathode' in red_led.ports


def test_cathode_high_prevents_lighting(red_led):
    # anode HIGH but cathode also HIGH → no voltage drop → LED off
    red_led.ports['cathode'].drive(True)
    red_led(True)
    assert red_led.lit is False


def test_physics_constants_present():
    assert hasattr(LED, 'V_F')
    assert hasattr(LED, 'I_F_TYP')
    assert hasattr(LED, 'I_F_MAX')
    assert LED.V_F > 0
    assert LED.I_F_MAX > LED.I_F_TYP
