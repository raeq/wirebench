from components.chips.opto_4n25 import OPTO_4N25
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'ANODE',     Direction.IN),
    (2, 'CATHODE',   Direction.IN),
    (4, 'EMITTER',   Direction.OUT),
    (5, 'COLLECTOR', Direction.OUT),
    (6, 'BASE',      Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = OPTO_4N25(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert OPTO_4N25.REFDES_PREFIX == 'U'


def test_footprint():
    assert OPTO_4N25.FOOTPRINT == 'Package_DIP:DIP-6_W7.62mm'


def test_pin_count():
    ic = OPTO_4N25(refdes_number=1)
    assert len(ic.pins) == 5


def test_pin_numbers_and_names_match_datasheet():
    ic = OPTO_4N25(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = OPTO_4N25(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = OPTO_4N25(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_nc_pin_omitted():
    ic = OPTO_4N25(refdes_number=1)
    numbers = {p.id.number for p in ic.pins}
    assert 3 not in numbers


def test_call_is_noop():
    ic = OPTO_4N25(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(OPTO_4N25(refdes_number=1)) == "OPTO_4N25(refdes='U1')"
