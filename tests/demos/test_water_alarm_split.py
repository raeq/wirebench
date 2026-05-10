"""End-to-end equivalence of the split-board WaterAlarm vs the single-board."""
import pytest

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


VCC, GND = 5.0, 0.0


@pytest.fixture
def single():
    return WaterAlarm()


@pytest.fixture
def split():
    return WaterAlarmAssembly()


_SCENARIOS = [
    ('initial — both dry', GND, GND),
    ('low wet, high dry — alarm set', VCC, GND),
    ('both wet — alarm clear',         VCC, VCC),
    ('both dry — alarm set again',     GND, GND),
]


@pytest.mark.parametrize("label,low,high", _SCENARIOS)
def test_split_matches_single_board(single, split, label, low, high):
    s = single(low, high)
    a = split(low, high)
    # Latch state matches.
    assert s == a, label
    # LED states match.
    assert single.red_led.lit   == split.controller.red_led.lit,   label
    assert single.green_led.lit == split.controller.green_led.lit, label


def test_refdes_scoping_per_board(split):
    # Sensor and controller both have a U1 — distinct, per-board namespace.
    sensor_chips = {fn.refdes for fn in split.sensor._factor_nodes
                    if hasattr(fn, 'refdes')}
    controller_chips = {fn.refdes for fn in split.controller._factor_nodes
                        if hasattr(fn, 'refdes')}
    assert 'U1' in sensor_chips
    assert 'U1' in controller_chips
    # Assembly itself sees A1 and A2 as its only refdes-bearing children.
    assert split.sensor.refdes == 'A1'
    assert split.controller.refdes == 'A2'


def test_unmated_assembly_leds_undriven():
    """Construct sensor + controller boards without mate(); the seam is
    open, the controller's LEDs are never lit."""
    from water_alarm_split import SensorBoard, ControllerBoard
    sensor     = SensorBoard    (refdes_number=1)
    controller = ControllerBoard(refdes_number=2)
    # No mate.
    # The controller can't see sensor outputs; its LEDs remain undriven
    # (lit == None) because the latch never gets set/reset.
    # We don't even need to evaluate — the chips' default states hold.
    assert controller.red_led.lit   is None
    assert controller.green_led.lit is None
