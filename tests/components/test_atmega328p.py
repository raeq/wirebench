from components.chips.atmega328p import ATmega328P
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'PC6',          Direction.BIDIR),
    (  2, 'PD0',          Direction.BIDIR),
    (  3, 'PD1',          Direction.BIDIR),
    (  4, 'PD2',          Direction.BIDIR),
    (  5, 'PD3',          Direction.BIDIR),
    (  6, 'PD4',          Direction.BIDIR),
    (  7, 'VCC',          Direction.IN),
    (  8, 'GND',        Direction.IN),
    (  9, 'PB6',          Direction.BIDIR),
    ( 10, 'PB7',          Direction.BIDIR),
    ( 11, 'PD5',          Direction.BIDIR),
    ( 12, 'PD6',          Direction.BIDIR),
    ( 13, 'PD7',          Direction.BIDIR),
    ( 14, 'PB0',          Direction.BIDIR),
    ( 15, 'PB1',          Direction.BIDIR),
    ( 16, 'PB2',          Direction.BIDIR),
    ( 17, 'PB3',          Direction.BIDIR),
    ( 18, 'PB4',          Direction.BIDIR),
    ( 19, 'PB5',          Direction.BIDIR),
    ( 20, 'AVCC',         Direction.IN),
    ( 21, 'AREF',         Direction.IN),
    ( 22, 'GND',        Direction.IN),
    ( 23, 'PC0',          Direction.BIDIR),
    ( 24, 'PC1',          Direction.BIDIR),
    ( 25, 'PC2',          Direction.BIDIR),
    ( 26, 'PC3',          Direction.BIDIR),
    ( 27, 'PC4',          Direction.BIDIR),
    ( 28, 'PC5',          Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = ATmega328P(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ATmega328P.REFDES_PREFIX == 'U'


def test_footprint():
    assert ATmega328P.FOOTPRINT == 'Package_DIP:DIP-28_W7.62mm'


def test_pin_count():
    ic = ATmega328P(refdes_number=1)
    assert len(ic.pins) == 28


def test_pin_numbers_and_names_match_datasheet():
    ic = ATmega328P(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ATmega328P(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = ATmega328P(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ATmega328P(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ATmega328P(refdes_number=1)) == "ATmega328P(refdes='U1')"
