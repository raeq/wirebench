from components.chips.tps2660 import TPS2660
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'SETI',  Direction.IN),
    ( 2, 'IMON',  Direction.OUT),
    ( 3, 'OV',    Direction.IN),
    ( 4, 'UV',    Direction.IN),
    ( 5, 'dVdT',  Direction.IN),
    ( 6, 'EN',    Direction.IN),
    ( 7, 'FLT_B', Direction.OUT),
    ( 8, 'GND',   Direction.IN),
    ( 9, 'OUT',   Direction.OUT),
    (10, 'IN',    Direction.IN),
)


def test_construction_with_refdes_1():
    ic = TPS2660(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert TPS2660.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(TPS2660(refdes_number=1).pins) == 10


def test_pin_numbers_and_names():
    ic = TPS2660(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = TPS2660(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = TPS2660(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    assert TPS2660(refdes_number=1)() is None


def test_repr():
    assert repr(TPS2660(refdes_number=1)) == "TPS2660(refdes='U1')"
