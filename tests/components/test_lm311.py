from components.chips.lm311 import LM311
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'EMIT_OUT', Direction.OUT),
    (2, 'IN_POS',      Direction.IN),
    (3, 'IN_NEG',      Direction.IN),
    (4, 'VCC_NEG',     Direction.IN),
    (5, 'BALANCE',  Direction.IN),
    (6, 'BAL_STRB', Direction.IN),
    (7, 'COL_OUT',  Direction.OUT),
    (8, 'VCC_POS',     Direction.IN),
)


def test_construction_with_refdes_1():
    ic = LM311(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM311.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM311.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = LM311(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = LM311(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM311(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM311(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = LM311(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM311(refdes_number=1)) == "LM311(refdes='U1')"
