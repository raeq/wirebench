from components.chips.ds1307 import DS1307
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'X1',      Direction.IN),
    (2, 'X2',      Direction.OUT),
    (3, 'VBAT',    Direction.IN),
    (4, 'GND',     Direction.IN),
    (5, 'SDA',     Direction.BIDIR),
    (6, 'SCL',     Direction.BIDIR),
    (7, 'SQW_OUT', Direction.OUT),
    (8, 'VCC',     Direction.IN),
)


def test_construction_with_refdes_1():
    ic = DS1307(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert DS1307.REFDES_PREFIX == 'U'


def test_footprint():
    assert DS1307.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = DS1307(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = DS1307(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = DS1307(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = DS1307(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = DS1307(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(DS1307(refdes_number=1)) == "DS1307(refdes='U1')"
