from components.chips.max232 import MAX232
from framework.port import Direction


EXPECTED_PINS = (
    (1,  'C1_POS',   Direction.IN),
    (2,  'V_POS',    Direction.OUT),
    (3,  'C1_NEG',   Direction.IN),
    (4,  'C2_POS',   Direction.IN),
    (5,  'C2_NEG',   Direction.IN),
    (6,  'V_NEG',    Direction.OUT),
    (7,  'T2OUT', Direction.OUT),
    (8,  'R2IN',  Direction.IN),
    (9,  'R2OUT', Direction.OUT),
    (10, 'T2IN',  Direction.IN),
    (11, 'T1IN',  Direction.IN),
    (12, 'R1OUT', Direction.OUT),
    (13, 'R1IN',  Direction.IN),
    (14, 'T1OUT', Direction.OUT),
    (15, 'GND',   Direction.IN),
    (16, 'VCC',   Direction.IN),
)


def test_construction_with_refdes_1():
    ic = MAX232(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert MAX232.REFDES_PREFIX == 'U'


def test_footprint():
    assert MAX232.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = MAX232(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = MAX232(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = MAX232(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = MAX232(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = MAX232(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(MAX232(refdes_number=1)) == "MAX232(refdes='U1')"
