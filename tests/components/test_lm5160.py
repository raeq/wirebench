from components.chips.lm5160 import LM5160
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'RT',   Direction.IN),
    ( 2, 'FB',   Direction.IN),
    ( 3, 'SS',   Direction.IN),
    ( 4, 'AGND', Direction.IN),
    ( 5, 'NC1',  Direction.IN),
    ( 6, 'FPWM', Direction.IN),
    ( 7, 'UVLO', Direction.IN),
    ( 8, 'VCC',  Direction.OUT),
    ( 9, 'SW',   Direction.OUT),
    (10, 'SW',   Direction.OUT),
    (11, 'PGND', Direction.IN),
    (12, 'PGND', Direction.IN),
    (13, 'BST',  Direction.IN),
    (14, 'VIN',  Direction.IN),
    (15, 'VIN',  Direction.IN),
    (16, 'NC2',  Direction.IN),
)


def test_construction_with_refdes_1():
    ic = LM5160(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM5160.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(LM5160(refdes_number=1).pins) == 16


def test_pin_numbers_and_names():
    ic = LM5160(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = LM5160(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_call_is_noop():
    assert LM5160(refdes_number=1)() is None


def test_repr():
    assert repr(LM5160(refdes_number=1)) == "LM5160(refdes='U1')"
