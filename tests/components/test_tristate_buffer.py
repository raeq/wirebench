import pytest
from components.tristate_buffer import TriStateBuffer


def test_passes_input_when_oe_high():
    buf = TriStateBuffer()
    assert buf(a=True,  oe=True) is True
    assert buf(a=False, oe=True) is False


def test_high_z_when_oe_low():
    buf = TriStateBuffer()
    assert buf(a=True,  oe=False) is None
    assert buf(a=False, oe=False) is None


def test_high_z_when_oe_undriven():
    buf = TriStateBuffer()
    buf.ports['a'].drive(True)
    buf.evaluate()
    assert buf.ports['y'].value is None


def test_repr():
    buf = TriStateBuffer()
    assert repr(buf) == "TriStateBuffer(y=None)"
