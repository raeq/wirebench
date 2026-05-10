import pytest
from components.chips.concepts.darlington_channel import DarlingtonChannel


def test_below_threshold_output_high():
    # transistor off → pull-up holds output HIGH
    assert DarlingtonChannel()(0.5) is True


def test_at_threshold_output_high():
    # not strictly greater → still off
    assert DarlingtonChannel()(DarlingtonChannel.V_THRESHOLD) is True


def test_above_threshold_output_low():
    # transistor on → output sunk LOW
    assert DarlingtonChannel()(5.0) is False


def test_undriven_input_yields_none():
    cell = DarlingtonChannel()
    cell.evaluate()
    assert cell.ports['out'].value is None
