from components.chips.ne555 import NE555
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'GND',   Direction.IN),
    (2, 'TRIG',  Direction.IN),
    (3, 'OUT',   Direction.OUT),
    (4, 'RESET', Direction.IN),
    (5, 'CONT',  Direction.BIDIR),
    (6, 'THRES', Direction.IN),
    (7, 'DISCH', Direction.OUT),
    (8, 'VCC',   Direction.IN),
)


def test_construction_with_refdes_1():
    ic = NE555(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert NE555.REFDES_PREFIX == 'U'


def test_footprint():
    assert NE555.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = NE555(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = NE555(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = NE555(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = NE555(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = NE555(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(NE555(refdes_number=1)) == "NE555(refdes='U1')"
