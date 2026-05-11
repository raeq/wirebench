from components.chips.sn74hc74 import SN74HC74
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, '1CLR'  , Direction.IN),
    ( 2, '1D'    , Direction.IN),
    ( 3, '1CLK'  , Direction.IN),
    ( 4, '1PRE'  , Direction.IN),
    ( 5, '1Q'    , Direction.OUT),
    ( 6, '1Q_BAR', Direction.OUT),
    ( 7, 'GND'   , Direction.IN),
    ( 8, '2Q_BAR', Direction.OUT),
    ( 9, '2Q'    , Direction.OUT),
    (10, '2PRE'  , Direction.IN),
    (11, '2CLK'  , Direction.IN),
    (12, '2D'    , Direction.IN),
    (13, '2CLR'  , Direction.IN),
    (14, 'VCC'   , Direction.IN),
)


def test_construction_with_refdes_1():
    ic = SN74HC74(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert SN74HC74.REFDES_PREFIX == 'U'


def test_footprint():
    assert SN74HC74.FOOTPRINT == 'Package_DIP:DIP-14_W7.62mm'


def test_pin_count():
    ic = SN74HC74(refdes_number=1)
    assert len(ic.pins) == 14


def test_pin_numbers_and_names_match_datasheet():
    ic = SN74HC74(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = SN74HC74(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = SN74HC74(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = SN74HC74(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(SN74HC74(refdes_number=1)) == "SN74HC74(refdes='U1')"
