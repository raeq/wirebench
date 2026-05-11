from components.chips.ams1117_33 import AMS1117_33
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'GND',        Direction.IN),
    (2, 'OUTPUT',     Direction.OUT),
    (3, 'INPUT',      Direction.IN),
    (4, 'OUTPUT_TAB', Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = AMS1117_33(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert AMS1117_33.REFDES_PREFIX == 'U'


def test_footprint():
    assert AMS1117_33.FOOTPRINT == 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'


def test_pin_count():
    ic = AMS1117_33(refdes_number=1)
    assert len(ic.pins) == 4


def test_pin_numbers_and_names_match_datasheet():
    ic = AMS1117_33(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = AMS1117_33(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = AMS1117_33(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = AMS1117_33(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(AMS1117_33(refdes_number=1)) == "AMS1117_33(refdes='U1')"
