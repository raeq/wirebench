from components.chips.lm5002 import LM5002
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'VCC',  Direction.IN),
    (2, 'RT',   Direction.IN),
    (3, 'SS',   Direction.IN),
    (4, 'FB',   Direction.IN),
    (5, 'COMP', Direction.IN),
    (6, 'ISEN', Direction.IN),
    (7, 'GND',  Direction.IN),
    (8, 'SW',   Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = LM5002(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM5002.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(LM5002(refdes_number=1).pins) == 8


def test_pin_numbers_and_names():
    ic = LM5002(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = LM5002(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = LM5002(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    assert LM5002(refdes_number=1)() is None


def test_repr():
    assert repr(LM5002(refdes_number=1)) == "LM5002(refdes='U1')"
