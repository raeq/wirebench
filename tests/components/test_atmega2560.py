from components.chips.atmega2560 import ATmega2560
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'PG5',          Direction.BIDIR),
    (  2, 'PE0',          Direction.BIDIR),
    (  3, 'PE1',          Direction.BIDIR),
    (  4, 'PE2',          Direction.BIDIR),
    (  5, 'PE3',          Direction.BIDIR),
    (  6, 'PE4',          Direction.BIDIR),
    (  7, 'PE5',          Direction.BIDIR),
    (  8, 'PE6',          Direction.BIDIR),
    (  9, 'PE7',          Direction.BIDIR),
    ( 10, 'VCC',        Direction.IN),
    ( 11, 'GND',        Direction.IN),
    ( 12, 'PH0',          Direction.BIDIR),
    ( 13, 'PH1',          Direction.BIDIR),
    ( 14, 'PH2',          Direction.BIDIR),
    ( 15, 'PH3',          Direction.BIDIR),
    ( 16, 'PH4',          Direction.BIDIR),
    ( 17, 'PH5',          Direction.BIDIR),
    ( 18, 'PH6',          Direction.BIDIR),
    ( 19, 'PB0',          Direction.BIDIR),
    ( 20, 'PB1',          Direction.BIDIR),
    ( 21, 'PB2',          Direction.BIDIR),
    ( 22, 'PB3',          Direction.BIDIR),
    ( 23, 'PB4',          Direction.BIDIR),
    ( 24, 'PB5',          Direction.BIDIR),
    ( 25, 'PB6',          Direction.BIDIR),
    ( 26, 'PB7',          Direction.BIDIR),
    ( 27, 'PH7',          Direction.BIDIR),
    ( 28, 'PG3',          Direction.BIDIR),
    ( 29, 'PG4',          Direction.BIDIR),
    ( 30, 'RESET',        Direction.IN),
    ( 31, 'VCC',        Direction.IN),
    ( 32, 'GND',        Direction.IN),
    ( 33, 'XTAL2',        Direction.BIDIR),
    ( 34, 'XTAL1',        Direction.BIDIR),
    ( 35, 'PL0',          Direction.BIDIR),
    ( 36, 'PL1',          Direction.BIDIR),
    ( 37, 'PL2',          Direction.BIDIR),
    ( 38, 'PL3',          Direction.BIDIR),
    ( 39, 'PL4',          Direction.BIDIR),
    ( 40, 'PL5',          Direction.BIDIR),
    ( 41, 'PL6',          Direction.BIDIR),
    ( 42, 'PL7',          Direction.BIDIR),
    ( 43, 'PD0',          Direction.BIDIR),
    ( 44, 'PD1',          Direction.BIDIR),
    ( 45, 'PD2',          Direction.BIDIR),
    ( 46, 'PD3',          Direction.BIDIR),
    ( 47, 'PD4',          Direction.BIDIR),
    ( 48, 'PD5',          Direction.BIDIR),
    ( 49, 'PD6',          Direction.BIDIR),
    ( 50, 'PD7',          Direction.BIDIR),
    ( 51, 'PG0',          Direction.BIDIR),
    ( 52, 'PG1',          Direction.BIDIR),
    ( 53, 'PC0',          Direction.BIDIR),
    ( 54, 'PC1',          Direction.BIDIR),
    ( 55, 'PC2',          Direction.BIDIR),
    ( 56, 'PC3',          Direction.BIDIR),
    ( 57, 'PC4',          Direction.BIDIR),
    ( 58, 'PC5',          Direction.BIDIR),
    ( 59, 'PC6',          Direction.BIDIR),
    ( 60, 'PC7',          Direction.BIDIR),
    ( 61, 'VCC',        Direction.IN),
    ( 62, 'GND',        Direction.IN),
    ( 63, 'PJ0',          Direction.BIDIR),
    ( 64, 'PJ1',          Direction.BIDIR),
    ( 65, 'PJ2',          Direction.BIDIR),
    ( 66, 'PJ3',          Direction.BIDIR),
    ( 67, 'PJ4',          Direction.BIDIR),
    ( 68, 'PJ5',          Direction.BIDIR),
    ( 69, 'PJ6',          Direction.BIDIR),
    ( 70, 'PG2',          Direction.BIDIR),
    ( 71, 'PA7',          Direction.BIDIR),
    ( 72, 'PA6',          Direction.BIDIR),
    ( 73, 'PA5',          Direction.BIDIR),
    ( 74, 'PA4',          Direction.BIDIR),
    ( 75, 'PA3',          Direction.BIDIR),
    ( 76, 'PA2',          Direction.BIDIR),
    ( 77, 'PA1',          Direction.BIDIR),
    ( 78, 'PA0',          Direction.BIDIR),
    ( 79, 'PJ7',          Direction.BIDIR),
    ( 80, 'VCC',        Direction.IN),
    ( 81, 'GND',        Direction.IN),
    ( 82, 'PK7',          Direction.BIDIR),
    ( 83, 'PK6',          Direction.BIDIR),
    ( 84, 'PK5',          Direction.BIDIR),
    ( 85, 'PK4',          Direction.BIDIR),
    ( 86, 'PK3',          Direction.BIDIR),
    ( 87, 'PK2',          Direction.BIDIR),
    ( 88, 'PK1',          Direction.BIDIR),
    ( 89, 'PK0',          Direction.BIDIR),
    ( 90, 'PF7',          Direction.BIDIR),
    ( 91, 'PF6',          Direction.BIDIR),
    ( 92, 'PF5',          Direction.BIDIR),
    ( 93, 'PF4',          Direction.BIDIR),
    ( 94, 'PF3',          Direction.BIDIR),
    ( 95, 'PF2',          Direction.BIDIR),
    ( 96, 'PF1',          Direction.BIDIR),
    ( 97, 'PF0',          Direction.BIDIR),
    ( 98, 'AREF',         Direction.IN),
    ( 99, 'GND',        Direction.IN),
    (100, 'AVCC',         Direction.IN),
)


def test_construction_with_refdes_1():
    ic = ATmega2560(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ATmega2560.REFDES_PREFIX == 'U'


def test_footprint():
    assert ATmega2560.FOOTPRINT == 'Package_QFP:TQFP-100_14x14mm_P0.5mm'


def test_pin_count():
    ic = ATmega2560(refdes_number=1)
    assert len(ic.pins) == 100


def test_pin_numbers_and_names_match_datasheet():
    ic = ATmega2560(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ATmega2560(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = ATmega2560(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ATmega2560(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ATmega2560(refdes_number=1)) == "ATmega2560(refdes='U1')"
