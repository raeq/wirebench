import pytest

from components.chips.concepts.fan_controller import FanController
from framework.port import Direction


def test_default_trip_points_match_tida_00517():
    c = FanController()
    assert c.trip_high_c == 60.0
    assert c.trip_low_c  == 50.0


def test_starts_with_fan_off():
    c = FanController()
    assert c.fan_on is False


def test_below_trip_low_keeps_fan_off():
    c = FanController()
    assert c(temperature_c=25.0) is False


def test_at_trip_high_turns_fan_on():
    c = FanController()
    assert c(temperature_c=60.0) is True


def test_above_trip_high_keeps_fan_on():
    c = FanController()
    c(temperature_c=60.0)
    assert c(temperature_c=80.0) is True


def test_deadband_holds_previous_state_when_off():
    """Between trip_low and trip_high, with the fan currently off,
    the controller must not turn it on."""
    c = FanController()
    c(temperature_c=25.0)            # ensure off
    assert c(temperature_c=55.0) is False


def test_deadband_holds_previous_state_when_on():
    """Same deadband, but with the fan currently on — it must stay on."""
    c = FanController()
    c(temperature_c=65.0)            # turn on
    assert c(temperature_c=55.0) is True


def test_at_trip_low_turns_fan_off():
    c = FanController()
    c(temperature_c=65.0)            # turn on
    assert c(temperature_c=50.0) is False


def test_falling_through_deadband_after_trip_low():
    c = FanController()
    c(temperature_c=65.0)
    c(temperature_c=49.0)            # below trip_low
    assert c(temperature_c=55.0) is False     # back into deadband, fan stays off


def test_custom_trip_points():
    c = FanController(trip_high_c=80.0, trip_low_c=70.0)
    assert c(temperature_c=75.0) is False     # deadband, never crossed up
    assert c(temperature_c=80.0) is True
    assert c(temperature_c=75.0) is True      # held in deadband
    assert c(temperature_c=70.0) is False


def test_rejects_inverted_trip_points():
    with pytest.raises(ValueError):
        FanController(trip_high_c=50.0, trip_low_c=60.0)
    with pytest.raises(ValueError):
        FanController(trip_high_c=60.0, trip_low_c=60.0)


def test_ports_have_correct_directions():
    c = FanController()
    assert c.ports['temperature_in'].direction is Direction.IN
    assert c.ports['fan_drive'     ].direction is Direction.OUT


def test_wired_temperature_overrides_python_attribute():
    """When something drives the temperature_in port, evaluate must
    use that value in preference to the Python `_temperature_c`."""
    c = FanController()
    c._temperature_c = 80.0
    c.ports['temperature_in'].drive(20.0)
    c.evaluate()
    assert c.fan_on is False


def test_repr_includes_temperature_and_state():
    c = FanController()
    c(temperature_c=65.0)
    r = repr(c)
    assert "fan_on=True"     in r
    assert "trip_high_c=60.0" in r
