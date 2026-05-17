from components.chips.sn74ahc1g14 import SN74AHC1G14
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'A',   Direction.IN),
    (2, 'GND', Direction.IN),
    (3, 'Y',   Direction.OUT),
    (4, 'NC',  Direction.IN),
    (5, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74AHC1G14(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74AHC1G14.REFDES_PREFIX == 'U'


def test_pin_count():
    assert len(SN74AHC1G14(refdes_number=1).pins) == 5


def test_pin_numbers_and_names():
    ic = SN74AHC1G14(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions():
    ic = SN74AHC1G14(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_call_is_noop():
    assert SN74AHC1G14(refdes_number=1)() is None


def test_repr():
    assert repr(SN74AHC1G14(refdes_number=1)) == "SN74AHC1G14(refdes='U1')"
