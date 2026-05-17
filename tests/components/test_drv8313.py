from components.chips.drv8313 import DRV8313
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'GND',     Direction.IN),
    ( 2, 'VM',      Direction.IN),
    ( 5, 'VCP',     Direction.OUT),
    ( 6, 'GVDD',    Direction.OUT),
    ( 7, 'V3P3OUT', Direction.OUT),
    ( 8, 'nSLEEP',  Direction.IN),
    ( 9, 'nRESET',  Direction.IN),
    (10, 'nFAULT',  Direction.OUT),
    (11, 'EN1',     Direction.IN),
    (12, 'IN1',     Direction.IN),
    (13, 'IN2',     Direction.IN),
    (14, 'EN2',     Direction.IN),
    (15, 'IN3',     Direction.IN),
    (16, 'IN4',     Direction.IN),
    (17, 'EN3',     Direction.IN),
    (18, 'IN5',     Direction.IN),
    (19, 'IN6',     Direction.IN),
    (21, 'OUT1',    Direction.OUT),
    (23, 'OUT2',    Direction.OUT),
    (25, 'OUT3',    Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = DRV8313(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert DRV8313.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(DRV8313(refdes_number=1).pins) == 28


def test_pin_numbers_and_names():
    ic = DRV8313(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = DRV8313(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_three_half_bridges_have_six_gate_inputs():
    """IN1..IN6 are the six gate-command pins (low / high per phase)."""
    ic = DRV8313(refdes_number=1)
    for name in ('IN1', 'IN2', 'IN3', 'IN4', 'IN5', 'IN6'):
        assert name in ic.ports
        assert ic.ports[name].direction is Direction.IN


def test_three_per_phase_enables():
    ic = DRV8313(refdes_number=1)
    for name in ('EN1', 'EN2', 'EN3'):
        assert name in ic.ports
        assert ic.ports[name].direction is Direction.IN


def test_call_is_noop():
    assert DRV8313(refdes_number=1)() is None


def test_repr():
    assert repr(DRV8313(refdes_number=1)) == "DRV8313(refdes='U1')"
