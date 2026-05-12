import pytest

from components.chips.concepts.isolated_channel import IsolatedChannel
from framework.errors import PartConfigurationError
from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction


@pytest.fixture
def iso_domain():
    return GroundDomain('isolated_channel_test')


@pytest.fixture
def cell(iso_domain):
    return IsolatedChannel(input_domain=ELECTRICAL, output_domain=iso_domain)


def test_passes_high(cell):
    assert cell(True) is True


def test_passes_low(cell):
    assert cell(False) is False


def test_none_propagates(cell):
    assert cell(None) is None


def test_input_port_is_in_input_domain(cell):
    assert cell.ports['input'].domain is ELECTRICAL


def test_output_port_is_in_output_domain(cell, iso_domain):
    assert cell.ports['output'].domain is iso_domain


def test_input_direction_is_in(cell):
    assert cell.ports['input'].direction is Direction.IN


def test_output_direction_is_out(cell):
    assert cell.ports['output'].direction is Direction.OUT


def test_domain_properties(cell, iso_domain):
    assert cell.input_domain is ELECTRICAL
    assert cell.output_domain is iso_domain


def test_same_domain_on_both_sides_raises():
    """Both ports in one domain means there's no barrier — that's a
    Buffer, not an IsolatedChannel.  The cell must refuse."""
    with pytest.raises(PartConfigurationError, match="distinct"):
        IsolatedChannel(input_domain=ELECTRICAL, output_domain=ELECTRICAL)


def test_repr_includes_both_domain_names(iso_domain):
    cell = IsolatedChannel(input_domain=ELECTRICAL, output_domain=iso_domain)
    r = repr(cell)
    assert ELECTRICAL.name in r
    assert iso_domain.name in r
