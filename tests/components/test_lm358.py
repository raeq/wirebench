from components.chips.lm358 import LM358
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'OUT1',  Direction.OUT),
    (2, 'IN1-',  Direction.IN),
    (3, 'IN1+',  Direction.IN),
    (4, 'V_GND', Direction.IN),
    (5, 'IN2+',  Direction.IN),
    (6, 'IN2-',  Direction.IN),
    (7, 'OUT2',  Direction.OUT),
    (8, 'V+',    Direction.IN),
)


def test_construction_with_refdes_1():
    ic = LM358(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM358.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM358.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = LM358(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = LM358(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM358(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM358(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM358(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM358(refdes_number=1)) == "LM358(refdes='U1')"
