import pytest

from components.chips.concepts.buffer import Buffer
from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction


def test_buffer_passes_high():
    assert Buffer()(True) is True


def test_buffer_passes_low():
    assert Buffer()(False) is False


def test_none_propagates():
    assert Buffer()(None) is None


def test_ports_share_default_domain():
    b = Buffer()
    assert b.ports['input'].domain is ELECTRICAL
    assert b.ports['output'].domain is ELECTRICAL


def test_custom_domain_is_used_on_both_ports():
    d = GroundDomain('buffer_test_domain')
    b = Buffer(domain=d)
    assert b.ports['input'].domain is d
    assert b.ports['output'].domain is d


def test_input_direction_is_in():
    assert Buffer().ports['input'].direction is Direction.IN


def test_output_direction_is_out():
    assert Buffer().ports['output'].direction is Direction.OUT


def test_repr_undriven():
    assert repr(Buffer()) == "Buffer(output=None)"
