from components.chips.sn74hc541 import SN74HC541
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'OE1', Direction.IN),
    ( 2, 'A1' , Direction.IN),
    ( 3, 'A2' , Direction.IN),
    ( 4, 'A3' , Direction.IN),
    ( 5, 'A4' , Direction.IN),
    ( 6, 'A5' , Direction.IN),
    ( 7, 'A6' , Direction.IN),
    ( 8, 'A7' , Direction.IN),
    ( 9, 'A8' , Direction.IN),
    (10, 'GND', Direction.IN),
    (11, 'Y8' , Direction.OUT),
    (12, 'Y7' , Direction.OUT),
    (13, 'Y6' , Direction.OUT),
    (14, 'Y5' , Direction.OUT),
    (15, 'Y4' , Direction.OUT),
    (16, 'Y3' , Direction.OUT),
    (17, 'Y2' , Direction.OUT),
    (18, 'Y1' , Direction.OUT),
    (19, 'OE2', Direction.IN),
    (20, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC541(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC541.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC541.FOOTPRINT == 'Package_DIP:DIP-20_W7.62mm'


def test_pin_count():
    ic = SN74HC541(refdes_number=1)
    assert len(ic.pins) == 20


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC541(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC541(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC541(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC541(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC541(refdes_number=1)) == "SN74HC541(refdes='U1')"
