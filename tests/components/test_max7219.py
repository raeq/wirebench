from components.chips.max7219 import MAX7219
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'DIN',    Direction.IN),
    ( 2, 'DIG_0',  Direction.OUT),
    ( 3, 'DIG_4',  Direction.OUT),
    ( 4, 'GND',    Direction.IN),
    ( 5, 'DIG_6',  Direction.OUT),
    ( 6, 'DIG_2',  Direction.OUT),
    ( 7, 'DIG_3',  Direction.OUT),
    ( 8, 'DIG_7',  Direction.OUT),
    ( 9, 'GND',    Direction.IN),
    (10, 'DIG_5',  Direction.OUT),
    (11, 'DIG_1',  Direction.OUT),
    (12, 'LOAD',   Direction.IN),
    (13, 'CLK',    Direction.IN),
    (14, 'SEG_A',  Direction.OUT),
    (15, 'SEG_F',  Direction.OUT),
    (16, 'SEG_B',  Direction.OUT),
    (17, 'SEG_G',  Direction.OUT),
    (18, 'ISET',   Direction.IN),
    (19, 'V_POS',     Direction.IN),
    (20, 'SEG_C',  Direction.OUT),
    (21, 'SEG_E',  Direction.OUT),
    (22, 'SEG_DP', Direction.OUT),
    (23, 'SEG_D',  Direction.OUT),
    (24, 'DOUT',   Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = MAX7219(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert MAX7219.REFDES_PREFIX == 'U'


def test_footprint():
    assert MAX7219.FOOTPRINT == 'Package_DIP:DIP-24_W15.24mm'


def test_pin_count():
    ic = MAX7219(refdes_number=1)
    assert len(ic.pins) == 24


def test_pin_numbers_and_names_match_datasheet():
    ic = MAX7219(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = MAX7219(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = MAX7219(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = MAX7219(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(MAX7219(refdes_number=1)) == "MAX7219(refdes='U1')"
