import pytest

from components.chips.isow7841 import ISOW7841
from components.chips.concepts.isolated_channel import IsolatedChannel
from framework.errors import PartConfigurationError
from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction
from framework.signals import Analog, Digital


# (pin number, name, direction, signal type, 'logic' | 'iso')
EXPECTED_PINS = (
    ( 1, 'VCC1', Direction.IN,  Analog,  'logic'),
    ( 2, 'GND1', Direction.IN,  Analog,  'logic'),
    ( 3, 'INA',  Direction.IN,  Digital, 'logic'),
    ( 4, 'INB',  Direction.IN,  Digital, 'logic'),
    ( 5, 'INC',  Direction.IN,  Digital, 'logic'),
    ( 6, 'OUTD', Direction.OUT, Digital, 'logic'),
    ( 7, 'GND1', Direction.IN,  Analog,  'logic'),
    ( 8, 'EN1',  Direction.IN,  Digital, 'logic'),
    ( 9, 'EN2',  Direction.IN,  Digital, 'iso'),
    (10, 'GND2', Direction.IN,  Analog,  'iso'),
    (11, 'IND',  Direction.IN,  Digital, 'iso'),
    (12, 'OUTC', Direction.OUT, Digital, 'iso'),
    (13, 'OUTB', Direction.OUT, Digital, 'iso'),
    (14, 'OUTA', Direction.OUT, Digital, 'iso'),
    (15, 'GND2', Direction.IN,  Analog,  'iso'),
    (16, 'VISO', Direction.OUT, Analog,  'iso'),
)


@pytest.fixture
def iso_domain():
    return GroundDomain('isow7841_test')


@pytest.fixture
def chip(iso_domain):
    return ISOW7841(refdes_number=1,
                    logic_domain=ELECTRICAL,
                    iso_domain=iso_domain)


def test_construction_with_refdes_1(chip):
    assert chip.refdes == 'U1'


def test_refdes_prefix():
    assert ISOW7841.REFDES_PREFIX == 'U'


def test_footprint():
    assert ISOW7841.FOOTPRINT == 'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm'


def test_pin_count(chip):
    assert len(chip.pins) == 16


def test_pin_numbers_and_names_match_datasheet(chip):
    by_number = {p.id.number: p for p in chip.pins}
    for number, name, *_ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet(chip):
    by_number = {p.id.number: p for p in chip.pins}
    for number, _, direction, *_ in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_pin_domains_match_side(chip, iso_domain):
    """Pins 1-8 in the logic domain, 9-16 in the iso domain — the
    chip's whole purpose is to straddle that boundary."""
    by_number = {p.id.number: p for p in chip.pins}
    for number, _, _, _, side in EXPECTED_PINS:
        expected_domain = ELECTRICAL if side == 'logic' else iso_domain
        assert by_number[number].external.domain is expected_domain
        assert by_number[number].internal.domain is expected_domain


def test_ports_keyed_by_pin_name(chip):
    for _, name, *_ in EXPECTED_PINS:
        assert name in chip.ports


def test_construction_rejects_identical_domains():
    """Logic and iso must be distinct GroundDomain instances —
    otherwise the chip's whole reason for existing is meaningless."""
    with pytest.raises(PartConfigurationError, match="distinct"):
        ISOW7841(refdes_number=1,
                 logic_domain=ELECTRICAL,
                 iso_domain=ELECTRICAL)


def test_has_four_isolated_channels(chip):
    assert set(chip.channels.keys()) == {'A', 'B', 'C', 'D'}
    for cell in chip.channels.values():
        assert isinstance(cell, IsolatedChannel)


def test_forward_channels_go_logic_to_iso(chip, iso_domain):
    for label in ('A', 'B', 'C'):
        assert chip.channels[label].input_domain is ELECTRICAL
        assert chip.channels[label].output_domain is iso_domain


def test_reverse_channel_goes_iso_to_logic(chip, iso_domain):
    assert chip.channels['D'].input_domain is iso_domain
    assert chip.channels['D'].output_domain is ELECTRICAL


def test_call_forwards_channel_a(chip):
    out = chip(ina=True)
    assert out['OUTA'] is True


def test_call_forwards_channel_b(chip):
    out = chip(inb=False)
    assert out['OUTB'] is False


def test_call_forwards_channel_c(chip):
    out = chip(inc=True)
    assert out['OUTC'] is True


def test_call_reverse_channel_d(chip):
    out = chip(ind=True)
    assert out['OUTD'] is True


def test_call_undriven_inputs_propagate_none(chip):
    out = chip()
    assert out == {'OUTA': None, 'OUTB': None, 'OUTC': None, 'OUTD': None}


def test_call_drives_all_four_channels_independently(chip):
    out = chip(ina=True, inb=False, inc=True, ind=False)
    assert out['OUTA'] is True
    assert out['OUTB'] is False
    assert out['OUTC'] is True
    assert out['OUTD'] is False


def test_domain_properties(chip, iso_domain):
    assert chip.logic_domain is ELECTRICAL
    assert chip.iso_domain is iso_domain


def test_repr(chip, iso_domain):
    r = repr(chip)
    assert "ISOW7841" in r
    assert "U1" in r
    assert iso_domain.name in r
