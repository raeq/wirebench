from components.chips.atmega32u4 import ATmega32U4
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'PE6',          Direction.BIDIR),
    (  2, 'UVCC',         Direction.IN),
    (  3, 'D_NEG',           Direction.BIDIR),
    (  4, 'D_POS',           Direction.BIDIR),
    (  5, 'UGND',         Direction.IN),
    (  6, 'UCAP',         Direction.IN),
    (  7, 'VBUS',         Direction.IN),
    (  8, 'PB0',          Direction.BIDIR),
    (  9, 'PB1',          Direction.BIDIR),
    ( 10, 'PB2',          Direction.BIDIR),
    ( 11, 'PB3',          Direction.BIDIR),
    ( 12, 'PB7',          Direction.BIDIR),
    ( 13, 'RESET',        Direction.IN),
    ( 14, 'VCC_1',        Direction.IN),
    ( 15, 'GND_1',        Direction.IN),
    ( 16, 'XTAL2',        Direction.BIDIR),
    ( 17, 'XTAL1',        Direction.BIDIR),
    ( 18, 'PD0',          Direction.BIDIR),
    ( 19, 'PD1',          Direction.BIDIR),
    ( 20, 'PD2',          Direction.BIDIR),
    ( 21, 'PD3',          Direction.BIDIR),
    ( 22, 'PD5',          Direction.BIDIR),
    ( 23, 'GND_2',        Direction.IN),
    ( 24, 'VCC_2',        Direction.IN),
    ( 25, 'PD4',          Direction.BIDIR),
    ( 26, 'PD6',          Direction.BIDIR),
    ( 27, 'PD7',          Direction.BIDIR),
    ( 28, 'PB4',          Direction.BIDIR),
    ( 29, 'PB5',          Direction.BIDIR),
    ( 30, 'PB6',          Direction.BIDIR),
    ( 31, 'PC6',          Direction.BIDIR),
    ( 32, 'PC7',          Direction.BIDIR),
    ( 33, 'PE2',          Direction.BIDIR),
    ( 34, 'VCC_3',        Direction.IN),
    ( 35, 'GND_3',        Direction.IN),
    ( 36, 'PF7',          Direction.BIDIR),
    ( 37, 'PF6',          Direction.BIDIR),
    ( 38, 'PF5',          Direction.BIDIR),
    ( 39, 'PF4',          Direction.BIDIR),
    ( 40, 'PF1',          Direction.BIDIR),
    ( 41, 'PF0',          Direction.BIDIR),
    ( 42, 'AREF',         Direction.IN),
    ( 43, 'GND_4',        Direction.IN),
    ( 44, 'AVCC',         Direction.IN),
)


def test_construction_with_refdes_1():
    ic = ATmega32U4(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ATmega32U4.REFDES_PREFIX == 'U'


def test_footprint():
    assert ATmega32U4.FOOTPRINT == 'Package_QFP:TQFP-44_10x10mm_P0.8mm'


def test_pin_count():
    ic = ATmega32U4(refdes_number=1)
    assert len(ic.pins) == 44


def test_pin_numbers_and_names_match_datasheet():
    ic = ATmega32U4(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ATmega32U4(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = ATmega32U4(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ATmega32U4(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ATmega32U4(refdes_number=1)) == "ATmega32U4(refdes='U1')"
