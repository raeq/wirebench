from components.chips.attiny84 import ATtiny84
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'VCC',          Direction.IN),
    (  2, 'PB0',          Direction.BIDIR),
    (  3, 'PB1',          Direction.BIDIR),
    (  4, 'PB3',          Direction.BIDIR),
    (  5, 'PB2',          Direction.BIDIR),
    (  6, 'PA7',          Direction.BIDIR),
    (  7, 'PA6',          Direction.BIDIR),
    (  8, 'PA5',          Direction.BIDIR),
    (  9, 'PA4',          Direction.BIDIR),
    ( 10, 'PA3',          Direction.BIDIR),
    ( 11, 'PA2',          Direction.BIDIR),
    ( 12, 'PA1',          Direction.BIDIR),
    ( 13, 'PA0',          Direction.BIDIR),
    ( 14, 'GND',          Direction.IN),
)


def test_construction_with_refdes_1():
    ic = ATtiny84(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ATtiny84.REFDES_PREFIX == 'U'


def test_footprint():
    assert ATtiny84.FOOTPRINT == 'Package_DIP:DIP-14_W7.62mm'


def test_pin_count():
    ic = ATtiny84(refdes_number=1)
    assert len(ic.pins) == 14


def test_pin_numbers_and_names_match_datasheet():
    ic = ATtiny84(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ATtiny84(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = ATtiny84(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ATtiny84(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ATtiny84(refdes_number=1)) == "ATtiny84(refdes='U1')"
