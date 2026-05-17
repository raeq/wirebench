from components.chips.sn74hc595 import SN74HC595
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'QB'      , Direction.OUT),
    ( 2, 'QC'      , Direction.OUT),
    ( 3, 'QD'      , Direction.OUT),
    ( 4, 'QE'      , Direction.OUT),
    ( 5, 'QF'      , Direction.OUT),
    ( 6, 'QG'      , Direction.OUT),
    ( 7, 'QH'      , Direction.OUT),
    ( 8, 'GND'     , Direction.IN),
    ( 9, 'QH_PRIME', Direction.OUT),
    (10, 'SRCLR'   , Direction.IN),
    (11, 'SRCLK'   , Direction.IN),
    (12, 'RCLK'    , Direction.IN),
    (13, 'OE'      , Direction.IN),
    (14, 'SER'     , Direction.IN),
    (15, 'QA'      , Direction.OUT),
    (16, 'VCC'     , Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC595(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC595.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC595.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = SN74HC595(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC595(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC595(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC595(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC595(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC595(refdes_number=1)) == "SN74HC595(refdes='U1')"
