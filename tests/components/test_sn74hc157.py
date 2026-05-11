from components.chips.sn74hc157 import SN74HC157
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'A_B', Direction.IN),
    ( 2, '1A' , Direction.IN),
    ( 3, '1B' , Direction.IN),
    ( 4, '1Y' , Direction.OUT),
    ( 5, '2A' , Direction.IN),
    ( 6, '2B' , Direction.IN),
    ( 7, '2Y' , Direction.OUT),
    ( 8, 'GND', Direction.IN),
    ( 9, '3Y' , Direction.OUT),
    (10, '3B' , Direction.IN),
    (11, '3A' , Direction.IN),
    (12, '4Y' , Direction.OUT),
    (13, '4B' , Direction.IN),
    (14, '4A' , Direction.IN),
    (15, 'G'  , Direction.IN),
    (16, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC157(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC157.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC157.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC157(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC157(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC157(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC157(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC157(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC157(refdes_number=1)) == "SN74HC157(refdes='U1')"
