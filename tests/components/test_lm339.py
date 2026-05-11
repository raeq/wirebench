from components.chips.lm339 import LM339
from framework.port import Direction


EXPECTED_PINS = (
    (1,  'OUT2', Direction.OUT),
    (2,  'OUT1', Direction.OUT),
    (3,  'VCC',  Direction.IN),
    (4,  'IN1-', Direction.IN),
    (5,  'IN1+', Direction.IN),
    (6,  'IN2-', Direction.IN),
    (7,  'IN2+', Direction.IN),
    (8,  'IN3-', Direction.IN),
    (9,  'IN3+', Direction.IN),
    (10, 'IN4-', Direction.IN),
    (11, 'IN4+', Direction.IN),
    (12, 'GND',  Direction.IN),
    (13, 'OUT4', Direction.OUT),
    (14, 'OUT3', Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = LM339(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM339.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM339.FOOTPRINT == 'Package_DIP:DIP-14_W7.62mm'


def test_pin_count():
    ic = LM339(refdes_number=1)
    assert len(ic.pins) == 14


def test_pin_numbers_and_names_match_datasheet():
    ic = LM339(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM339(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM339(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM339(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM339(refdes_number=1)) == "LM339(refdes='U1')"
