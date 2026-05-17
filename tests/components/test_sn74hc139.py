from components.chips.sn74hc139 import SN74HC139
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, '1G' , Direction.IN),
    ( 2, '1A' , Direction.IN),
    ( 3, '1B' , Direction.IN),
    ( 4, '1Y0', Direction.OUT),
    ( 5, '1Y1', Direction.OUT),
    ( 6, '1Y2', Direction.OUT),
    ( 7, '1Y3', Direction.OUT),
    ( 8, 'GND', Direction.IN),
    ( 9, '2Y3', Direction.OUT),
    (10, '2Y2', Direction.OUT),
    (11, '2Y1', Direction.OUT),
    (12, '2Y0', Direction.OUT),
    (13, '2B' , Direction.IN),
    (14, '2A' , Direction.IN),
    (15, '2G' , Direction.IN),
    (16, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC139(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC139.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC139.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC139(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC139(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC139(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC139(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC139(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC139(refdes_number=1)) == "SN74HC139(refdes='U1')"
