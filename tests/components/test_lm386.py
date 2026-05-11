from components.chips.lm386 import LM386
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'GAIN',   Direction.BIDIR),
    (2, '-INPUT', Direction.IN),
    (3, '+INPUT', Direction.IN),
    (4, 'GND',    Direction.IN),
    (5, 'VOUT',   Direction.OUT),
    (6, 'VS',     Direction.IN),
    (7, 'BYPASS', Direction.OUT),
    (8, 'GAIN',   Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = LM386(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM386.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM386.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = LM386(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = LM386(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM386(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM386(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM386(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM386(refdes_number=1)) == "LM386(refdes='U1')"
