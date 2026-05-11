from components.chips.tlv3401 import TLV3401
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'OUT', Direction.OUT),
    (2, 'GND', Direction.IN),
    (3, 'IN+', Direction.IN),
    (4, 'IN-', Direction.IN),
    (5, 'VCC', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = TLV3401(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert TLV3401.REFDES_PREFIX == 'U'


def test_footprint():
    assert TLV3401.FOOTPRINT == 'Package_TO_SOT_SMD:SOT-23-5'


def test_pin_count():
    ic = TLV3401(refdes_number=1)
    assert len(ic.pins) == 5


def test_pin_numbers_and_names_match_datasheet():
    ic = TLV3401(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = TLV3401(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = TLV3401(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = TLV3401(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(TLV3401(refdes_number=1)) == "TLV3401(refdes='U1')"
