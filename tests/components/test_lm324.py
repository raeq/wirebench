from components.chips.lm324 import LM324
from framework.port import Direction


EXPECTED_PINS = (
    (1,  'OUT1',  Direction.OUT),
    (2,  'IN1_NEG',  Direction.IN),
    (3,  'IN1_POS',  Direction.IN),
    (4,  'V_POS',    Direction.IN),
    (5,  'IN2_POS',  Direction.IN),
    (6,  'IN2_NEG',  Direction.IN),
    (7,  'OUT2',  Direction.OUT),
    (8,  'OUT3',  Direction.OUT),
    (9,  'IN3_NEG',  Direction.IN),
    (10, 'IN3_POS',  Direction.IN),
    (11, 'V_GND', Direction.IN),
    (12, 'IN4_POS',  Direction.IN),
    (13, 'IN4_NEG',  Direction.IN),
    (14, 'OUT4',  Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = LM324(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM324.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM324.FOOTPRINT == 'Package_DIP:DIP-14_W7.62mm'


def test_pin_count():
    ic = LM324(refdes_number=1)
    assert len(ic.pins) == 14


def test_pin_numbers_and_names_match_datasheet():
    ic = LM324(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM324(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = LM324(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM324(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM324(refdes_number=1)) == "LM324(refdes='U1')"
