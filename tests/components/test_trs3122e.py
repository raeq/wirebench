import pytest

from components.chips.trs3122e import TRS3122E
from components.chips.concepts.buffer import Buffer
from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction
from framework.signals import Analog, Digital


EXPECTED_PINS = (
    ( 1, 'VL',      Direction.IN,  Analog),
    ( 2, 'VCC',     Direction.IN,  Analog),
    ( 3, 'GND',     Direction.IN,  Analog),
    ( 4, 'C1+',     Direction.IN,  Analog),
    ( 5, 'V+',      Direction.OUT, Analog),
    ( 6, 'C1-',     Direction.IN,  Analog),
    ( 7, 'C2+',     Direction.IN,  Analog),
    ( 8, 'C2-',     Direction.IN,  Analog),
    ( 9, 'V-',      Direction.OUT, Analog),
    (10, 'TIN2',    Direction.IN,  Digital),
    (11, 'ROUT2',   Direction.OUT, Digital),
    (12, 'TOUT2',   Direction.OUT, Digital),
    (13, 'RIN2',    Direction.IN,  Digital),
    (14, 'GND',     Direction.IN,  Analog),
    (15, 'TIN1',    Direction.IN,  Digital),
    (16, 'ROUT1',   Direction.OUT, Digital),
    (17, 'RIN1',    Direction.IN,  Digital),
    (18, 'TOUT1',   Direction.OUT, Digital),
    (19, 'SHDN',    Direction.IN,  Digital),
    (20, 'INVALID', Direction.OUT, Digital),
)


def test_construction_with_refdes_2():
    ic = TRS3122E(refdes_number=2)
    assert ic.refdes == 'U2'


def test_refdes_prefix():
    assert TRS3122E.REFDES_PREFIX == 'U'


def test_footprint():
    assert TRS3122E.FOOTPRINT == 'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'


def test_pin_count():
    ic = TRS3122E(refdes_number=1)
    assert len(ic.pins) == 20


def test_pin_numbers_and_names_match_datasheet():
    ic = TRS3122E(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, *_ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = TRS3122E(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction, _ in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_all_pins_in_single_domain():
    """TRS3122E is not an isolator — every pin must sit in the same
    ground domain the chip was constructed with."""
    iso = GroundDomain('trs3122e_test')
    ic = TRS3122E(domain=iso, refdes_number=1)
    for p in ic.pins:
        assert p.external.domain is iso


def test_default_domain_is_electrical():
    ic = TRS3122E(refdes_number=1)
    for p in ic.pins:
        assert p.external.domain is ELECTRICAL


def test_call_passes_tin1_to_tout1():
    ic = TRS3122E(refdes_number=1)
    out = ic(tin1=True)
    assert out['TOUT1'] is True


def test_call_passes_tin2_to_tout2():
    ic = TRS3122E(refdes_number=1)
    out = ic(tin2=False)
    assert out['TOUT2'] is False


def test_call_passes_rin1_to_rout1():
    ic = TRS3122E(refdes_number=1)
    out = ic(rin1=True)
    assert out['ROUT1'] is True


def test_call_passes_rin2_to_rout2():
    ic = TRS3122E(refdes_number=1)
    out = ic(rin2=False)
    assert out['ROUT2'] is False


def test_call_undriven_inputs_propagate_none():
    ic = TRS3122E(refdes_number=1)
    out = ic()
    assert out == {'TOUT1': None, 'TOUT2': None,
                   'ROUT1': None, 'ROUT2': None}


def test_call_drives_all_four_channels_independently():
    ic = TRS3122E(refdes_number=1)
    out = ic(tin1=True, tin2=False, rin1=False, rin2=True)
    assert out['TOUT1'] is True
    assert out['TOUT2'] is False
    assert out['ROUT1'] is False
    assert out['ROUT2'] is True


def test_has_four_internal_buffer_cells():
    ic = TRS3122E(refdes_number=1)
    buffers = [fn for fn in ic._factor_nodes if isinstance(fn, Buffer)]
    assert len(buffers) == 4


def test_repr():
    assert repr(TRS3122E(refdes_number=2)) == "TRS3122E(refdes='U2')"
