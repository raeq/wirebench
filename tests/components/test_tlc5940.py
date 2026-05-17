from components.chips.tlc5940 import TLC5940
from framework.port import Direction


EXPECTED_PINS = (
    (1,  'OUT1',  Direction.OUT),
    (2,  'OUT0',  Direction.OUT),
    (3,  'VPRG',  Direction.IN),
    (4,  'SIN',   Direction.IN),
    (5,  'SCLK',  Direction.IN),
    (6,  'XLAT',  Direction.IN),
    (7,  'BLANK', Direction.IN),
    (8,  'GND',   Direction.IN),
    (9,  'VCC',   Direction.IN),
    (10, 'IREF',  Direction.IN),
    (11, 'DCPRG', Direction.IN),
    (12, 'GSCLK', Direction.IN),
    (13, 'SOUT',  Direction.OUT),
    (14, 'XERR',  Direction.OUT),
    (15, 'OUT15', Direction.OUT),
    (16, 'OUT14', Direction.OUT),
    (17, 'OUT13', Direction.OUT),
    (18, 'OUT12', Direction.OUT),
    (19, 'OUT11', Direction.OUT),
    (20, 'OUT10', Direction.OUT),
    (21, 'OUT9',  Direction.OUT),
    (22, 'OUT8',  Direction.OUT),
    (23, 'OUT7',  Direction.OUT),
    (24, 'OUT6',  Direction.OUT),
    (25, 'OUT5',  Direction.OUT),
    (26, 'OUT4',  Direction.OUT),
    (27, 'OUT3',  Direction.OUT),
    (28, 'OUT2',  Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = TLC5940(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert TLC5940.REFDES_PREFIX == 'U'


def test_footprint():
    assert TLC5940.FOOTPRINT == 'Package_DIP:DIP-28_W7.62mm'


def test_pin_count():
    ic = TLC5940(refdes_number=1)
    assert len(ic.pins) == 28


def test_pin_numbers_and_names_match_datasheet():
    ic = TLC5940(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = TLC5940(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = TLC5940(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = TLC5940(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(TLC5940(refdes_number=1)) == "TLC5940(refdes='U1')"
