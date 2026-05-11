from components.chips.lm7812 import LM7812
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'INPUT',  Direction.IN),
    (2, 'GND',    Direction.IN),
    (3, 'OUTPUT', Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = LM7812(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM7812.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM7812.FOOTPRINT == 'Package_TO_SOT_THT:TO-220-3_Vertical'


def test_pin_count():
    ic = LM7812(refdes_number=1)
    assert len(ic.pins) == 3


def test_pin_numbers_and_names_match_datasheet():
    ic = LM7812(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM7812(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM7812(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM7812(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM7812(refdes_number=1)) == "LM7812(refdes='U1')"
