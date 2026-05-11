from components.chips.opto_tlp521 import OPTO_TLP521
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'ANODE',     Direction.IN),
    (2, 'CATHODE',   Direction.IN),
    (3, 'EMITTER',   Direction.OUT),
    (4, 'COLLECTOR', Direction.OUT),
)


def test_construction_with_refdes_1():
    ic = OPTO_TLP521(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert OPTO_TLP521.REFDES_PREFIX == 'U'


def test_footprint():
    assert OPTO_TLP521.FOOTPRINT == 'Package_DIP:DIP-4_W7.62mm'


def test_pin_count():
    ic = OPTO_TLP521(refdes_number=1)
    assert len(ic.pins) == 4


def test_pin_numbers_and_names_match_datasheet():
    ic = OPTO_TLP521(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = OPTO_TLP521(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = OPTO_TLP521(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = OPTO_TLP521(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(OPTO_TLP521(refdes_number=1)) == "OPTO_TLP521(refdes='U1')"
