from components.chips.sn74hc174 import SN74HC174
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'CLR', Direction.IN),
    ( 2, '1Q' , Direction.OUT),
    ( 3, '1D' , Direction.IN),
    ( 4, '2D' , Direction.IN),
    ( 5, '2Q' , Direction.OUT),
    ( 6, '3D' , Direction.IN),
    ( 7, '3Q' , Direction.OUT),
    ( 8, 'GND', Direction.IN),
    ( 9, 'CLK', Direction.IN),
    (10, '4Q' , Direction.OUT),
    (11, '4D' , Direction.IN),
    (12, '5Q' , Direction.OUT),
    (13, '5D' , Direction.IN),
    (14, '6D' , Direction.IN),
    (15, '6Q' , Direction.OUT),
    (16, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC174(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC174.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC174.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC174(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC174(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC174(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC174(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC174(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC174(refdes_number=1)) == "SN74HC174(refdes='U1')"
