import pytest

from components.passives.capacitor import Capacitor
from framework.units import Farads, Microfarads, Nanofarads, Picofarads


def test_construction_with_refdes_1():
    c = Capacitor(100e-9, refdes_number=1)
    assert c.refdes == 'C1'
    assert c.refdes_number == 1


def test_refdes_prefix():
    assert Capacitor.REFDES_PREFIX == 'C'


def test_farads_property_returns_unit_typed_value():
    c = Capacitor(0.01e-6, refdes_number=1)
    assert isinstance(c.farads, Farads)
    assert float(c.farads) == pytest.approx(0.01e-6)


def test_accepts_explicit_unit_input():
    c1 = Capacitor(Microfarads(0.1), refdes_number=1)
    c2 = Capacitor(Nanofarads(100),  refdes_number=2)
    c3 = Capacitor(Picofarads(100),  refdes_number=3)
    assert float(c1.farads) == pytest.approx(100e-9)
    assert float(c2.farads) == pytest.approx(100e-9)
    assert float(c3.farads) == pytest.approx(100e-12)


def test_terminals_are_bidir_analog_wildcards():
    """t1/t2 are BIDIR Analog: same conductor-wildcard treatment as
    Resistor terminals (matches the wire() rules)."""
    from framework.port import Direction
    from framework.signals import Analog
    c = Capacitor(1e-6, refdes_number=1)
    for name in ('t1', 't2'):
        p = c.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True   # see test_terminals_are_mandatory below


def test_call_returns_value_and_skips_input_guard():
    """__call__ is a documentation/sizing surface: it returns the stored
    value and never touches the ports, so it is allowed to run even
    when the device is wired into a parent (same convention as
    Resistor.__call__)."""
    c = Capacitor(1e-6, refdes_number=1)
    assert float(c()) == pytest.approx(1e-6)


def test_evaluate_is_noop():
    """A voltage-only graph cannot solve the I = C dV/dt term, so the
    capacitor is opaque under evaluate."""
    c = Capacitor(1e-6, refdes_number=1)
    c.evaluate()   # must not raise; must not drive anything.
    assert c.ports['t1'].value is None
    assert c.ports['t2'].value is None


def test_rejects_zero_and_negative():
    with pytest.raises(Exception):
        Capacitor(0, refdes_number=1)
    with pytest.raises(Exception):
        Capacitor(-1e-9, refdes_number=1)


def test_repr_and_str():
    c = Capacitor(1e-6, refdes_number=2)
    assert "C2" in repr(c)
    assert "1e-06" in repr(c)
    assert "F" in str(c)


def test_terminals_are_mandatory():
    """Both Capacitor terminals must be `mandatory=True`. See
    `tests/components/test_resistor.py::test_terminals_are_mandatory`
    for the same regression on Resistor."""
    c = Capacitor(1e-6, refdes_number=1)
    assert c.ports['t1'].mandatory is True
    assert c.ports['t2'].mandatory is True


def test_floating_capacitor_refused_at_circuit_construction():
    from framework.circuit import Circuit
    from framework.errors import UnconnectedPinError

    class _DanglingCapacitor(Circuit):
        def __init__(self) -> None:
            self.c = Capacitor(1e-6, refdes_number=1)
            super().__init__()

    with pytest.raises(UnconnectedPinError, match='Capacitor'):
        _DanglingCapacitor()
