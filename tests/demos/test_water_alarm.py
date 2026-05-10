import pytest

VCC = 5.0   # probe voltage when submerged (water conducts to reference)
GND = 0.0   # probe voltage when dry


def test_initial_state_unknown(alarm):
    assert alarm(VCC, GND) is None          # deadband on first call


def test_low_probe_dry_sets_alarm(alarm):
    assert alarm(GND, GND) is True


def test_deadband_holds_after_alarm_set(alarm):
    alarm(GND, GND)
    assert alarm(VCC, GND) is True


def test_high_probe_submerged_resets_alarm(alarm):
    alarm(GND, GND)
    assert alarm(VCC, VCC) is False


def test_deadband_holds_after_reset(alarm):
    alarm(GND, GND)
    alarm(VCC, VCC)
    assert alarm(VCC, GND) is False


def test_red_led_on_when_alarm_set(alarm):
    alarm(GND, GND)
    assert alarm.red_led.lit is True
    assert alarm.green_led.lit is False


def test_green_led_on_when_alarm_reset(alarm):
    alarm(GND, GND)
    alarm(VCC, VCC)
    assert alarm.red_led.lit is False
    assert alarm.green_led.lit is True


def test_str(alarm):
    alarm(GND, GND)
    assert str(alarm) == "red: ON | green: OFF"
