from components.chips.moc3021 import MOC3021
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'ANODE',   Direction.IN),
    (2, 'CATHODE', Direction.IN),
    (4, 'MT1',     Direction.OUT),
    (6, 'MT2',     Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = MOC3021(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert MOC3021.REFDES_PREFIX == 'U'


def test_footprint():
    assert MOC3021.FOOTPRINT == 'Package_DIP:DIP-6_W7.62mm'


def test_pin_count():
    ic = MOC3021(refdes_number=1)
    assert len(ic.pins) == 4


def test_pin_numbers_and_names_match_datasheet():
    ic = MOC3021(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = MOC3021(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = MOC3021(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_nc_and_substrate_pins_omitted():
    ic = MOC3021(refdes_number=1)
    numbers = {p.id.number for p in ic.pins}
    assert 3 not in numbers
    assert 5 not in numbers


def test_call_is_noop():
    ic = MOC3021(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(MOC3021(refdes_number=1)) == "MOC3021(refdes='U1')"
