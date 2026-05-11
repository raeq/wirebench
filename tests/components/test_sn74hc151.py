from components.chips.sn74hc151 import SN74HC151
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'D3' , Direction.IN),
    ( 2, 'D2' , Direction.IN),
    ( 3, 'D1' , Direction.IN),
    ( 4, 'D0' , Direction.IN),
    ( 5, 'Y'  , Direction.OUT),
    ( 6, 'W'  , Direction.OUT),
    ( 7, 'G'  , Direction.IN),
    ( 8, 'GND', Direction.IN),
    ( 9, 'C'  , Direction.IN),
    (10, 'B'  , Direction.IN),
    (11, 'A'  , Direction.IN),
    (12, 'D7' , Direction.IN),
    (13, 'D6' , Direction.IN),
    (14, 'D5' , Direction.IN),
    (15, 'D4' , Direction.IN),
    (16, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC151(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC151.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC151.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC151(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC151(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC151(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC151(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC151(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC151(refdes_number=1)) == "SN74HC151(refdes='U1')"
