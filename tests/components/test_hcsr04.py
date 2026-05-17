from components.chips.hcsr04 import HCSR04
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'VCC',  Direction.IN),
    (2, 'TRIG', Direction.IN),
    (3, 'ECHO', Direction.OUT),
    (4, 'GND',  Direction.IN),
)


def test_construction_with_refdes_1():
    ic = HCSR04(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert HCSR04.REFDES_PREFIX == 'U'


def test_footprint():
    assert HCSR04.FOOTPRINT == 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'


def test_pin_count():
    ic = HCSR04(refdes_number=1)
    assert len(ic.pins) == 4


def test_pin_numbers_and_names_match_datasheet():
    ic = HCSR04(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = HCSR04(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = HCSR04(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = HCSR04(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(HCSR04(refdes_number=1)) == "HCSR04(refdes='U1')"
