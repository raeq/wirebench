from components.chips.attiny85 import ATtiny85
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'PB5',          Direction.BIDIR),
    (  2, 'PB3',          Direction.BIDIR),
    (  3, 'PB4',          Direction.BIDIR),
    (  4, 'GND',          Direction.IN),
    (  5, 'PB0',          Direction.BIDIR),
    (  6, 'PB1',          Direction.BIDIR),
    (  7, 'PB2',          Direction.BIDIR),
    (  8, 'VCC',          Direction.IN),
)


def test_construction_with_refdes_1():
    ic = ATtiny85(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ATtiny85.REFDES_PREFIX == 'U'


def test_footprint():
    assert ATtiny85.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = ATtiny85(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = ATtiny85(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ATtiny85(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = ATtiny85(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ATtiny85(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ATtiny85(refdes_number=1)) == "ATtiny85(refdes='U1')"
