import pytest

from components.chips.concepts.bldc_motor import BLDCMotor
from framework.port import Direction


# Expected (HA, HB, HC) pattern for each 60° sector boundary —
# the standard 120°-spaced sensor convention used by the matching
# Commutator cell so the two cells agree on sector numbering.
SECTOR_PATTERNS = (
    (0.0,   (True,  False, True )),
    (30.0,  (True,  False, True )),
    (60.0,  (True,  False, False)),
    (90.0,  (True,  False, False)),
    (120.0, (True,  True,  False)),
    (150.0, (True,  True,  False)),
    (180.0, (False, True,  False)),
    (210.0, (False, True,  False)),
    (240.0, (False, True,  True )),
    (270.0, (False, True,  True )),
    (300.0, (False, False, True )),
    (330.0, (False, False, True )),
)


def test_default_angle_is_zero():
    m = BLDCMotor()
    assert m.rotor_angle_deg == 0.0


def test_initial_angle_parameter():
    m = BLDCMotor(initial_angle_deg=180.0)
    assert m.rotor_angle_deg == 180.0


def test_initial_angle_wraps_to_360_range():
    m = BLDCMotor(initial_angle_deg=450.0)
    assert m.rotor_angle_deg == pytest.approx(90.0)


def test_rotor_angle_setter_wraps_to_360_range():
    m = BLDCMotor()
    m.rotor_angle_deg = 540.0
    assert m.rotor_angle_deg == pytest.approx(180.0)


def test_ports_are_all_digital_outputs():
    m = BLDCMotor()
    for name in ('ha', 'hb', 'hc'):
        assert m.ports[name].direction is Direction.OUT


@pytest.mark.parametrize("angle,expected", SECTOR_PATTERNS)
def test_hall_pattern_at_angle(angle, expected):
    m = BLDCMotor()
    assert m(angle) == expected


def test_active_sector_index_matches_60deg_window():
    m = BLDCMotor()
    for angle, sector in ((0.0, 1), (60.0, 2), (120.0, 3),
                           (180.0, 4), (240.0, 5), (300.0, 6)):
        m.rotor_angle_deg = angle
        assert m.active_sector == sector


def test_hall_pattern_property_is_consistent_with_outputs():
    m = BLDCMotor()
    m(45.0)
    pattern = m.hall_pattern
    for name, expected in zip(('ha', 'hb', 'hc'), pattern):
        assert bool(m.ports[name].value) is expected


def test_evaluate_drives_three_hall_pins():
    """Even without calling __call__, evaluate() must drive every
    output port — the surrounding board / system relies on the
    behaviour through the wired ports, not the standalone API."""
    m = BLDCMotor()
    m.rotor_angle_deg = 90.0
    m.evaluate()
    assert m.ports['ha'].value is True
    assert m.ports['hb'].value is False
    assert m.ports['hc'].value is False


def test_full_revolution_visits_every_sector_once():
    m = BLDCMotor()
    visited = set()
    for angle in range(0, 360, 60):
        m(float(angle))
        visited.add(m.active_sector)
    assert visited == {1, 2, 3, 4, 5, 6}


def test_repr_includes_angle_and_sector():
    m = BLDCMotor(initial_angle_deg=120.0)
    r = repr(m)
    assert '120' in r
    assert 'sector=3' in r
