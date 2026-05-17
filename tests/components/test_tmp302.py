from components.chips.tmp302 import TMP302
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'TripSet0', Direction.IN),
    (2, 'GND',      Direction.IN),
    (3, 'OUT',      Direction.OUT),
    (4, 'HysSet',   Direction.IN),
    (5, 'VS',       Direction.IN),
    (6, 'TripSet1', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = TMP302(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert TMP302.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(TMP302(refdes_number=1).pins) == 6


def test_pin_numbers_and_names():
    ic = TMP302(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = TMP302(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_call_is_noop():
    assert TMP302(refdes_number=1)() is None


def test_repr():
    assert repr(TMP302(refdes_number=1)) == "TMP302(refdes='U1')"
