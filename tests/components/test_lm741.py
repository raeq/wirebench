from components.chips.lm741 import LM741
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'OFFSET_N1', Direction.IN),
    (2, 'IN-',       Direction.IN),
    (3, 'IN+',       Direction.IN),
    (4, 'V-',        Direction.IN),
    (5, 'OFFSET_N2', Direction.IN),
    (6, 'OUT',       Direction.OUT),
    (7, 'V+',        Direction.IN),
)


def test_construction_with_refdes_1():
    ic = LM741(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert LM741.REFDES_PREFIX == 'U'


def test_footprint():
    assert LM741.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = LM741(refdes_number=1)
    assert len(ic.pins) == 7


def test_pin_numbers_and_names_match_datasheet():
    ic = LM741(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = LM741(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = LM741(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_nc_pin_8_omitted():
    ic = LM741(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    assert 8 not in by_number


def test_call_is_noop():
    ic = LM741(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(LM741(refdes_number=1)) == "LM741(refdes='U1')"
