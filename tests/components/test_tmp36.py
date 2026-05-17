from components.chips.tmp36 import TMP36
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'Vs_plus', Direction.IN),
    (2, 'VOUT',    Direction.OUT),
    (3, 'GND',     Direction.IN),
)


def test_construction_with_refdes_1():
    ic = TMP36(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert TMP36.REFDES_PREFIX == 'U'


def test_footprint():
    assert TMP36.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_pin_count():
    ic = TMP36(refdes_number=1)
    assert len(ic.pins) == 3


def test_pin_numbers_and_names_match_datasheet():
    ic = TMP36(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = TMP36(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = TMP36(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = TMP36(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(TMP36(refdes_number=1)) == "TMP36(refdes='U1')"
