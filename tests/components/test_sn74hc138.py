from components.chips.sn74hc138 import SN74HC138
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'A'  , Direction.IN),
    ( 2, 'B'  , Direction.IN),
    ( 3, 'C'  , Direction.IN),
    ( 4, 'G2A', Direction.IN),
    ( 5, 'G2B', Direction.IN),
    ( 6, 'G1' , Direction.IN),
    ( 7, 'Y7' , Direction.OUT),
    ( 8, 'GND', Direction.IN),
    ( 9, 'Y6' , Direction.OUT),
    (10, 'Y5' , Direction.OUT),
    (11, 'Y4' , Direction.OUT),
    (12, 'Y3' , Direction.OUT),
    (13, 'Y2' , Direction.OUT),
    (14, 'Y1' , Direction.OUT),
    (15, 'Y0' , Direction.OUT),
    (16, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC138(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC138.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC138.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC138(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC138(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC138(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC138(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC138(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC138(refdes_number=1)) == "SN74HC138(refdes='U1')"
