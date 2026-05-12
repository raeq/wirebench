import pytest

from components.passives.inductor import Inductor
from framework.units import Henries, Millihenries, Microhenries, Nanohenries


def test_construction_with_refdes_1():
    l = Inductor(100e-6, refdes_number=1)
    assert l.refdes == 'L1'
    assert l.refdes_number == 1


def test_refdes_prefix():
    assert Inductor.REFDES_PREFIX == 'L'


def test_henries_property_returns_unit_typed_value():
    l = Inductor(47e-6, refdes_number=1)
    assert isinstance(l.henries, Henries)
    assert float(l.henries) == pytest.approx(47e-6)


def test_accepts_explicit_unit_input():
    l1 = Inductor(Millihenries(10), refdes_number=1)
    l2 = Inductor(Microhenries(47), refdes_number=2)
    l3 = Inductor(Nanohenries(100), refdes_number=3)
    assert float(l1.henries) == pytest.approx(10e-3)
    assert float(l2.henries) == pytest.approx(47e-6)
    assert float(l3.henries) == pytest.approx(100e-9)


def test_terminals_are_bidir_analog_wildcards():
    """t1/t2 are BIDIR Analog — same conductor-wildcard treatment as
    Resistor and Capacitor terminals."""
    from framework.port import Direction
    from framework.signals import Analog
    l = Inductor(1e-3, refdes_number=1)
    for name in ('t1', 't2'):
        p = l.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is False


def test_call_returns_value_and_skips_input_guard():
    """__call__ is a documentation/sizing surface: returns the stored
    value and never touches the ports.  Allowed to run when wired."""
    l = Inductor(1e-3, refdes_number=1)
    assert float(l()) == pytest.approx(1e-3)


def test_evaluate_is_noop():
    """A voltage-only graph cannot solve the V = L dI/dt term, so the
    inductor is opaque under evaluate."""
    l = Inductor(1e-3, refdes_number=1)
    l.evaluate()
    assert l.ports['t1'].value is None
    assert l.ports['t2'].value is None


def test_rejects_zero_and_negative():
    with pytest.raises(Exception):
        Inductor(0, refdes_number=1)
    with pytest.raises(Exception):
        Inductor(-1e-6, refdes_number=1)


def test_repr_and_str():
    l = Inductor(1e-3, refdes_number=2)
    assert "L2" in repr(l)
    assert "0.001" in repr(l)
    assert "H" in str(l)
